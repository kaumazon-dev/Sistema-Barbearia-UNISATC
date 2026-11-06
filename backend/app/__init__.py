import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from app.config import configuracoes
from app.extensions import db, migrate, jwt, cors, limiter
from app.api.v1 import blueprint_inicial
from app.api.health import blueprint_health
from app.core.email import criar_enviador_email
from app.core.error_handlers import registrar_error_handlers, registrar_jwt_handlers
from app import models  # noqa: F401

def create_app():
    app = Flask(__name__)
    nome_config = os.environ.get("APP_ENV", "dev")
    app.config.from_object(configuracoes[nome_config]())
    proxies = app.config["PROXIES_CONFIAVEIS"]
    if proxies:
        # Atras de proxy, request.remote_addr e o IP do proxy, nao do cliente:
        # todo mundo dividiria o mesmo limite. O ProxyFix le o IP real do
        # X-Forwarded-For, confiando so nos ultimos N saltos (os nossos
        # proxies). Confiar em mais do que existe deixa o cliente forjar o IP.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=proxies)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, origins=app.config["CORS_ORIGINS"])
    limiter.init_app(app)
    app.register_blueprint(blueprint_inicial)
    app.register_blueprint(blueprint_health)
    registrar_error_handlers(app)
    registrar_jwt_handlers(jwt)
    # Um enviador por app. Os testes trocam este objeto para ler o e-mail.
    app.extensions["enviador_email"] = criar_enviador_email(app.config)

    return app
