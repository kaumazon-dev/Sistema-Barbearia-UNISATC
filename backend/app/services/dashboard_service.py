from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

from app.core.fuso import FUSO_BARBEARIA, agora, intervalo_do_dia
from app.models.agendamento import STATUS_CANCELADO, STATUS_CONCLUIDO

GRANULARIDADE_SEMANA = "semana"
GRANULARIDADE_MES = "mes"
GRANULARIDADES = (GRANULARIDADE_SEMANA, GRANULARIDADE_MES)

# Termo do date_trunc do Postgres. A traducao fica so aqui.
_UNIDADE_SQL = {GRANULARIDADE_SEMANA: "week", GRANULARIDADE_MES: "month"}
CENTAVO = Decimal("0.01")


class DashboardService:
    """Metricas do dashboard (RF28 a RF31, RN05).

    O repository devolve numeros prontos; aqui so se decide o que entra em cada
    metrica e se organiza a resposta para o Chart.js: labels e valores ja
    alinhados, com zero nos periodos sem movimento.

    Periodo em dias do fuso da barbearia, com "ate" inclusivo. Sem datas, vale
    o mes atual, do dia 1 ate hoje. Produtos em falta (RF32) nao passam por
    aqui: o dashboard usa o ProdutoService.listar_em_falta.
    """

    def __init__(self, repositorio):
        self.repositorio = repositorio

    def atendimentos(self, granularidade, de=None, ate=None):
        """RF28. So conta atendimento concluido."""
        de, ate = self._periodo(de, ate)
        linhas = self.repositorio.contar_atendimentos(
            *self._intervalo(de, ate), _UNIDADE_SQL[granularidade], STATUS_CONCLUIDO
        )
        return self._serie(granularidade, de, ate, linhas, vazio=0)

    def faturamento(self, granularidade, de=None, ate=None):
        """RF29. Soma o preco cobrado dos atendimentos concluidos."""
        de, ate = self._periodo(de, ate)
        linhas = self.repositorio.somar_faturamento(
            *self._intervalo(de, ate), _UNIDADE_SQL[granularidade], STATUS_CONCLUIDO
        )
        return self._serie(granularidade, de, ate, linhas, vazio=Decimal("0"))

    def ranking_servicos(self, limite, de=None, ate=None):
        """RF30. Servicos de atendimentos concluidos, do mais vendido ao menos."""
        de, ate = self._periodo(de, ate)
        linhas = self.repositorio.ranking_servicos(
            *self._intervalo(de, ate), STATUS_CONCLUIDO, limite
        )
        return {
            "de": de,
            "ate": ate,
            "labels": [linha.nome for linha in linhas],
            "valores": [linha.quantidade for linha in linhas],
            "receitas": [linha.receita for linha in linhas],
        }

    def cancelamento(self, de=None, ate=None):
        """RF31. Taxa = cancelados / (concluidos + cancelados).

        Agendado fica de fora: ainda nao teve desfecho, e conta-lo faria a taxa
        mudar sozinha conforme o futuro se resolve.
        """
        de, ate = self._periodo(de, ate)
        contagem = dict(
            self.repositorio.contar_por_status(
                *self._intervalo(de, ate), (STATUS_CONCLUIDO, STATUS_CANCELADO)
            )
        )
        concluidos = contagem.get(STATUS_CONCLUIDO, 0)
        cancelados = contagem.get(STATUS_CANCELADO, 0)
        total = concluidos + cancelados
        # Sem nenhum desfecho no periodo a taxa nao existe; zero seria mentira.
        taxa = (
            None
            if total == 0
            else (Decimal(cancelados * 100) / total).quantize(CENTAVO, ROUND_HALF_UP)
        )
        return {
            "de": de,
            "ate": ate,
            "concluidos": concluidos,
            "cancelados": cancelados,
            "total": total,
            "taxa": taxa,
            "labels": ["Concluídos", "Cancelados"],
            "valores": [concluidos, cancelados],
        }

    @staticmethod
    def _periodo(de, ate):
        if de is None or ate is None:
            hoje = agora().astimezone(FUSO_BARBEARIA).date()
            return hoje.replace(day=1), hoje
        return de, ate

    @staticmethod
    def _intervalo(de, ate):
        """[00:00 de "de", 00:00 do dia seguinte a "ate") no fuso da barbearia."""
        return intervalo_do_dia(de)[0], intervalo_do_dia(ate)[1]

    def _serie(self, granularidade, de, ate, linhas, vazio):
        por_periodo = {periodo.date(): valor for periodo, valor in linhas}
        periodos = self._periodos(granularidade, de, ate)
        return {
            "granularidade": granularidade,
            "de": de,
            "ate": ate,
            "labels": [self._rotulo(granularidade, p) for p in periodos],
            "valores": [por_periodo.get(p, vazio) for p in periodos],
        }

    @staticmethod
    def _periodos(granularidade, de, ate):
        """Inicio de cada semana (segunda) ou mes que toca [de, ate]. O banco so
        devolve periodos com movimento; os vazios entram aqui, com zero.
        """
        periodos = []
        if granularidade == GRANULARIDADE_SEMANA:
            atual = de - timedelta(days=de.weekday())
            while atual <= ate:
                periodos.append(atual)
                atual += timedelta(days=7)
        else:
            atual = de.replace(day=1)
            while atual <= ate:
                periodos.append(atual)
                # Dia 28 + 4 sempre cai no mes seguinte.
                atual = (atual.replace(day=28) + timedelta(days=4)).replace(day=1)
        return periodos

    @staticmethod
    def _rotulo(granularidade, inicio):
        if granularidade == GRANULARIDADE_SEMANA:
            return inicio.isoformat()
        return inicio.strftime("%Y-%m")
