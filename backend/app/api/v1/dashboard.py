from flask import Blueprint, jsonify, request

from app.api.decoradores import rota_protegida
from app.models.usuario import PAPEL_ADMIN
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard_schema import (
    AtendimentosSchema,
    CancelamentoSchema,
    FaturamentoSchema,
    PeriodoFiltroSchema,
    RankingFiltroSchema,
    RankingSchema,
    SerieFiltroSchema,
)
from app.services.dashboard_service import DashboardService

blueprint_dashboard = Blueprint("dashboard", __name__, url_prefix="/dashboard")

schema_periodo_filtro = PeriodoFiltroSchema()
schema_serie_filtro = SerieFiltroSchema()
schema_ranking_filtro = RankingFiltroSchema()
schema_atendimentos = AtendimentosSchema()
schema_faturamento = FaturamentoSchema()
schema_ranking = RankingSchema()
schema_cancelamento = CancelamentoSchema()


def obter_servico():
    return DashboardService(DashboardRepository())


# Dashboard e area do admin. Produtos em falta (RF32) ficam em
# GET /produtos/em-falta, que ja existe e tambem e so do admin.
@blueprint_dashboard.route("/atendimentos", methods=["GET"])
@rota_protegida(PAPEL_ADMIN)
def atendimentos():
    filtros = schema_serie_filtro.load(request.args.to_dict())
    return jsonify(schema_atendimentos.dump(obter_servico().atendimentos(**filtros)))


@blueprint_dashboard.route("/faturamento", methods=["GET"])
@rota_protegida(PAPEL_ADMIN)
def faturamento():
    filtros = schema_serie_filtro.load(request.args.to_dict())
    return jsonify(schema_faturamento.dump(obter_servico().faturamento(**filtros)))


@blueprint_dashboard.route("/servicos-ranking", methods=["GET"])
@rota_protegida(PAPEL_ADMIN)
def ranking_servicos():
    filtros = schema_ranking_filtro.load(request.args.to_dict())
    return jsonify(schema_ranking.dump(obter_servico().ranking_servicos(**filtros)))


@blueprint_dashboard.route("/cancelamento", methods=["GET"])
@rota_protegida(PAPEL_ADMIN)
def cancelamento():
    filtros = schema_periodo_filtro.load(request.args.to_dict())
    return jsonify(schema_cancelamento.dump(obter_servico().cancelamento(**filtros)))
