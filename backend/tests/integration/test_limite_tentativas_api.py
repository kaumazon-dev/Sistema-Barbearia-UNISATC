"""Rate limit das rotas publicas de autenticacao (Flask-Limiter)."""

from app.core.limites import MENSAGEM_LIMITE
from app.models.usuario import PAPEL_CLIENTE
from tests.integration.fabricas import criar_usuario

URL_LOGIN = "/api/v1/auth/login"
URL_ESQUECI = "/api/v1/auth/esqueci-senha"
URL_CADASTRO = "/api/v1/auth/register"


def test_esqueci_senha_bloqueia_o_quarto_pedido_do_mesmo_email(client):
    criar_usuario(PAPEL_CLIENTE, email="ana@exemplo.com")
    for _ in range(3):
        assert client.post(URL_ESQUECI, json={"email": "ana@exemplo.com"}).status_code == 202

    # Maiusculas e espacos contam como o mesmo e-mail.
    resposta = client.post(URL_ESQUECI, json={"email": " ANA@exemplo.com"})

    assert resposta.status_code == 429
    assert resposta.get_json() == {
        "erro": {"codigo": "MUITAS_TENTATIVAS", "mensagem": MENSAGEM_LIMITE}
    }
    assert int(resposta.headers["Retry-After"]) > 0


def test_limite_de_um_email_nao_afeta_outro(client):
    for _ in range(4):
        client.post(URL_ESQUECI, json={"email": "ana@exemplo.com"})

    resposta = client.post(URL_ESQUECI, json={"email": "bia@exemplo.com"})

    assert resposta.status_code == 202


def test_login_bloqueia_forca_bruta_na_mesma_conta(client):
    usuario = criar_usuario(PAPEL_CLIENTE, email="ana@exemplo.com")
    for _ in range(10):
        resposta = client.post(URL_LOGIN, json={"email": usuario.email, "senha": "chute-errado"})
        assert resposta.status_code == 401

    # Bloqueado mesmo com a senha certa: o contador e da conta, nao do acerto.
    resposta = client.post(URL_LOGIN, json={"email": usuario.email, "senha": "senha-boa-123"})

    assert resposta.status_code == 429


def test_cadastro_limita_por_ip(client):
    for i in range(10):
        client.post(
            URL_CADASTRO,
            json={"nome": "Fulano", "email": f"f{i}@exemplo.com", "senha": "senha-boa-123"},
        )

    resposta = client.post(
        URL_CADASTRO,
        json={"nome": "Fulano", "email": "f99@exemplo.com", "senha": "senha-boa-123"},
    )

    assert resposta.status_code == 429


def test_ip_real_vem_do_x_forwarded_for_quando_ha_proxy(app):
    """Com PROXIES_CONFIAVEIS=1 cada cliente atras do proxy tem o seu limite."""
    from werkzeug.middleware.proxy_fix import ProxyFix

    original = app.wsgi_app
    app.wsgi_app = ProxyFix(original, x_for=1)
    try:
        client = app.test_client()
        for i in range(10):
            client.post(
                URL_CADASTRO,
                json={"nome": "Fulano", "email": f"a{i}@exemplo.com", "senha": "senha-boa-123"},
                headers={"X-Forwarded-For": "200.0.0.1"},
            )
        bloqueado = client.post(
            URL_CADASTRO,
            json={"nome": "Fulano", "email": "a99@exemplo.com", "senha": "senha-boa-123"},
            headers={"X-Forwarded-For": "200.0.0.1"},
        )
        outro_cliente = client.post(
            URL_CADASTRO,
            json={"nome": "Fulano", "email": "b1@exemplo.com", "senha": "senha-boa-123"},
            headers={"X-Forwarded-For": "200.0.0.2"},
        )
    finally:
        app.wsgi_app = original

    assert bloqueado.status_code == 429
    assert outro_cliente.status_code == 201
