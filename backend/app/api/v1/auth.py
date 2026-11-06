from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token

from app.api.decoradores import rota_protegida, usuario_logado_id
from app.core.limites import (
    LIMITE_CADASTRO_IP,
    LIMITE_ESQUECI_EMAIL,
    LIMITE_ESQUECI_IP,
    LIMITE_LOGIN_EMAIL,
    LIMITE_LOGIN_IP,
    LIMITE_REDEFINIR_IP,
    chave_por_email,
)
from app.core.security import TokenRedefinicaoSenha
from app.extensions import limiter
from app.models.usuario import PAPEL_ADMIN
from app.repositories.agendamento_repository import AgendamentoRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario_schema import (
    AlterarPapelSchema,
    EsqueciSenhaSchema,
    LoginSchema,
    RedefinirSenhaSchema,
    UsuarioCadastroSchema,
    UsuarioFiltroSchema,
    UsuarioResumoSchema,
    UsuarioSchema,
)
from app.services.auth_service import AuthService
from app.services.recuperacao_senha_service import (
    MENSAGEM_SOLICITACAO,
    RecuperacaoSenhaService,
)
from app.services.usuario_service import UsuarioService

blueprint_auth = Blueprint("auth", __name__, url_prefix="/auth")

schema_cadastro = UsuarioCadastroSchema()
schema_login = LoginSchema()
schema_usuario = UsuarioSchema()
schema_lista_usuarios = UsuarioSchema(many=True)
schema_filtro = UsuarioFiltroSchema()
schema_lista_resumo = UsuarioResumoSchema(many=True)
schema_alterar_papel = AlterarPapelSchema()
schema_esqueci_senha = EsqueciSenhaSchema()
schema_redefinir_senha = RedefinirSenhaSchema()


def obter_servico():
    return AuthService(UsuarioRepository())


def obter_servico_recuperacao():
    config = current_app.config
    tokens = TokenRedefinicaoSenha(
        config["SECRET_KEY"], config["REDEFINIR_SENHA_EXPIRA_MINUTOS"] * 60
    )
    return RecuperacaoSenhaService(
        UsuarioRepository(),
        tokens,
        current_app.extensions["enviador_email"],
        config["FRONTEND_URL"],
    )


def obter_servico_usuarios():
    return UsuarioService(UsuarioRepository(), AgendamentoRepository())


@blueprint_auth.route("/register", methods=["POST"])
@limiter.limit(LIMITE_CADASTRO_IP)
def registrar():
    dados = schema_cadastro.load(request.get_json())
    usuario = obter_servico().cadastrar(dados)
    return jsonify(schema_usuario.dump(usuario)), 201


@blueprint_auth.route("/login", methods=["POST"])
@limiter.limit(LIMITE_LOGIN_IP)
@limiter.limit(LIMITE_LOGIN_EMAIL, key_func=chave_por_email)
def login():
    dados = schema_login.load(request.get_json())
    usuario = obter_servico().autenticar(dados["email"], dados["senha"])
    # O token nasce aqui, e nao no service: create_access_token depende da
    # configuracao da aplicacao.
    token = create_access_token(
        identity=str(usuario.id), additional_claims={"papel": usuario.papel}
    )
    return jsonify({"token": token, "usuario": schema_usuario.dump(usuario)})


@blueprint_auth.route("/esqueci-senha", methods=["POST"])
@limiter.limit(LIMITE_ESQUECI_IP)
@limiter.limit(LIMITE_ESQUECI_EMAIL, key_func=chave_por_email)
def esqueci_senha():
    dados = schema_esqueci_senha.load(request.get_json())
    obter_servico_recuperacao().solicitar(dados["email"])
    # Sempre 202 e a mesma mensagem, exista o e-mail ou nao.
    return jsonify({"mensagem": MENSAGEM_SOLICITACAO}), 202


@blueprint_auth.route("/redefinir-senha", methods=["POST"])
@limiter.limit(LIMITE_REDEFINIR_IP)
def redefinir_senha():
    dados = schema_redefinir_senha.load(request.get_json())
    obter_servico_recuperacao().redefinir(dados["token"], dados["senha"])
    return jsonify({"mensagem": "Senha redefinida. Entre com a senha nova."})


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


@blueprint_auth.route("/usuarios/<int:usuario_id>/papel", methods=["PATCH"])
@rota_protegida(PAPEL_ADMIN)
def alterar_papel(usuario_id):
    dados = schema_alterar_papel.load(request.get_json())
    usuario = obter_servico_usuarios().alterar_papel(
        usuario_id, dados["papel"], admin_id=usuario_logado_id()
    )
    return jsonify(schema_usuario.dump(usuario))


@blueprint_auth.route("/barbeiros", methods=["GET"])
@rota_protegida()
def listar_barbeiros():
    barbeiros = obter_servico().listar_barbeiros()
    return jsonify(schema_lista_resumo.dump(barbeiros))
