import os
from flask import Flask
from app.config import configuracoes
from app.extensions import db, migrate, jwt, cors
from app.api.v1 import blueprint_inicial
from app.api.health import blueprint_health
from app.core.error_handlers import registrar_error_handlers

def create_app():
    app = Flask(__name__)
    nome_config = os.environ.get("APP_ENV", "dev")
    app.config.from_object(configuracoes[nome_config]())
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    app.register_blueprint(blueprint_inicial)
    app.register_blueprint(blueprint_health)
    registrar_error_handlers(app)

    return app
