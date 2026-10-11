from flask import Blueprint

blueprint_inicial = Blueprint("api_v1", __name__, url_prefix="/api/v1")

# Registrar o filho depois que o pai for para a app nao da erro: as rotas
# simplesmente nao existem.
from app.api.v1.auth import blueprint_auth  # noqa: E402

blueprint_inicial.register_blueprint(blueprint_auth)
