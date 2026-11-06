from decimal import Decimal

import pytest
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.extensions import db
from app.models.produto import MovimentacaoEstoque, Produto
from app.repositories.movimentacao_estoque_repository import (
    MovimentacaoEstoqueRepository,
)
from app.repositories.produto_repository import ProdutoRepository
from app.services.estoque_service import EstoqueService

URL = "/api/v1/produtos"
POMADA = {"nome": "Pomada", "unidade": "g", "estoque_minimo": "5"}


def cadastrar(client, admin, **campos):
    resposta = client.post(URL, json=dict(POMADA, **campos), headers=admin)
    assert resposta.status_code == 201
    return resposta.get_json()


def entrada(client, admin, produto_id, quantidade, motivo=None):
    return client.post(
        f"{URL}/{produto_id}/entradas",
        json={"quantidade": quantidade, "motivo": motivo},
        headers=admin,
    )


def saida(client, admin, produto_id, quantidade, motivo=None):
    return client.post(
        f"{URL}/{produto_id}/saidas",
        json={"quantidade": quantidade, "motivo": motivo},
        headers=admin,
    )


def no_banco(produto_id):
    """(quantidade_atual, total de movimentacoes) lidos de novo do banco."""
    db.session.expire_all()
    produto = db.session.get(Produto, produto_id)
    total = db.session.scalar(
        db.select(db.func.count())
        .select_from(MovimentacaoEstoque)
        .where(MovimentacaoEstoque.produto_id == produto_id)
    )
    return produto.quantidade_atual, total


# --- cadastro ---------------------------------------------------------------------


def test_produto_nasce_zerado_e_em_falta(client, admin):
    produto = cadastrar(client, admin)

    assert produto["quantidade_atual"] == "0.00"
    assert produto["estoque_minimo"] == "5.00"
    assert produto["em_falta"] is True
    assert produto["ativo"] is True


def test_cadastro_nao_aceita_quantidade(client, admin):
    resposta = client.post(URL, json=dict(POMADA, quantidade_atual="10"), headers=admin)

    assert resposta.status_code == 422
    assert "quantidade_atual" in resposta.get_json()["erro"]["campos"]


def test_edicao_nao_aceita_quantidade(client, admin):
    produto = cadastrar(client, admin)

    resposta = client.put(
        f"{URL}/{produto['id']}", json={"quantidade_atual": "10"}, headers=admin
    )

    assert resposta.status_code == 422
    assert no_banco(produto["id"]) == (Decimal("0"), 0)


def test_editar_estoque_minimo_recalcula_em_falta(client, admin):
    produto = cadastrar(client, admin)
    entrada(client, admin, produto["id"], "3")

    resposta = client.put(
        f"{URL}/{produto['id']}", json={"estoque_minimo": "2"}, headers=admin
    )

    assert resposta.get_json()["em_falta"] is False


def test_desativar_mantem_registro(client, admin):
    produto = cadastrar(client, admin)

    resposta = client.delete(f"{URL}/{produto['id']}", headers=admin)

    assert resposta.status_code == 204
    detalhe = client.get(f"{URL}/{produto['id']}", headers=admin).get_json()
    assert detalhe["ativo"] is False


@pytest.mark.parametrize("papel", ["barbeiro", "cliente_logado"])
@pytest.mark.parametrize(
    "metodo, caminho",
    [
        ("get", ""),
        ("get", "/em-falta"),
        ("post", ""),
        ("post", "/1/entradas"),
        ("post", "/1/saidas"),
        ("get", "/1/movimentacoes"),
    ],
)
def test_estoque_e_so_do_admin(client, request, papel, metodo, caminho):
    cabecalho = request.getfixturevalue(papel)
    resposta = getattr(client, metodo)(URL + caminho, json={}, headers=cabecalho)
    assert resposta.status_code == 403


# --- movimentacao ------------------------------------------------------------------


def test_entrada_soma_e_grava_movimentacao(client, admin):
    produto = cadastrar(client, admin)

    resposta = entrada(client, admin, produto["id"], "10.5", "compra")

    assert resposta.status_code == 201
    corpo = resposta.get_json()
    assert corpo["tipo"] == "entrada"
    assert corpo["quantidade"] == "10.50"
    assert corpo["motivo"] == "compra"
    assert corpo["usuario"]["id"] is not None
    assert corpo["produto"]["quantidade_atual"] == "10.50"
    assert corpo["produto"]["em_falta"] is False
    assert no_banco(produto["id"]) == (Decimal("10.50"), 1)


def test_saida_subtrai_e_grava_movimentacao(client, admin):
    produto = cadastrar(client, admin)
    entrada(client, admin, produto["id"], "10")

    resposta = saida(client, admin, produto["id"], "7", "uso no atendimento")

    assert resposta.status_code == 201
    assert resposta.get_json()["produto"]["quantidade_atual"] == "3.00"
    assert resposta.get_json()["produto"]["em_falta"] is True
    assert no_banco(produto["id"]) == (Decimal("3"), 2)


def test_saida_maior_que_o_disponivel_e_recusada_sem_gravar_nada(client, admin):
    produto = cadastrar(client, admin)
    entrada(client, admin, produto["id"], "2")

    resposta = saida(client, admin, produto["id"], "2.01")

    assert resposta.status_code == 422
    assert resposta.get_json()["erro"]["codigo"] == "REGRA_VIOLADA"
    assert no_banco(produto["id"]) == (Decimal("2"), 1)


def test_saida_de_tudo_zera(client, admin):
    produto = cadastrar(client, admin)
    entrada(client, admin, produto["id"], "2")

    assert saida(client, admin, produto["id"], "2").status_code == 201
    assert no_banco(produto["id"]) == (Decimal("0"), 2)


def test_movimentar_produto_desativado(client, admin):
    produto = cadastrar(client, admin)
    client.delete(f"{URL}/{produto['id']}", headers=admin)

    resposta = entrada(client, admin, produto["id"], "1")

    assert resposta.status_code == 422
    assert no_banco(produto["id"]) == (Decimal("0"), 0)


def test_movimentar_produto_inexistente(client, admin):
    assert entrada(client, admin, 999999, "1").status_code == 404


@pytest.mark.parametrize("quantidade", ["0", "-1", "1.001"])
def test_quantidade_invalida(client, admin, quantidade):
    produto = cadastrar(client, admin)
    assert entrada(client, admin, produto["id"], quantidade).status_code == 422


def test_falha_no_commit_desfaz_as_duas_escritas(app, admin):
    """Regra de ouro: se a movimentacao nao grava, a quantidade nao muda.

    usuario_id inexistente faz a FK falhar no commit, depois de o service ja
    ter alterado a quantidade em memoria.
    """
    produto = Produto(nome="Pomada", unidade="g", estoque_minimo=Decimal("0"))
    db.session.add(produto)
    db.session.commit()
    service = EstoqueService(ProdutoRepository(), MovimentacaoEstoqueRepository())

    with pytest.raises(IntegrityError):
        service.registrar_entrada(produto.id, Decimal("5"), usuario_id=999999)

    assert no_banco(produto.id) == (Decimal("0"), 0)


# --- historico imutavel ------------------------------------------------------------

# SQLSTATE do RAISE do trigger (restrict_violation).
_HISTORICO_IMUTAVEL = "23001"


def _primeira_movimentacao(client, admin):
    produto = cadastrar(client, admin)
    entrada(client, admin, produto["id"], "10", "compra")
    db.session.expire_all()
    return db.session.scalar(db.select(MovimentacaoEstoque))


@pytest.mark.parametrize(
    "sql",
    [
        "UPDATE movimentacao_estoque SET quantidade = 999",
        "UPDATE movimentacao_estoque SET motivo = 'editado'",
        "DELETE FROM movimentacao_estoque",
    ],
)
def test_banco_recusa_editar_ou_apagar_movimentacao(client, admin, sql):
    """Mesmo por fora da API (SQL solto, pgAdmin), o historico nao muda."""
    movimentacao = _primeira_movimentacao(client, admin)

    with pytest.raises(DBAPIError) as erro:
        db.session.execute(db.text(sql))
        db.session.commit()
    db.session.rollback()

    assert erro.value.orig.pgcode == _HISTORICO_IMUTAVEL
    db.session.expire_all()
    intacta = db.session.get(MovimentacaoEstoque, movimentacao.id)
    assert (intacta.quantidade, intacta.motivo) == (Decimal("10"), "compra")


def test_orm_tambem_nao_edita_movimentacao(client, admin):
    movimentacao = _primeira_movimentacao(client, admin)

    movimentacao.motivo = "editado"
    with pytest.raises(DBAPIError):
        db.session.commit()
    db.session.rollback()

    db.session.expire_all()
    assert db.session.get(MovimentacaoEstoque, movimentacao.id).motivo == "compra"


# --- produtos em falta (RF27) ----------------------------------------------------


def test_lista_em_falta(client, admin):
    acima = cadastrar(client, admin, nome="Acima")
    no_minimo = cadastrar(client, admin, nome="No minimo")
    abaixo = cadastrar(client, admin, nome="Abaixo")
    inativo = cadastrar(client, admin, nome="Inativo")
    entrada(client, admin, acima["id"], "6")
    entrada(client, admin, no_minimo["id"], "5")
    entrada(client, admin, abaixo["id"], "4.99")
    client.delete(f"{URL}/{inativo['id']}", headers=admin)

    resposta = client.get(f"{URL}/em-falta", headers=admin)

    assert resposta.status_code == 200
    assert [p["nome"] for p in resposta.get_json()] == ["Abaixo", "No minimo"]


# --- historico ----------------------------------------------------------------------


def test_historico_paginado_do_mais_recente_e_filtra_tipo(client, admin):
    produto = cadastrar(client, admin)
    entrada(client, admin, produto["id"], "10", "primeira")
    saida(client, admin, produto["id"], "1", "segunda")
    saida(client, admin, produto["id"], "2", "terceira")
    url = f"{URL}/{produto['id']}/movimentacoes"

    pagina = client.get(f"{url}?por_pagina=2", headers=admin).get_json()
    entradas = client.get(f"{url}?tipo=entrada", headers=admin).get_json()

    assert pagina["total"] == 3
    assert pagina["paginas"] == 2
    assert [m["motivo"] for m in pagina["itens"]] == ["terceira", "segunda"]
    assert "produto" not in pagina["itens"][0]
    assert [m["motivo"] for m in entradas["itens"]] == ["primeira"]


def test_historico_de_produto_inexistente(client, admin):
    assert client.get(f"{URL}/999999/movimentacoes", headers=admin).status_code == 404
