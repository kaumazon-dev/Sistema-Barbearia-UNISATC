import os
from datetime import timedelta

def normalizar_url_banco(url):
    if url is None:
        return 
    busca = "postgres://"
    if url.startswith(busca):
        return "postgresql://" + url[len(busca):]
    else:
        return url

def ler_minutos_expiracao_jwt(valor, padrao):
    try:
        minutos = int(valor)
    except (TypeError, ValueError):
        return padrao
    return minutos if minutos > 0 else padrao

def ler_origens_cors(valor):
    if not valor:
        return []
    return [origem.strip() for origem in valor.split(",") if origem.strip()]

def ler_inteiro_positivo(valor, padrao):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return padrao
    return numero if numero > 0 else padrao

def ler_inteiro_nao_negativo(valor, padrao):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return padrao
    return numero if numero >= 0 else padrao

def ler_booleano(valor, padrao):
    if valor is None or valor == "":
        return padrao
    return valor.strip().lower() in ("1", "true", "sim", "yes")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = normalizar_url_banco(os.environ.get("DATABASE_URL"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = ler_origens_cors(os.environ.get("CORS_ORIGINS"))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=ler_minutos_expiracao_jwt(os.environ.get("JWT_EXPIRA_MINUTOS"), 60)
    )

    # Esqueci minha senha. Sem MAIL_SERVIDOR o e-mail nao sai: o link e escrito
    # no log do Flask (bom para dev; em producao, configure o SMTP).
    MAIL_SERVIDOR = os.environ.get("MAIL_SERVIDOR")
    MAIL_PORTA = ler_inteiro_positivo(os.environ.get("MAIL_PORTA"), 587)
    MAIL_USUARIO = os.environ.get("MAIL_USUARIO")
    MAIL_SENHA = os.environ.get("MAIL_SENHA")
    MAIL_REMETENTE = os.environ.get("MAIL_REMETENTE")
    MAIL_USAR_TLS = ler_booleano(os.environ.get("MAIL_USAR_TLS"), True)
    # Endereco do front que aparece no link do e-mail.
    FRONTEND_URL = os.environ.get("FRONTEND_URL") or "http://localhost:5173"
    REDEFINIR_SENHA_EXPIRA_MINUTOS = ler_inteiro_positivo(
        os.environ.get("REDEFINIR_SENHA_EXPIRA_MINUTOS"), 30
    )

    # Limite de tentativas (Flask-Limiter le as chaves RATELIMIT_*).
    # memory:// conta em cada processo: com 2 workers do gunicorn o limite
    # real fica ate 2x maior. Para contar junto, use um Redis:
    # RATELIMIT_STORAGE_URI=redis://host:6379
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI") or "memory://"
    RATELIMIT_ENABLED = ler_booleano(os.environ.get("RATELIMIT_ATIVO"), True)
    # Manda Retry-After e X-RateLimit-* na resposta.
    RATELIMIT_HEADERS_ENABLED = True
    # Quantos proxies nossos ficam na frente da API (ver ProxyFix no create_app).
    PROXIES_CONFIAVEIS = ler_inteiro_nao_negativo(os.environ.get("PROXIES_CONFIAVEIS"), 0)

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    CORS_ORIGINS = ler_origens_cors(os.environ.get("CORS_ORIGINS")) or [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]

class TestConfig(Config):
    TESTING = True
    # Nos testes o e-mail nunca sai, mesmo com MAIL_SERVIDOR no ambiente.
    MAIL_SERVIDOR = None
    SQLALCHEMY_DATABASE_URI = normalizar_url_banco(os.environ.get("DATABASE_URL_TEST"))

class ProdConfig(Config):
    DEBUG = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    def __init__(self):
        super().__init__()

        if not self.SQLALCHEMY_DATABASE_URI:
            raise RuntimeError("Variavel SQLALCHEMY_DATABASE_URI com valor nulo")
        if not self.SECRET_KEY:
            raise RuntimeError("Variavel SECRET_KEY com valor nulo")
        if not self.JWT_SECRET_KEY:
            raise RuntimeError("Variavel JWT_SECRET_KEY com valor nulo")
        if not self.CORS_ORIGINS:
            raise RuntimeError("Variavel CORS_ORIGINS com valor nulo")
        if "*" in self.CORS_ORIGINS:
            raise RuntimeError("Variavel CORS_ORIGINS nao pode conter '*'")
        if not os.environ.get("FRONTEND_URL"):
            # O link do e-mail aponta para o front. Sem a variavel, usa a
            # primeira origem do CORS, que e o endereco do front no ar.
            self.FRONTEND_URL = self.CORS_ORIGINS[0]

configuracoes = {"dev": DevConfig, "prod":ProdConfig, "test":TestConfig}
