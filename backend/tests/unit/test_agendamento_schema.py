from datetime import datetime, timezone

import pytest
from marshmallow import ValidationError

from app.schemas.agendamento_schema import (
    AgendamentoCriacaoSchema,
    AgendamentoFiltroSchema,
    DataHoraComFuso,
)

VALIDO = {"cliente_id": 1, "barbeiro_id": 2, "inicio": "2026-10-20T14:30:00-03:00", "servico_ids": [1, 2]}


def carregar(**mudancas):
    return AgendamentoCriacaoSchema().load(dict(VALIDO, **mudancas))


def test_inicio_vira_datetime_com_fuso():
    assert carregar()["inicio"] == datetime(2026, 10, 20, 17, 30, tzinfo=timezone.utc)


def test_aceita_utc_com_z():
    assert carregar(inicio="2026-10-20T17:30:00Z")["inicio"].utcoffset() is not None


def test_recusa_horario_sem_fuso():
    with pytest.raises(ValidationError) as erro:
        carregar(inicio="2026-10-20T14:30:00")
    assert "inicio" in erro.value.messages


def test_recusa_segundos():
    with pytest.raises(ValidationError) as erro:
        carregar(inicio="2026-10-20T14:30:15-03:00")
    assert erro.value.messages["inicio"] == ["Informe o horário sem segundos."]


@pytest.mark.parametrize("servico_ids", [[], list(range(1, 12)), ["1"]])
def test_lista_de_servicos_invalida(servico_ids):
    with pytest.raises(ValidationError) as erro:
        carregar(servico_ids=servico_ids)
    assert "servico_ids" in erro.value.messages


def test_observacao_em_branco_vira_nula():
    assert carregar(observacao="   ")["observacao"] is None


def test_campo_desconhecido_e_recusado():
    with pytest.raises(ValidationError):
        carregar(fim="2026-10-20T15:00:00-03:00")


def test_saida_no_fuso_da_barbearia():
    campo = DataHoraComFuso()
    valor = datetime(2026, 10, 20, 17, 30, tzinfo=timezone.utc)
    assert campo.serialize("x", {"x": valor}) == "2026-10-20T14:30:00-03:00"


def test_filtro_ignora_vazios_e_recusa_status_desconhecido():
    assert AgendamentoFiltroSchema().load({"dia": "", "status": ""})["dia"] is None
    with pytest.raises(ValidationError):
        AgendamentoFiltroSchema().load({"status": "pendente"})
