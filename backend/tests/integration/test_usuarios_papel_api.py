"""PATCH /auth/usuarios/<id>/papel: o admin decide quem e barbeiro ou admin."""

from datetime import datetime, timedelta, timezone

import pytest

from app.extensions import db
from app.models.agendamento import STATUS_AGENDADO, STATUS_CANCELADO, Agendamento
from app.models.usuario import PAPEL_ADMIN, PAPEL_BARBEIRO, PAPEL_CLIENTE, Usuario
from tests.integration.fabricas import cabecalho_de, criar_usuario


def url(usuario_id):
    return f"/api/v1/auth/usuarios/{usuario_id}/papel"


def papel_no_banco(usuario_id):
    db.session.expire_all()
    return db.session.get(Usuario, usuario_id).papel


def marcar(barbeiro, cliente, daqui_a, status=STATUS_AGENDADO):
    inicio = datetime.now(timezone.utc) + daqui_a
    db.session.add(
        Agendamento(
            cliente_id=cliente.id,
            barbeiro_id=barbeiro.id,
            inicio=inicio,
            fim=inicio + timedelta(minutes=30),
            status=status,
        )
    )
    db.session.commit()


@pytest.mark.parametrize("novo", [PAPEL_BARBEIRO, PAPEL_ADMIN])
def test_admin_promove_cliente(client, admin, novo):
    ana = criar_usuario(PAPEL_CLIENTE, nome="Ana")

    resposta = client.patch(url(ana.id), json={"papel": novo}, headers=admin)

    assert resposta.status_code == 200
    corpo = resposta.get_json()
    assert (corpo["id"], corpo["papel"]) == (ana.id, novo)
    assert "senha_hash" not in corpo
    assert papel_no_banco(ana.id) == novo


def test_promovido_a_barbeiro_aparece_para_agendar(client, admin, cliente_logado):
    pedro = criar_usuario(PAPEL_CLIENTE, nome="Pedro")
    client.patch(url(pedro.id), json={"papel": PAPEL_BARBEIRO}, headers=admin)

    resposta = client.get("/api/v1/auth/barbeiros", headers=cliente_logado)

    assert {"id": pedro.id, "nome": "Pedro"} in resposta.get_json()


@pytest.mark.parametrize("quem", ["barbeiro", "cliente_logado"])
def test_so_admin_altera_papel(client, request, quem):
    alvo = criar_usuario(PAPEL_CLIENTE)
    cabecalho = request.getfixturevalue(quem)

    resposta = client.patch(url(alvo.id), json={"papel": PAPEL_ADMIN}, headers=cabecalho)

    assert resposta.status_code == 403
    assert papel_no_banco(alvo.id) == PAPEL_CLIENTE


def test_sem_token_da_401(client):
    alvo = criar_usuario(PAPEL_CLIENTE)

    assert client.patch(url(alvo.id), json={"papel": PAPEL_ADMIN}).status_code == 401


def test_admin_nao_altera_o_proprio_papel(client):
    eu = criar_usuario(PAPEL_ADMIN)

    resposta = client.patch(url(eu.id), json={"papel": PAPEL_CLIENTE}, headers=cabecalho_de(eu))

    assert resposta.status_code == 422
    assert papel_no_banco(eu.id) == PAPEL_ADMIN


@pytest.mark.parametrize("corpo", [{"papel": "dono"}, {}, {"papel": "admin", "ativo": False}])
def test_corpo_invalido_da_422(client, admin, corpo):
    alvo = criar_usuario(PAPEL_CLIENTE)

    resposta = client.patch(url(alvo.id), json=corpo, headers=admin)

    assert resposta.status_code == 422
    assert resposta.get_json()["erro"]["codigo"] == "DADOS_INVALIDOS"


def test_usuario_inexistente_da_404(client, admin):
    assert client.patch(url(999999), json={"papel": PAPEL_ADMIN}, headers=admin).status_code == 404


def test_barbeiro_com_horario_futuro_nao_deixa_de_ser_barbeiro(client, admin):
    joao = criar_usuario(PAPEL_BARBEIRO, nome="João")
    marcar(joao, criar_usuario(PAPEL_CLIENTE), daqui_a=timedelta(days=1))

    resposta = client.patch(url(joao.id), json={"papel": PAPEL_CLIENTE}, headers=admin)

    assert resposta.status_code == 422
    assert "1 horário marcado" in resposta.get_json()["erro"]["mensagem"]
    assert papel_no_banco(joao.id) == PAPEL_BARBEIRO


def test_horario_passado_ou_cancelado_nao_segura_o_barbeiro(client, admin):
    joao = criar_usuario(PAPEL_BARBEIRO)
    cliente = criar_usuario(PAPEL_CLIENTE)
    marcar(joao, cliente, daqui_a=timedelta(days=-1))
    marcar(joao, cliente, daqui_a=timedelta(days=2), status=STATUS_CANCELADO)

    resposta = client.patch(url(joao.id), json={"papel": PAPEL_CLIENTE}, headers=admin)

    assert resposta.status_code == 200
    assert papel_no_banco(joao.id) == PAPEL_CLIENTE
