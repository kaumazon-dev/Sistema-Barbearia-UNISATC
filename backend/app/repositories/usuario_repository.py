from app.extensions import db
from app.models.usuario import Usuario
from app.repositories.base_repository import BaseRepository


class UsuarioRepository(BaseRepository):
    def __init__(self):
        super().__init__(Usuario)

    def buscar_por_email(self, email):
        consulta = db.select(self.model).where(self.model.email == email)
        return db.session.execute(consulta).scalar_one_or_none()

    def listar_por_papel(self, papel):
        consulta = db.select(self.model).where(self.model.papel == papel)
        return db.session.execute(consulta).scalars().all()

    def desfazer(self):
        db.session.rollback()
