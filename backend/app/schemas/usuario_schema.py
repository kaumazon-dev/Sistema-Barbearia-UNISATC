from marshmallow import (
    EXCLUDE,
    Schema,
    ValidationError,
    fields,
    pre_load,
    validate,
    validates,
)

from app.core.security import LIMITE_BYTES_SENHA
from app.models.usuario import PAPEIS


def _limpar_entrada(dados):
    if not isinstance(dados, dict):
        return dados
    dados = dict(dados)
    if isinstance(dados.get("email"), str):
        dados["email"] = dados["email"].strip().lower()
    if isinstance(dados.get("nome"), str):
        dados["nome"] = dados["nome"].strip()
    return dados


class UsuarioCadastroSchema(Schema):
    # Sem o campo papel de proposito: se ele viesse no corpo da requisicao,
    # qualquer pessoa se cadastraria como admin.
    nome = fields.String(required=True, validate=validate.Length(min=3, max=120))
    email = fields.Email(required=True, validate=validate.Length(max=160))
    senha = fields.String(
        required=True, load_only=True, validate=validate.Length(min=8)
    )
    telefone = fields.String(
        required=False, allow_none=True, validate=validate.Length(max=20)
    )

    @pre_load
    def normalizar(self, dados, **kwargs):
        return _limpar_entrada(dados)

    @validates("senha")
    def validar_tamanho_em_bytes(self, senha, **kwargs):
        if len(senha.encode("utf-8")) > LIMITE_BYTES_SENHA:
            raise ValidationError(
                f"A senha nao pode passar de {LIMITE_BYTES_SENHA} bytes."
            )


class LoginSchema(Schema):
    email = fields.Email(required=True)
    senha = fields.String(required=True, load_only=True)

    @pre_load
    def normalizar(self, dados, **kwargs):
        return _limpar_entrada(dados)


class UsuarioSchema(Schema):
    # Lista de permissao, nao de exclusao: campo novo no model so aparece na
    # resposta se for escrito aqui.
    id = fields.Integer()
    nome = fields.String()
    email = fields.String()
    telefone = fields.String()
    papel = fields.String()
    ativo = fields.Boolean()
    criado_em = fields.DateTime()


class UsuarioFiltroSchema(Schema):
    """Filtros de GET /auth/usuarios.

    Sem o OneOf, um papel que nao existe no enum chega ao Postgres e vira 500.
    """

    class Meta:
        unknown = EXCLUDE

    papel = fields.String(
        required=False, load_default=None, validate=validate.OneOf(PAPEIS)
    )

    @pre_load
    def ignorar_filtro_vazio(self, dados, **kwargs):
        if isinstance(dados, dict) and not dados.get("papel"):
            return {chave: valor for chave, valor in dados.items() if chave != "papel"}
        return dados
