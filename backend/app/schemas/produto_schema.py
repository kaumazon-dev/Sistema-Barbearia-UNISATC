from decimal import Decimal

from marshmallow import (
    EXCLUDE,
    Schema,
    ValidationError,
    fields,
    pre_load,
    validate,
)

from app.models.produto import TIPOS_MOVIMENTACAO, UNIDADES
from app.schemas.agendamento_schema import DataHoraComFuso, PessoaResumoSchema
from app.schemas.paginacao_schema import PaginacaoSchema, descartar_vazios

QUANTIDADE_MAXIMA = Decimal("99999999.99")  # limite do Numeric(10, 2)
CENTAVO = Decimal("0.01")
TAMANHO_MAXIMO_MOTIVO = 160


def _no_maximo_duas_casas(valor):
    # Recusar em vez de arredondar: 1.555 provavelmente e erro de digitacao.
    if valor != valor.quantize(CENTAVO):
        raise ValidationError("Aceita no máximo 2 casas decimais.")


def _limpar_texto(dados, campo, vazio_vira_none=False):
    if isinstance(dados, dict) and isinstance(dados.get(campo), str):
        dados = dict(dados)
        dados[campo] = dados[campo].strip()
        if vazio_vira_none and not dados[campo]:
            dados[campo] = None
    return dados


class ProdutoCadastroSchema(Schema):
    """Sem quantidade_atual de proposito: campo desconhecido vira 422. O estoque
    inicial entra por POST /produtos/<id>/entradas (RN04).
    """

    nome = fields.String(required=True, validate=validate.Length(min=2, max=120))
    unidade = fields.String(required=True, validate=validate.OneOf(UNIDADES))
    estoque_minimo = fields.Decimal(
        load_default=Decimal("0"),
        validate=[
            validate.Range(min=Decimal("0"), max=QUANTIDADE_MAXIMA),
            _no_maximo_duas_casas,
        ],
    )

    @pre_load
    def normalizar(self, dados, **kwargs):
        return _limpar_texto(dados, "nome")


class ProdutoAtualizacaoSchema(ProdutoCadastroSchema):
    """Corpo do PUT /produtos/<id>. Carregar com partial=True."""

    # Sem load_default: no PUT, campo ausente nao pode virar zero.
    estoque_minimo = fields.Decimal(
        validate=[
            validate.Range(min=Decimal("0"), max=QUANTIDADE_MAXIMA),
            _no_maximo_duas_casas,
        ],
    )
    ativo = fields.Boolean()


class ProdutoFiltroSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    ativo = fields.Boolean(load_default=None)

    @pre_load
    def ignorar_vazios(self, dados, **kwargs):
        return descartar_vazios(dados)


class ProdutoSchema(Schema):
    id = fields.Integer()
    nome = fields.String()
    unidade = fields.String()
    # Sai como string ("10.50"): numero em JSON vira float no JavaScript.
    quantidade_atual = fields.Decimal(places=2, as_string=True)
    estoque_minimo = fields.Decimal(places=2, as_string=True)
    em_falta = fields.Boolean()
    ativo = fields.Boolean()


class MovimentacaoCriacaoSchema(Schema):
    """Corpo de POST /produtos/<id>/entradas e /saidas. O tipo vem da rota."""

    # Sempre positiva: o sinal vem do tipo.
    quantidade = fields.Decimal(
        required=True,
        validate=[
            validate.Range(
                min=Decimal("0"), min_inclusive=False, max=QUANTIDADE_MAXIMA
            ),
            _no_maximo_duas_casas,
        ],
    )
    motivo = fields.String(
        allow_none=True, validate=validate.Length(max=TAMANHO_MAXIMO_MOTIVO)
    )

    @pre_load
    def normalizar(self, dados, **kwargs):
        return _limpar_texto(dados, "motivo", vazio_vira_none=True)


class MovimentacaoFiltroSchema(PaginacaoSchema):
    tipo = fields.String(load_default=None, validate=validate.OneOf(TIPOS_MOVIMENTACAO))


class MovimentacaoSchema(Schema):
    id = fields.Integer()
    tipo = fields.String()
    quantidade = fields.Decimal(places=2, as_string=True)
    motivo = fields.String()
    usuario = fields.Nested(PessoaResumoSchema)
    criado_em = DataHoraComFuso()
    # Saldo ja atualizado, para o front redesenhar a tela sem outro GET. A
    # listagem do historico exclui este campo: ali seria o saldo de hoje, nao
    # o da epoca da movimentacao.
    produto = fields.Nested(ProdutoSchema)
