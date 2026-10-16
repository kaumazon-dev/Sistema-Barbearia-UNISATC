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

    def buscar_por_papel(self, papel, busca=None, ativo=None, pagina=1, por_pagina=20):
        """Lista paginada de um papel, com busca por nome ou telefone (RF08)."""
        consulta = db.select(self.model).where(self.model.papel == papel)
        if busca:
            # Os curingas do LIKE digitados pelo usuario viram texto literal.
            termo = "%" + _escapar_like(busca) + "%"
            consulta = consulta.where(
                db.or_(
                    self.model.nome.ilike(termo, escape="\\"),
                    self.model.telefone.ilike(termo, escape="\\"),
                )
            )
        if ativo is not None:
            consulta = consulta.where(self.model.ativo == ativo)
        consulta = consulta.order_by(self.model.nome, self.model.id)
        return self.paginar(consulta, pagina, por_pagina)


def _escapar_like(texto):
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
