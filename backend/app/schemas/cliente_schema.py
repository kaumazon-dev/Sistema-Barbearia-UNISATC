from marshmallow import Schema, fields, pre_load, validate

from app.schemas.paginacao_schema import PaginacaoSchema
from app.schemas.usuario_schema import UsuarioCadastroSchema, limpar_entrada

# Cadastro de cliente pelo admin tem exatamente as regras do cadastro publico:
# nome, e-mail, senha e telefone, sem papel no corpo.
ClienteCadastroSchema = UsuarioCadastroSchema


class ClienteAtualizacaoSchema(Schema):
    """Corpo do PUT /clientes/<id>. Todos os campos sao opcionais.

    Senha e papel ficam de fora de proposito: campo desconhecido vira 422.
    """

    nome = fields.String(validate=validate.Length(min=3, max=120))
    email = fields.Email(validate=validate.Length(max=160))
    telefone = fields.String(allow_none=True, validate=validate.Length(max=20))
    ativo = fields.Boolean()

    @pre_load
    def normalizar(self, dados, **kwargs):
        return limpar_entrada(dados)


class ClienteFiltroSchema(PaginacaoSchema):
    busca = fields.String(load_default=None, validate=validate.Length(max=120))
    ativo = fields.Boolean(load_default=None)

    @pre_load
    def limpar_busca(self, dados, **kwargs):
        if isinstance(dados, dict) and isinstance(dados.get("busca"), str):
            dados = dict(dados)
            dados["busca"] = dados["busca"].strip()
        return dados
