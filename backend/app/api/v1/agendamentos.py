from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt
from marshmallow import ValidationError

from app.api.decoradores import rota_protegida, usuario_logado_id
from app.models.usuario import PAPEL_ADMIN, PAPEL_BARBEIRO, PAPEL_CLIENTE
from app.repositories.agendamento_repository import AgendamentoRepository
from app.repositories.servico_repository import ServicoRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.agendamento_schema import (
    AgendamentoCriacaoSchema,
    AgendamentoFiltroSchema,
    AgendamentoRemarcacaoSchema,
    AgendamentoSchema,
)
from app.schemas.paginacao_schema import montar_pagina
from app.services.agendamento_service import AgendamentoService
from app.services.servico_service import ServicoService

blueprint_agendamentos = Blueprint("agendamentos", __name__, url_prefix="/agendamentos")

schema_criacao = AgendamentoCriacaoSchema()
schema_remarcacao = AgendamentoRemarcacaoSchema()
schema_filtro = AgendamentoFiltroSchema()
schema_agendamento = AgendamentoSchema()
schema_lista_agendamentos = AgendamentoSchema(many=True)


def obter_servico():
    return AgendamentoService(
        AgendamentoRepository(),
        ServicoService(ServicoRepository()),
        UsuarioRepository(),
    )


def _logado():
    """(usuario_id, papel) do token. O service recebe por argumento e nunca
    le o token sozinho.
    """
    return usuario_logado_id(), get_jwt().get("papel")


# Cliente usa as mesmas rotas, mas so enxerga e mexe no que e dele (RF21).
@blueprint_agendamentos.route("", methods=["GET"])
@rota_protegida()
def listar():
    filtros = schema_filtro.load(request.args.to_dict())
    agendamentos, total = obter_servico().listar(*_logado(), **filtros)
    return jsonify(
        montar_pagina(
            schema_lista_agendamentos.dump(agendamentos),
            total,
            filtros["pagina"],
            filtros["por_pagina"],
        )
    )


@blueprint_agendamentos.route("/<int:agendamento_id>", methods=["GET"])
@rota_protegida()
def detalhar(agendamento_id):
    agendamento = obter_servico().buscar(agendamento_id, *_logado())
    return jsonify(schema_agendamento.dump(agendamento))


@blueprint_agendamentos.route("", methods=["POST"])
@rota_protegida()
def criar():
    dados = schema_criacao.load(request.get_json())
    usuario_id, papel = _logado()
    if papel != PAPEL_CLIENTE and dados["cliente_id"] is None:
        raise ValidationError(
            {"cliente_id": ["Obrigatório para admin e barbeiro."]}
        )
    agendamento = obter_servico().criar(dados, usuario_id, papel)
    return jsonify(schema_agendamento.dump(agendamento)), 201


@blueprint_agendamentos.route("/<int:agendamento_id>", methods=["PATCH"])
@rota_protegida()
def remarcar(agendamento_id):
    dados = schema_remarcacao.load(request.get_json())
    agendamento = obter_servico().remarcar(agendamento_id, dados, *_logado())
    return jsonify(schema_agendamento.dump(agendamento))


@blueprint_agendamentos.route("/<int:agendamento_id>/cancelar", methods=["POST"])
@rota_protegida()
def cancelar(agendamento_id):
    # Muda o status e mantem o registro (RF19).
    agendamento = obter_servico().cancelar(agendamento_id, *_logado())
    return jsonify(schema_agendamento.dump(agendamento))


@blueprint_agendamentos.route("/<int:agendamento_id>/concluir", methods=["POST"])
@rota_protegida(PAPEL_ADMIN, PAPEL_BARBEIRO)
def concluir(agendamento_id):
    agendamento = obter_servico().concluir(agendamento_id, *_logado())
    return jsonify(schema_agendamento.dump(agendamento))
