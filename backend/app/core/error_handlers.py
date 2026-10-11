from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
from app.core.exceptions import (ErroNegocio, NaoEncontrado, RegraDeNegocioViolada, NaoAutorizada, AcessoNegado, Conflito)



STATUS_POR_EXCECAO = {NaoEncontrado: 404, RegraDeNegocioViolada: 422, NaoAutorizada: 401, AcessoNegado: 403, Conflito: 409}

def registrar_error_handlers(app):
    @app.errorhandler(ErroNegocio)
    def tratar_erro_negocio(erro):
        status = STATUS_POR_EXCECAO.get(type(erro), 400)
        corpo = {"erro": {"codigo": erro.codigo, "mensagem":erro.mensagem}}
        return corpo,status

    @app.errorhandler(ValidationError)
    def tratar_erro_validacao(erro):
        corpo = {
            "erro": {
                "codigo": "DADOS_INVALIDOS",
                "mensagem": "Dados de entrada inválidos.",
                "campos": erro.messages,
            }
        }
        return corpo, 422

    @app.errorhandler(HTTPException)
    def tratar_erro_http(erro):
        corpo = {"erro": {"codigo": erro.name.upper().replace(" ", "_"), "mensagem": erro.description}}
        return corpo, erro.code

    @app.errorhandler(Exception)
    def tratar_erro_generico(erro):
        app.logger.exception("Erro não tratado")
        corpo = {"erro": {"codigo": "ERRO_INTERNO", "mensagem": "Erro interno do servidor."}}
        return corpo, 500


def _corpo_jwt(mensagem):
    return {"erro": {"codigo": NaoAutorizada.codigo, "mensagem": mensagem}}


def registrar_jwt_handlers(jwt):
    """Faz os erros de token seguirem o mesmo envelope de erro da API.

    Sem isto o flask-jwt-extended responde no formato dele ({"msg": "..."}), e o
    front precisaria de um tratamento especial só para token.
    """

    @jwt.unauthorized_loader
    def tratar_token_ausente(motivo):
        return _corpo_jwt("Token de acesso ausente."), 401

    @jwt.invalid_token_loader
    def tratar_token_invalido(motivo):
        return _corpo_jwt("Token de acesso inválido."), 401

    @jwt.expired_token_loader
    def tratar_token_expirado(cabecalho, conteudo):
        return _corpo_jwt("Token de acesso expirado."), 401

    @jwt.revoked_token_loader
    def tratar_token_revogado(cabecalho, conteudo):
        return _corpo_jwt("Token de acesso revogado."), 401
