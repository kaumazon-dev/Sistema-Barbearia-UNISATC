import os

from flask_jwt_extended import create_access_token

from app.core.security import gerar_hash
from app.extensions import db
from app.models.usuario import Usuario


def criar_usuario(papel, email=None, nome="Fulano de Tal", telefone=None, ativo=True):
    usuario = Usuario(
        nome=nome,
        email=email or f"{papel}-{os.urandom(4).hex()}@exemplo.com",
        senha_hash=gerar_hash("senha-boa-123"),
        telefone=telefone,
        papel=papel,
        ativo=ativo,
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario


def cabecalho_de(usuario):
    token = create_access_token(
        identity=str(usuario.id), additional_claims={"papel": usuario.papel}
    )
    return {"Authorization": f"Bearer {token}"}
