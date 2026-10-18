from flask import Blueprint

blueprint_inicial = Blueprint("api_v1", __name__, url_prefix="/api/v1")

# Registrar o filho depois que o pai for para a app nao da erro: as rotas
# simplesmente nao existem.
from app.api.v1.agendamentos import blueprint_agendamentos  # noqa: E402
from app.api.v1.auth import blueprint_auth  # noqa: E402
from app.api.v1.clientes import blueprint_clientes  # noqa: E402
from app.api.v1.servicos import blueprint_servicos  # noqa: E402

blueprint_inicial.register_blueprint(blueprint_auth)
blueprint_inicial.register_blueprint(blueprint_clientes)
blueprint_inicial.register_blueprint(blueprint_servicos)
blueprint_inicial.register_blueprint(blueprint_agendamentos)
