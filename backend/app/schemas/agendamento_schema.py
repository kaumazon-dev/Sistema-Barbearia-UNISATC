from marshmallow import Schema, ValidationError, fields, pre_load, validate

from app.core.fuso import FUSO_BARBEARIA
from app.models.agendamento import STATUS
from app.schemas.paginacao_schema import PaginacaoSchema

MAXIMO_SERVICOS = 10
TAMANHO_MAXIMO_OBSERVACAO = 500


class DataHoraComFuso(fields.AwareDateTime):
    """Entra em ISO 8601 com fuso obrigatorio; sai no fuso da barbearia.

    "2026-10-20T14:30:00" (sem fuso) e recusado: nao da para saber se e
    horario de Brasilia ou UTC. Use "2026-10-20T14:30:00-03:00" ou "...Z".
    """

    def __init__(self, **kwargs):
        super().__init__(format="iso", **kwargs)

    def _serialize(self, valor, atributo, objeto, **kwargs):
        if valor is None:
            return None
        return valor.astimezone(FUSO_BARBEARIA).isoformat()

    def _deserialize(self, valor, atributo, dados, **kwargs):
        data_hora = super()._deserialize(valor, atributo, dados, **kwargs)
        # Recusar em vez de arredondar: agenda trabalha em minutos cheios.
        if data_hora.second or data_hora.microsecond:
            raise ValidationError("Informe o horário sem segundos.")
        return data_hora


def _limpar_observacao(dados):
    if isinstance(dados, dict) and isinstance(dados.get("observacao"), str):
        dados = dict(dados)
        dados["observacao"] = dados["observacao"].strip() or None
    return dados


class AgendamentoCriacaoSchema(Schema):
    # Obrigatorio para admin e barbeiro; para cliente e ignorado (vem do token).
    # A rota confere, porque depende de quem esta logado.
    cliente_id = fields.Integer(strict=True, load_default=None)
    barbeiro_id = fields.Integer(required=True, strict=True)
    inicio = DataHoraComFuso(required=True)
    servico_ids = fields.List(
        fields.Integer(strict=True),
        required=True,
        validate=validate.Length(min=1, max=MAXIMO_SERVICOS),
    )
    observacao = fields.String(
        allow_none=True, validate=validate.Length(max=TAMANHO_MAXIMO_OBSERVACAO)
    )

    @pre_load
    def normalizar(self, dados, **kwargs):
        return _limpar_observacao(dados)


class AgendamentoRemarcacaoSchema(Schema):
    inicio = DataHoraComFuso(required=True)
    barbeiro_id = fields.Integer(strict=True)


class AgendamentoFiltroSchema(PaginacaoSchema):
    # Dia no fuso da barbearia: 2026-10-20 vai de 00:00 a 24:00 de Brasilia.
    dia = fields.Date(load_default=None)
    barbeiro_id = fields.Integer(load_default=None)
    cliente_id = fields.Integer(load_default=None)
    status = fields.String(load_default=None, validate=validate.OneOf(STATUS))


class PessoaResumoSchema(Schema):
    id = fields.Integer()
    nome = fields.String()


class ItemAgendamentoSchema(Schema):
    servico_id = fields.Integer()
    nome = fields.String(attribute="servico.nome")
    # Preco congelado na marcacao (RN02). Sai como string, igual ao servico.
    preco_cobrado = fields.Decimal(places=2, as_string=True)


class AgendamentoSchema(Schema):
    id = fields.Integer()
    cliente = fields.Nested(PessoaResumoSchema)
    barbeiro = fields.Nested(PessoaResumoSchema)
    inicio = DataHoraComFuso()
    fim = DataHoraComFuso()
    status = fields.String()
    observacao = fields.String()
    servicos = fields.Nested(ItemAgendamentoSchema, many=True, attribute="itens")
    total = fields.Method("somar_total")
    criado_em = DataHoraComFuso()

    def somar_total(self, agendamento):
        return f"{sum(item.preco_cobrado for item in agendamento.itens):.2f}"
