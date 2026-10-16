from decimal import Decimal

import pytest

from app.extensions import db
from app.models.servico import Servico

URL = "/api/v1/servicos"
CORTE = {"nome": "Corte", "duracao_minutos": 30, "preco": "35.90"}


def criar_servico(nome="Corte", ativo=True, preco="35.00"):
    servico = Servico(nome=nome, duracao_minutos=30, preco=Decimal(preco), ativo=ativo)
    db.session.add(servico)
    db.session.commit()
    return servico


def test_admin_cadastra_servico_e_preco_volta_exato(client, admin):
    resposta = client.post(URL, json=CORTE, headers=admin)

    assert resposta.status_code == 201
    corpo = resposta.get_json()
    assert corpo["preco"] == "35.90"
    assert corpo["ativo"] is True
    db.session.expire_all()
    assert db.session.get(Servico, corpo["id"]).preco == Decimal("35.90")


def test_preco_com_tres_casas_da_422(client, admin):
    resposta = client.post(URL, json=dict(CORTE, preco="35.999"), headers=admin)

    assert resposta.status_code == 422
    assert "preco" in resposta.get_json()["erro"]["campos"]


@pytest.mark.parametrize("metodo", ["post", "put", "delete"])
def test_barbeiro_nao_escreve_servico(client, barbeiro, metodo):
    servico = criar_servico()
    url = URL if metodo == "post" else f"{URL}/{servico.id}"

    resposta = getattr(client, metodo)(url, json=CORTE, headers=barbeiro)

    assert resposta.status_code == 403


def test_cliente_so_ve_servicos_ativos(client, cliente_logado):
    criar_servico("Corte")
    inativo = criar_servico("Antigo", ativo=False)

    lista = client.get(f"{URL}?ativo=false", headers=cliente_logado).get_json()
    detalhe = client.get(f"{URL}/{inativo.id}", headers=cliente_logado)

    assert [s["nome"] for s in lista] == ["Corte"]
    assert detalhe.status_code == 404


def test_admin_ve_todos_e_filtra(client, admin):
    criar_servico("Corte")
    criar_servico("Antigo", ativo=False)

    todos = client.get(URL, headers=admin).get_json()
    inativos = client.get(f"{URL}?ativo=false", headers=admin).get_json()

    assert [s["nome"] for s in todos] == ["Antigo", "Corte"]
    assert [s["nome"] for s in inativos] == ["Antigo"]


def test_atualizar_parcial(client, admin):
    servico = criar_servico()

    resposta = client.put(f"{URL}/{servico.id}", json={"preco": 40}, headers=admin)

    assert resposta.status_code == 200
    assert resposta.get_json()["preco"] == "40.00"
    assert resposta.get_json()["duracao_minutos"] == 30


def test_desativar_mantem_registro(client, admin):
    servico = criar_servico()

    resposta = client.delete(f"{URL}/{servico.id}", headers=admin)

    assert resposta.status_code == 204
    db.session.expire_all()
    assert db.session.get(Servico, servico.id).ativo is False


def test_servico_inexistente_da_404(client, admin):
    resposta = client.put(f"{URL}/999", json={"nome": "X Y"}, headers=admin)

    assert resposta.status_code == 404
    assert resposta.get_json()["erro"]["codigo"] == "NAO_ENCONTRADO"
