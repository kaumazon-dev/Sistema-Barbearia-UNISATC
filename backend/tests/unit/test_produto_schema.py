from decimal import Decimal

import pytest
from marshmallow import ValidationError

from app.schemas.produto_schema import (
    MovimentacaoCriacaoSchema,
    MovimentacaoFiltroSchema,
    ProdutoAtualizacaoSchema,
    ProdutoCadastroSchema,
)

POMADA = {"nome": "  Pomada  ", "unidade": "g", "estoque_minimo": "5"}


def test_cadastro_valido():
    dados = ProdutoCadastroSchema().load(POMADA)
    assert dados == {"nome": "Pomada", "unidade": "g", "estoque_minimo": Decimal("5")}


def test_cadastro_sem_estoque_minimo_vira_zero():
    dados = ProdutoCadastroSchema().load({"nome": "Pomada", "unidade": "un"})
    assert dados["estoque_minimo"] == Decimal("0")


def test_cadastro_recusa_quantidade_atual():
    """RN04: estoque inicial entra por movimentacao, nunca pelo cadastro."""
    with pytest.raises(ValidationError) as erro:
        ProdutoCadastroSchema().load(dict(POMADA, quantidade_atual="10"))
    assert "quantidade_atual" in erro.value.messages


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("unidade", "litro"),
        ("estoque_minimo", "-1"),
        ("estoque_minimo", "1.555"),
        ("nome", " a "),
    ],
)
def test_cadastro_invalido(campo, valor):
    with pytest.raises(ValidationError) as erro:
        ProdutoCadastroSchema().load(dict(POMADA, **{campo: valor}))
    assert campo in erro.value.messages


def test_atualizacao_parcial_nao_zera_estoque_minimo():
    dados = ProdutoAtualizacaoSchema().load({"nome": "Pomada"}, partial=True)
    assert dados == {"nome": "Pomada"}


def test_atualizacao_recusa_quantidade_atual():
    with pytest.raises(ValidationError):
        ProdutoAtualizacaoSchema().load({"quantidade_atual": "10"}, partial=True)


@pytest.mark.parametrize("quantidade", ["0", "-1", "1.001", "abc"])
def test_movimentacao_quantidade_invalida(quantidade):
    with pytest.raises(ValidationError) as erro:
        MovimentacaoCriacaoSchema().load({"quantidade": quantidade})
    assert "quantidade" in erro.value.messages


def test_movimentacao_aceita_fracao_e_motivo_vazio_vira_none():
    dados = MovimentacaoCriacaoSchema().load({"quantidade": "0.5", "motivo": "   "})
    assert dados == {"quantidade": Decimal("0.5"), "motivo": None}


def test_movimentacao_recusa_tipo_no_corpo():
    # O tipo vem da rota (/entradas ou /saidas), nao do corpo.
    with pytest.raises(ValidationError):
        MovimentacaoCriacaoSchema().load({"quantidade": "1", "tipo": "saida"})


def test_filtro_de_movimentacoes():
    assert MovimentacaoFiltroSchema().load({"tipo": "", "pagina": "2"}) == {
        "tipo": None,
        "pagina": 2,
        "por_pagina": 20,
    }
    with pytest.raises(ValidationError):
        MovimentacaoFiltroSchema().load({"tipo": "ajuste"})
