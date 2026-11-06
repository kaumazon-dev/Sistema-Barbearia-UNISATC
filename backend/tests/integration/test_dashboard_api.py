"""Rotas do dashboard contra o banco real: a agregacao roda no Postgres."""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.core.fuso import FUSO_BARBEARIA
from app.extensions import db
from app.models.agendamento import (
    STATUS_AGENDADO,
    STATUS_CANCELADO,
    STATUS_CONCLUIDO,
    Agendamento,
    AgendamentoServico,
)
from app.models.servico import Servico
from app.models.usuario import PAPEL_BARBEIRO, PAPEL_CLIENTE
from tests.integration.fabricas import criar_usuario

URL = "/api/v1/dashboard"
OUTUBRO = {"de": "2026-10-01", "ate": "2026-10-31"}


def criar_servico(nome, preco):
    servico = Servico(nome=nome, duracao_minutos=30, preco=Decimal(preco))
    db.session.add(servico)
    db.session.commit()
    return servico


@pytest.fixture
def cenario():
    return {
        "joao": criar_usuario(PAPEL_BARBEIRO, nome="João"),
        "ana": criar_usuario(PAPEL_CLIENTE, nome="Ana"),
        "corte": criar_servico("Corte", "40.00"),
        "barba": criar_servico("Barba", "25.00"),
    }


def gravar(cenario, quando, status=STATUS_CONCLUIDO, itens=(("corte", "40.00"),)):
    """Grava direto no banco: a API nao deixa marcar no passado."""
    inicio = datetime.fromisoformat(quando).replace(tzinfo=FUSO_BARBEARIA)
    agendamento = Agendamento(
        cliente_id=cenario["ana"].id,
        barbeiro_id=cenario["joao"].id,
        inicio=inicio,
        fim=inicio + timedelta(hours=1),
        status=status,
        itens=[
            AgendamentoServico(servico_id=cenario[nome].id, preco_cobrado=Decimal(preco))
            for nome, preco in itens
        ],
    )
    db.session.add(agendamento)
    db.session.commit()
    return agendamento


def get(client, cabecalho, rota, **parametros):
    resposta = client.get(f"{URL}/{rota}", query_string=parametros, headers=cabecalho)
    return resposta.status_code, resposta.get_json()


# --- acesso ----------------------------------------------------------------------

ROTAS = ("atendimentos", "faturamento", "servicos-ranking", "cancelamento")


@pytest.mark.parametrize("rota", ROTAS)
def test_so_admin_acessa(client, barbeiro, cliente_logado, rota):
    assert client.get(f"{URL}/{rota}").status_code == 401
    assert client.get(f"{URL}/{rota}", headers=barbeiro).status_code == 403
    assert client.get(f"{URL}/{rota}", headers=cliente_logado).status_code == 403


# --- atendimentos (RF28) ---------------------------------------------------------


def test_atendimentos_por_semana_conta_so_concluidos(client, admin, cenario):
    gravar(cenario, "2026-10-06 09:00")
    gravar(cenario, "2026-10-07 09:00", itens=(("corte", "40.00"), ("barba", "25.00")))
    gravar(cenario, "2026-10-08 09:00", status=STATUS_CANCELADO)
    gravar(cenario, "2026-10-09 09:00", status=STATUS_AGENDADO)
    gravar(cenario, "2026-10-21 09:00")

    status, corpo = get(client, admin, "atendimentos", granularidade="semana", **OUTUBRO)

    assert status == 200
    assert corpo["labels"] == [
        "2026-09-28",
        "2026-10-05",
        "2026-10-12",
        "2026-10-19",
        "2026-10-26",
    ]
    # Corte + barba e um atendimento so, nao dois.
    assert corpo["valores"] == [0, 2, 0, 1, 0]
    assert (corpo["de"], corpo["ate"], corpo["granularidade"]) == (
        "2026-10-01",
        "2026-10-31",
        "semana",
    )


def test_domingo_a_noite_fica_na_semana_de_brasilia(client, admin, cenario):
    # Domingo 18/10 22h em Brasilia ja e segunda 19/10 em UTC.
    gravar(cenario, "2026-10-18 22:00")

    _, corpo = get(client, admin, "atendimentos", granularidade="semana", **OUTUBRO)

    semanas = dict(zip(corpo["labels"], corpo["valores"]))
    assert semanas["2026-10-12"] == 1
    assert semanas["2026-10-19"] == 0


def test_limites_do_periodo(client, admin, cenario):
    gravar(cenario, "2026-09-30 23:00")  # fora
    gravar(cenario, "2026-10-01 00:00")  # primeiro minuto: dentro
    gravar(cenario, "2026-10-31 23:00")  # ultimo dia: dentro ("ate" e inclusivo)
    gravar(cenario, "2026-11-01 00:00")  # fora

    _, corpo = get(client, admin, "atendimentos", granularidade="mes", **OUTUBRO)

    assert corpo["labels"] == ["2026-10"]
    assert corpo["valores"] == [2]


# --- faturamento (RF29) ----------------------------------------------------------


def test_faturamento_soma_preco_cobrado_e_nao_o_preco_atual(client, admin, cenario):
    gravar(cenario, "2026-09-10 09:00", itens=(("corte", "35.00"),))
    gravar(cenario, "2026-10-10 09:00", itens=(("corte", "40.00"), ("barba", "25.00")))
    gravar(cenario, "2026-10-11 09:00", status=STATUS_CANCELADO)
    # Reajuste depois das marcacoes nao pode mexer no que ja foi faturado.
    cenario["corte"].preco = Decimal("99.00")
    db.session.commit()

    status, corpo = get(
        client, admin, "faturamento", granularidade="mes", de="2026-09-01", ate="2026-10-31"
    )

    assert status == 200
    assert corpo["labels"] == ["2026-09", "2026-10"]
    assert corpo["valores"] == ["35.00", "65.00"]


def test_faturamento_sem_movimento_sai_zerado(client, admin):
    _, corpo = get(client, admin, "faturamento", granularidade="mes", **OUTUBRO)

    assert corpo["valores"] == ["0.00"]


# --- ranking (RF30) --------------------------------------------------------------


def test_ranking_ordena_pelo_mais_vendido(client, admin, cenario):
    gravar(cenario, "2026-10-05 09:00", itens=(("barba", "25.00"),))
    gravar(cenario, "2026-10-06 09:00", itens=(("barba", "25.00"),))
    gravar(cenario, "2026-10-07 09:00", itens=(("corte", "40.00"), ("barba", "20.00")))
    gravar(cenario, "2026-10-08 09:00", status=STATUS_CANCELADO, itens=(("corte", "40.00"),))

    status, corpo = get(client, admin, "servicos-ranking", **OUTUBRO)

    assert status == 200
    assert corpo["labels"] == ["Barba", "Corte"]
    assert corpo["valores"] == [3, 1]
    assert corpo["receitas"] == ["70.00", "40.00"]


def test_ranking_respeita_o_limite(client, admin, cenario):
    gravar(cenario, "2026-10-05 09:00", itens=(("corte", "40.00"), ("barba", "25.00")))

    _, corpo = get(client, admin, "servicos-ranking", limite=1, **OUTUBRO)

    assert len(corpo["labels"]) == 1


# --- cancelamento (RF31) ---------------------------------------------------------


def test_taxa_de_cancelamento_ignora_agendados(client, admin, cenario):
    for dia in (5, 6, 7):
        gravar(cenario, f"2026-10-0{dia} 09:00")
    gravar(cenario, "2026-10-08 09:00", status=STATUS_CANCELADO)
    gravar(cenario, "2026-10-09 09:00", status=STATUS_AGENDADO)

    status, corpo = get(client, admin, "cancelamento", **OUTUBRO)

    assert status == 200
    assert corpo["concluidos"] == 3
    assert corpo["cancelados"] == 1
    assert corpo["total"] == 4
    assert corpo["taxa"] == "25.00"
    assert corpo["labels"] == ["Concluídos", "Cancelados"]
    assert corpo["valores"] == [3, 1]


def test_sem_desfecho_a_taxa_e_nula(client, admin):
    _, corpo = get(client, admin, "cancelamento", **OUTUBRO)

    assert corpo["taxa"] is None
    assert corpo["total"] == 0


# --- validacao -------------------------------------------------------------------


def test_periodo_invalido_da_422(client, admin):
    status, corpo = get(client, admin, "atendimentos", de="2026-10-31", ate="2026-10-01")

    assert status == 422
    assert corpo["erro"]["codigo"] == "DADOS_INVALIDOS"
    assert "ate" in corpo["erro"]["campos"]


def test_sem_datas_responde_o_mes_atual(client, admin):
    hoje = datetime.now(FUSO_BARBEARIA).date()

    status, corpo = get(client, admin, "atendimentos")

    assert status == 200
    assert corpo["de"] == hoje.replace(day=1).isoformat()
    assert corpo["ate"] == hoje.isoformat()
    assert corpo["granularidade"] == "semana"
