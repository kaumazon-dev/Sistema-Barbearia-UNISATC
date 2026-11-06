from app.extensions import db
from app.models.servico import Servico
from app.repositories.base_repository import BaseRepository


class ServicoRepository(BaseRepository):
    def __init__(self):
        super().__init__(Servico)

    def listar(self, ativo=None):
        consulta = db.select(self.model).order_by(self.model.nome, self.model.id)
        if ativo is not None:
            consulta = consulta.where(self.model.ativo == ativo)
        return db.session.execute(consulta).scalars().all()

    def buscar_por_ids(self, ids):
        consulta = db.select(self.model).where(self.model.id.in_(ids))
        return db.session.execute(consulta).scalars().all()
