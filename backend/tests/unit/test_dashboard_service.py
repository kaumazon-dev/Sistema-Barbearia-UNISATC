"""Service do dashboard, sem banco e sem subir o Flask."""

from collections import namedtuple
from datetime import date, datetime, timezone
from decimal import Decimal

from app.core.fuso import FUSO_BARBEARIA
from app.services import dashboard_service
from app.services.dashboard_service import DashboardService

LinhaRanking = namedtuple("LinhaRanking", "servico_id nome quantidade receita")


class RepositorioFalso:
    """Devolve linhas prontas e guarda os argumentos de cada chamada."""

    def __init__(self, linhas=()):
        self.linhas = list(linhas)
        self.chamadas = []

    def _registrar(self, nome, *args):
        self.chamadas.append((nome, args))
        return self.linhas

    def contar_atendimentos(self, *args):
        return self._registrar("contar_atendimentos", *args)

    def somar_faturamento(self, *args):
        return self._registrar("somar_faturamento", *args)

    def ranking_servicos(self, *args):
        return self._registrar("ranking_servicos", *args)

    def contar_por_status(self, *args):
        return self._registrar("contar_por_status", *args)


def meia_noite(ano, mes, dia):
    # date_trunc sobre timestamp sem fuso volta como datetime ingenuo.
    return datetime(ano, mes, dia)


# --- series (RF28, RF29) ---------------------------------------------------------


def test_semana_preenche_com_zero_os_periodos_sem_movimento():
    repositorio = RepositorioFalso([(meia_noite(2026, 10, 12), 5)])

    serie = DashboardService(repositorio).atendimentos(
        "semana", date(2026, 10, 1), date(2026, 10, 20)
    )

    # 01/10 e quinta: a primeira semana comeca na segunda 28/09.
    assert serie["labels"] == ["2026-09-28", "2026-10-05", "2026-10-12", "2026-10-19"]
    assert serie["valores"] == [0, 0, 5, 0]


def test_mes_usa_rotulo_ano_mes_e_atravessa_virada_de_ano():
    repositorio = RepositorioFalso([(meia_noite(2027, 1, 1), Decimal("80.00"))])

    serie = DashboardService(repositorio).faturamento(
        "mes", date(2026, 11, 15), date(2027, 2, 3)
    )

    assert serie["labels"] == ["2026-11", "2026-12", "2027-01", "2027-02"]
    assert serie["valores"] == [Decimal("0"), Decimal("0"), Decimal("80.00"), Decimal("0")]


def test_series_contam_so_concluido_e_traduzem_a_granularidade():
    repositorio = RepositorioFalso()
    service = DashboardService(repositorio)

    service.atendimentos("semana", date(2026, 10, 1), date(2026, 10, 31))
    service.faturamento("mes", date(2026, 10, 1), date(2026, 10, 31))

    (_, args_atendimentos), (_, args_faturamento) = repositorio.chamadas
    assert args_atendimentos[2:] == ("week", "concluido")
    assert args_faturamento[2:] == ("month", "concluido")


def test_ate_e_inclusivo_no_fuso_da_barbearia():
    repositorio = RepositorioFalso()

    DashboardService(repositorio).atendimentos(
        "semana", date(2026, 10, 1), date(2026, 10, 31)
    )

    inicio, fim = repositorio.chamadas[0][1][:2]
    assert inicio == datetime(2026, 10, 1, tzinfo=FUSO_BARBEARIA)
    assert fim == datetime(2026, 11, 1, tzinfo=FUSO_BARBEARIA)


def test_sem_datas_usa_o_mes_atual_ate_hoje(monkeypatch):
    # 01/10 02h em UTC ainda e 30/09 em Brasilia: o mes atual e setembro.
    monkeypatch.setattr(
        dashboard_service, "agora", lambda: datetime(2026, 10, 1, 2, tzinfo=timezone.utc)
    )

    serie = DashboardService(RepositorioFalso()).atendimentos("mes")

    assert (serie["de"], serie["ate"]) == (date(2026, 9, 1), date(2026, 9, 30))
    assert serie["labels"] == ["2026-09"]


# --- ranking (RF30) --------------------------------------------------------------


def test_ranking_devolve_listas_alinhadas_para_o_grafico():
    repositorio = RepositorioFalso(
        [
            LinhaRanking(1, "Corte", 10, Decimal("400.00")),
            LinhaRanking(2, "Barba", 4, Decimal("100.00")),
        ]
    )

    ranking = DashboardService(repositorio).ranking_servicos(
        5, date(2026, 10, 1), date(2026, 10, 31)
    )

    assert ranking["labels"] == ["Corte", "Barba"]
    assert ranking["valores"] == [10, 4]
    assert ranking["receitas"] == [Decimal("400.00"), Decimal("100.00")]
    assert repositorio.chamadas[0][1][2:] == ("concluido", 5)


# --- cancelamento (RF31) ---------------------------------------------------------


def test_taxa_considera_so_concluidos_e_cancelados():
    repositorio = RepositorioFalso([("concluido", 417), ("cancelado", 64)])

    resultado = DashboardService(repositorio).cancelamento(
        date(2026, 8, 1), date(2026, 10, 31)
    )

    assert resultado["taxa"] == Decimal("13.31")
    assert resultado["total"] == 481
    assert resultado["valores"] == [417, 64]
    assert repositorio.chamadas[0][1][2] == ("concluido", "cancelado")


def test_taxa_arredonda_meio_para_cima():
    # 1/8 = 12,5%; 1/16 = 6,25%; 1/32 = 3,125% -> 3,13
    repositorio = RepositorioFalso([("concluido", 31), ("cancelado", 1)])

    resultado = DashboardService(repositorio).cancelamento(
        date(2026, 10, 1), date(2026, 10, 31)
    )

    assert resultado["taxa"] == Decimal("3.13")


def test_sem_desfecho_no_periodo_a_taxa_e_nula():
    resultado = DashboardService(RepositorioFalso()).cancelamento(
        date(2026, 10, 1), date(2026, 10, 31)
    )

    assert resultado["taxa"] is None
    assert resultado["valores"] == [0, 0]


def test_so_cancelados_da_cem_por_cento():
    repositorio = RepositorioFalso([("cancelado", 3)])

    resultado = DashboardService(repositorio).cancelamento(
        date(2026, 10, 1), date(2026, 10, 31)
    )

    assert resultado["taxa"] == Decimal("100.00")
    assert resultado["concluidos"] == 0
