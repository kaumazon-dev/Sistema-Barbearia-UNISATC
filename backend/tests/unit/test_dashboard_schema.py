from datetime import date

import pytest
from marshmallow import ValidationError

from app.schemas.dashboard_schema import RankingFiltroSchema, SerieFiltroSchema


def test_sem_parametros_usa_padroes():
    assert SerieFiltroSchema().load({}) == {
        "de": None,
        "ate": None,
        "granularidade": "semana",
    }
    assert RankingFiltroSchema().load({})["limite"] == 5


def test_parametro_vazio_vale_como_ausente():
    assert SerieFiltroSchema().load({"de": "", "ate": "", "granularidade": ""}) == {
        "de": None,
        "ate": None,
        "granularidade": "semana",
    }


def test_periodo_valido():
    dados = SerieFiltroSchema().load(
        {"de": "2026-10-01", "ate": "2026-10-31", "granularidade": "mes"}
    )

    assert (dados["de"], dados["ate"]) == (date(2026, 10, 1), date(2026, 10, 31))


def test_um_dia_so_e_valido():
    assert SerieFiltroSchema().load({"de": "2026-10-01", "ate": "2026-10-01"})


@pytest.mark.parametrize(
    "parametros, campo",
    [
        ({"de": "2026-10-01"}, "ate"),
        ({"ate": "2026-10-01"}, "de"),
        ({"de": "2026-10-31", "ate": "2026-10-01"}, "ate"),
        ({"de": "2026-01-01", "ate": "2027-01-02"}, "ate"),  # 366 dias de diferenca
        ({"de": "31/10/2026", "ate": "2026-11-01"}, "de"),
        ({"granularidade": "dia"}, "granularidade"),
    ],
)
def test_parametros_invalidos(parametros, campo):
    with pytest.raises(ValidationError) as erro:
        SerieFiltroSchema().load(parametros)
    assert campo in erro.value.messages


@pytest.mark.parametrize("limite", ["0", "21", "abc"])
def test_limite_do_ranking_fora_da_faixa(limite):
    with pytest.raises(ValidationError) as erro:
        RankingFiltroSchema().load({"limite": limite})
    assert "limite" in erro.value.messages
