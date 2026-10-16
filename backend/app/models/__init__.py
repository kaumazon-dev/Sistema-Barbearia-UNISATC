# Model novo precisa ser importado aqui: o Alembic nao varre a pasta, e so
# enxerga as classes que entraram em db.metadata.
from app.models.servico import Servico
from app.models.usuario import Usuario

__all__ = ["Servico", "Usuario"]
