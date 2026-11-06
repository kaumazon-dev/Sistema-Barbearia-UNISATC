from decimal import Decimal

import pytest
from marshmallow import ValidationError

from app.schemas.cliente_schema import ClienteAtualizacaoSchema, ClienteFiltroSchema
from app.schemas.paginacao_schema import montar_pagina
from app.schemas.servico_schema import (
    ServicoAtualizacaoSchema,
    ServicoCadastroSchema,
    ServicoSchema,
)

SERVICO_VALIDO = {"nome": " Corte ", "duracao_minutos": 30, "preco": "35.90"}


def test_servico_valido_vira_decimal_e_nome_sem_espacos():
    dados = ServicoCadastroSchema().load(SERVICO_VALIDO)

    assert dados["preco"] == Decimal("35.90")
    assert isinstance(dados["preco"], Decimal)
    assert dados["nome"] == "Corte"


def test_preco_numerico_no_json_tambem_e_aceito():
    dados = ServicoCadastroSchema().load(dict(SERVICO_VALIDO, preco=35.9))

    assert dados["preco"] == Decimal("35.9")


@pytest.mark.parametrize("preco", ["35.999", "-1", "abc", "100000000.00", "NaN"])
def test_preco_invalido_recusa(preco):
    with pytest.raises(ValidationError) as erro:
        ServicoCadastroSchema().load(dict(SERVICO_VALIDO, preco=preco))

    assert "preco" in erro.value.messages


@pytest.mark.parametrize("duracao", [0, -5, 481, 30.5, "30"])
def test_duracao_invalida_recusa(duracao):
    with pytest.raises(ValidationError) as erro:
        ServicoCadastroSchema().load(dict(SERVICO_VALIDO, duracao_minutos=duracao))

    assert "duracao_minutos" in erro.value.messages


def test_servico_sai_com_preco_em_string_e_duas_casas():
    class Fake:
        id, nome, duracao_minutos, preco, ativo = 1, "Corte", 30, Decimal("35"), True

    assert ServicoSchema().dump(Fake())["preco"] == "35.00"


def test_atualizacao_de_servico_aceita_corpo_parcial():
    dados = ServicoAtualizacaoSchema().load({"ativo": True}, partial=True)

    assert dados == {"ativo": True}


def test_atualizacao_de_cliente_recusa_senha_e_papel():
    with pytest.raises(ValidationError) as erro:
        ClienteAtualizacaoSchema().load({"senha": "nova-senha-123", "papel": "admin"})

    assert set(erro.value.messages) == {"senha", "papel"}


def test_atualizacao_de_cliente_normaliza_email():
    dados = ClienteAtualizacaoSchema().load({"email": " Joao@X.com "})

    assert dados["email"] == "joao@x.com"


def test_filtro_de_cliente_tem_padroes_e_ignora_vazios():
    dados = ClienteFiltroSchema().load({"busca": "", "ativo": "", "outro": "x"})

    assert dados == {"busca": None, "ativo": None, "pagina": 1, "por_pagina": 20}


@pytest.mark.parametrize("parametros", [{"pagina": "0"}, {"por_pagina": "101"}, {"pagina": "a"}])
def test_filtro_de_cliente_recusa_paginacao_invalida(parametros):
    with pytest.raises(ValidationError):
        ClienteFiltroSchema().load(parametros)


def test_montar_pagina_calcula_total_de_paginas():
    assert montar_pagina([], 41, 1, 20)["paginas"] == 3
    assert montar_pagina([], 0, 1, 20)["paginas"] == 0
