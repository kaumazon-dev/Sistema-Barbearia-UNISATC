from marshmallow import (
    EXCLUDE,
    Schema,
    ValidationError,
    fields,
    pre_load,
    validate,
    validates_schema,
)

from app.schemas.paginacao_schema import descartar_vazios
from app.services.dashboard_service import GRANULARIDADE_SEMANA, GRANULARIDADES

INTERVALO_MAXIMO_DIAS = 366
RANKING_PADRAO = 5
RANKING_MAXIMO = 20


class PeriodoFiltroSchema(Schema):
    """Dias no fuso da barbearia, com "ate" inclusivo: de=2026-10-01 e
    ate=2026-10-31 e o mes de outubro inteiro. Sem os dois, o service usa o mes
    atual.
    """

    class Meta:
        unknown = EXCLUDE

    de = fields.Date(load_default=None)
    ate = fields.Date(load_default=None)

    @pre_load
    def ignorar_vazios(self, dados, **kwargs):
        return descartar_vazios(dados)

    @validates_schema
    def validar_periodo(self, dados, **kwargs):
        de, ate = dados.get("de"), dados.get("ate")
        # Um so dos dois e ambiguo: "desde 01/10" ate quando?
        if de is None and ate is not None:
            raise ValidationError("Informe junto com ate.", "de")
        if ate is None and de is not None:
            raise ValidationError("Informe junto com de.", "ate")
        if de is None:
            return
        if ate < de:
            raise ValidationError("Deve ser igual ou posterior a de.", "ate")
        if (ate - de).days >= INTERVALO_MAXIMO_DIAS:
            raise ValidationError(
                f"Intervalo máximo de {INTERVALO_MAXIMO_DIAS} dias.", "ate"
            )


class SerieFiltroSchema(PeriodoFiltroSchema):
    granularidade = fields.String(
        load_default=GRANULARIDADE_SEMANA, validate=validate.OneOf(GRANULARIDADES)
    )


class RankingFiltroSchema(PeriodoFiltroSchema):
    limite = fields.Integer(
        load_default=RANKING_PADRAO, validate=validate.Range(min=1, max=RANKING_MAXIMO)
    )


class PeriodoSchema(Schema):
    # Periodo efetivamente usado: com o padrao do mes atual, o front descobre
    # aqui quais datas foram aplicadas.
    de = fields.Date()
    ate = fields.Date()


class AtendimentosSchema(PeriodoSchema):
    granularidade = fields.String()
    labels = fields.List(fields.String())
    valores = fields.List(fields.Integer())


class FaturamentoSchema(AtendimentosSchema):
    # String com duas casas, como todo valor monetario da API (RNF09).
    valores = fields.List(fields.Decimal(places=2, as_string=True))


class RankingSchema(PeriodoSchema):
    labels = fields.List(fields.String())
    valores = fields.List(fields.Integer())
    receitas = fields.List(fields.Decimal(places=2, as_string=True))


class CancelamentoSchema(PeriodoSchema):
    concluidos = fields.Integer()
    cancelados = fields.Integer()
    total = fields.Integer()
    # Percentual, "13.31". null quando nao houve nenhum desfecho no periodo.
    taxa = fields.Decimal(places=2, as_string=True, allow_none=True)
    labels = fields.List(fields.String())
    valores = fields.List(fields.Integer())
