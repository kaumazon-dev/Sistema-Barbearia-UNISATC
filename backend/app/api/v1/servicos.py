from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt

from app.api.decoradores import rota_protegida
from app.core.exceptions import NaoEncontrado
from app.models.usuario import PAPEL_ADMIN
from app.repositories.servico_repository import ServicoRepository
from app.schemas.servico_schema import (
    ServicoAtualizacaoSchema,
    ServicoCadastroSchema,
    ServicoFiltroSchema,
    ServicoSchema,
)
from app.services.servico_service import ServicoService

blueprint_servicos = Blueprint("servicos", __name__, url_prefix="/servicos")

schema_cadastro = ServicoCadastroSchema()
schema_atualizacao = ServicoAtualizacaoSchema()
schema_filtro = ServicoFiltroSchema()
schema_servico = ServicoSchema()
schema_lista_servicos = ServicoSchema(many=True)


def obter_servico():
    return ServicoService(ServicoRepository())


def _logado_e_admin():
    return get_jwt().get("papel") == PAPEL_ADMIN


# Leitura aberta a qualquer papel: o cliente escolhe servicos ao marcar horario.
# Quem nao e admin so enxerga servico ativo.
@blueprint_servicos.route("", methods=["GET"])
@rota_protegida()
def listar():
    filtros = schema_filtro.load(request.args.to_dict())
    ativo = filtros["ativo"] if _logado_e_admin() else True
    return jsonify(schema_lista_servicos.dump(obter_servico().listar(ativo)))


@blueprint_servicos.route("/<int:servico_id>", methods=["GET"])
@rota_protegida()
def detalhar(servico_id):
    servico = obter_servico().buscar(servico_id)
    if not servico.ativo and not _logado_e_admin():
        raise NaoEncontrado(f"Serviço {servico_id} não existe.")
    return jsonify(schema_servico.dump(servico))


@blueprint_servicos.route("", methods=["POST"])
@rota_protegida(PAPEL_ADMIN)
def cadastrar():
    dados = schema_cadastro.load(request.get_json())
    servico = obter_servico().cadastrar(dados)
    return jsonify(schema_servico.dump(servico)), 201


@blueprint_servicos.route("/<int:servico_id>", methods=["PUT"])
@rota_protegida(PAPEL_ADMIN)
def atualizar(servico_id):
    dados = schema_atualizacao.load(request.get_json(), partial=True)
    servico = obter_servico().atualizar(servico_id, dados)
    return jsonify(schema_servico.dump(servico))


@blueprint_servicos.route("/<int:servico_id>", methods=["DELETE"])
@rota_protegida(PAPEL_ADMIN)
def desativar(servico_id):
    # Exclusao logica: agendamentos antigos continuam apontando para ele.
    obter_servico().desativar(servico_id)
    return "", 204
