from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from app.api.decoradores import rota_protegida, usuario_logado_id
from app.models.usuario import PAPEL_ADMIN
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario_schema import (
    LoginSchema,
    UsuarioCadastroSchema,
    UsuarioFiltroSchema,
    UsuarioSchema,
)
from app.services.auth_service import AuthService

blueprint_auth = Blueprint("auth", __name__, url_prefix="/auth")

schema_cadastro = UsuarioCadastroSchema()
schema_login = LoginSchema()
schema_usuario = UsuarioSchema()
schema_lista_usuarios = UsuarioSchema(many=True)
schema_filtro = UsuarioFiltroSchema()


def obter_servico():
    return AuthService(UsuarioRepository())


@blueprint_auth.route("/register", methods=["POST"])
def registrar():
    dados = schema_cadastro.load(request.get_json())
    usuario = obter_servico().cadastrar(dados)
    return jsonify(schema_usuario.dump(usuario)), 201


@blueprint_auth.route("/login", methods=["POST"])
def login():
    dados = schema_login.load(request.get_json())
    usuario = obter_servico().autenticar(dados["email"], dados["senha"])
    # O token nasce aqui, e nao no service: create_access_token depende da
    # configuracao da aplicacao.
    token = create_access_token(
        identity=str(usuario.id), additional_claims={"papel": usuario.papel}
    )
    return jsonify({"token": token, "usuario": schema_usuario.dump(usuario)})


@blueprint_auth.route("/me", methods=["GET"])
@rota_protegida()
def perfil():
    usuario = obter_servico().buscar_perfil(usuario_logado_id())
    return jsonify(schema_usuario.dump(usuario))


@blueprint_auth.route("/usuarios", methods=["GET"])
@rota_protegida(PAPEL_ADMIN)
def listar_usuarios():
    filtros = schema_filtro.load(request.args.to_dict())
    usuarios = obter_servico().listar_usuarios(filtros["papel"])
    return jsonify(schema_lista_usuarios.dump(usuarios))
