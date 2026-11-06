from sqlalchemy import func

from app.extensions import db

PAPEL_ADMIN = "admin"
PAPEL_BARBEIRO = "barbeiro"
PAPEL_CLIENTE = "cliente"
PAPEIS = (PAPEL_ADMIN, PAPEL_BARBEIRO, PAPEL_CLIENTE)


class Usuario(db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20))
    papel = db.Column(db.Enum(*PAPEIS, name="usuario_papel"), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))
    criado_em = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    def __repr__(self):
        return f"<Usuario {self.id} {self.email} {self.papel}>"
