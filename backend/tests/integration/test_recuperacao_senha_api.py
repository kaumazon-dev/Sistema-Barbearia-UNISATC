import pytest

from app.core.email import EnviadorEmailLog
from app.models.usuario import PAPEL_CLIENTE
from tests.integration.fabricas import criar_usuario

URL_ESQUECI = "/api/v1/auth/esqueci-senha"
URL_REDEFINIR = "/api/v1/auth/redefinir-senha"
URL_LOGIN = "/api/v1/auth/login"


@pytest.fixture
def caixa_de_email(app):
    """Troca o enviador da app por um novo e devolve a lista de enviados."""
    anterior = app.extensions["enviador_email"]
    enviador = EnviadorEmailLog()
    app.extensions["enviador_email"] = enviador
    yield enviador.enviados
    app.extensions["enviador_email"] = anterior


def token_do(email):
    return email["corpo"].split("?redefinir=")[1].split()[0]


def test_fluxo_completo_esqueci_redefinir_e_entrar(client, caixa_de_email):
    usuario = criar_usuario(PAPEL_CLIENTE, email="ana@exemplo.com")

    resposta = client.post(URL_ESQUECI, json={"email": "  ANA@exemplo.com "})
    assert resposta.status_code == 202
    assert len(caixa_de_email) == 1
    assert caixa_de_email[0]["para"] == usuario.email

    resposta = client.post(
        URL_REDEFINIR,
        json={"token": token_do(caixa_de_email[0]), "senha": "senha-nova-123"},
    )
    assert resposta.status_code == 200

    antiga = client.post(URL_LOGIN, json={"email": usuario.email, "senha": "senha-boa-123"})
    nova = client.post(URL_LOGIN, json={"email": usuario.email, "senha": "senha-nova-123"})
    assert antiga.status_code == 401
    assert nova.status_code == 200


def test_email_inexistente_recebe_a_mesma_resposta(client, caixa_de_email):
    criar_usuario(PAPEL_CLIENTE, email="ana@exemplo.com")

    existe = client.post(URL_ESQUECI, json={"email": "ana@exemplo.com"})
    nao_existe = client.post(URL_ESQUECI, json={"email": "ninguem@exemplo.com"})

    assert existe.status_code == nao_existe.status_code == 202
    assert existe.get_json() == nao_existe.get_json()
    assert len(caixa_de_email) == 1


def test_link_usado_nao_serve_de_novo(client, caixa_de_email):
    criar_usuario(PAPEL_CLIENTE, email="ana@exemplo.com")
    client.post(URL_ESQUECI, json={"email": "ana@exemplo.com"})
    token = token_do(caixa_de_email[0])

    primeira = client.post(URL_REDEFINIR, json={"token": token, "senha": "senha-nova-123"})
    segunda = client.post(URL_REDEFINIR, json={"token": token, "senha": "outra-senha-456"})

    assert primeira.status_code == 200
    assert segunda.status_code == 422
    assert segunda.get_json()["erro"]["codigo"] == "REGRA_VIOLADA"


def test_token_invalido_da_422(client):
    resposta = client.post(URL_REDEFINIR, json={"token": "lixo", "senha": "senha-nova-123"})

    assert resposta.status_code == 422
    assert resposta.get_json()["erro"]["codigo"] == "REGRA_VIOLADA"


@pytest.mark.parametrize(
    "corpo, campo",
    [
        ({"token": "x", "senha": "curta"}, "senha"),
        ({"token": "x", "senha": "á" * 40}, "senha"),
        ({"senha": "senha-nova-123"}, "token"),
    ],
)
def test_redefinir_valida_entrada(client, corpo, campo):
    resposta = client.post(URL_REDEFINIR, json=corpo)

    assert resposta.status_code == 422
    assert campo in resposta.get_json()["erro"]["campos"]


def test_esqueci_com_email_malformado_da_422(client):
    resposta = client.post(URL_ESQUECI, json={"email": "nao-e-email"})

    assert resposta.status_code == 422
    assert "email" in resposta.get_json()["erro"]["campos"]
