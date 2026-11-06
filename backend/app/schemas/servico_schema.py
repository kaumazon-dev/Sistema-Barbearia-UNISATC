from decimal import Decimal

from marshmallow import (
    EXCLUDE,
    Schema,
    ValidationError,
    fields,
    pre_load,
    validate,
    validates,
)

from app.schemas.paginacao_schema import descartar_vazios

DURACAO_MAXIMA_MINUTOS = 480
PRECO_MAXIMO = Decimal("99999999.99")  # limite do Numeric(10, 2)
CENTAVO = Decimal("0.01")


def _limpar_nome(dados):
    if isinstance(dados, dict) and isinstance(dados.get("nome"), str):
        dados = dict(dados)
        dados["nome"] = dados["nome"].strip()
    return dados


class ServicoCadastroSchema(Schema):
    nome = fields.String(required=True, validate=validate.Length(min=2, max=120))
    # strict: 30.5 ou "30" sao recusados em vez de truncados.
    duracao_minutos = fields.Integer(
        required=True,
        strict=True,
        validate=validate.Range(min=1, max=DURACAO_MAXIMA_MINUTOS),
    )
    # Aceita numero ou string ("35.90"); vira Decimal, nunca float (RNF09).
    preco = fields.Decimal(
        required=True, validate=validate.Range(min=Decimal("0"), max=PRECO_MAXIMO)
    )

    @pre_load
    def normalizar(self, dados, **kwargs):
        return _limpar_nome(dados)

    @validates("preco")
    def validar_centavos(self, preco, **kwargs):
        # Recusar em vez de arredondar: 35.999 provavelmente e erro de digitacao.
        if preco != preco.quantize(CENTAVO):
            raise ValidationError("O preço aceita no máximo 2 casas decimais.")


class ServicoAtualizacaoSchema(ServicoCadastroSchema):
    """Corpo do PUT /servicos/<id>. Carregar com partial=True."""

    ativo = fields.Boolean()


class ServicoSchema(Schema):
    id = fields.Integer()
    nome = fields.String()
    duracao_minutos = fields.Integer()
    # Sai como string ("35.00"): numero em JSON vira float no JavaScript.
    preco = fields.Decimal(places=2, as_string=True)
    ativo = fields.Boolean()


class ServicoFiltroSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    ativo = fields.Boolean(load_default=None)

    @pre_load
    def ignorar_vazios(self, dados, **kwargs):
        return descartar_vazios(dados)
