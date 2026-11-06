from flask import Blueprint, jsonify, request

from app.api.decoradores import rota_protegida
from app.models.usuario import PAPEL_ADMIN, PAPEL_BARBEIRO
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.cliente_schema import (
    ClienteAtualizacaoSchema,
    ClienteCadastroSchema,
    ClienteFiltroSchema,
)
from app.schemas.paginacao_schema import montar_pagina
from app.schemas.usuario_schema import UsuarioSchema
from app.services.cliente_service import ClienteService

blueprint_clientes = Blueprint("clientes", __name__, url_prefix="/clientes")

schema_cadastro = ClienteCadastroSchema()
schema_atualizacao = ClienteAtualizacaoSchema()
schema_filtro = ClienteFiltroSchema()
schema_cliente = UsuarioSchema()
schema_lista_clientes = UsuarioSchema(many=True)


def obter_servico():
    return ClienteService(UsuarioRepository())


# Barbeiro so le: precisa escolher o cliente ao marcar horario (Fase 4).
@blueprint_clientes.route("", methods=["GET"])
@rota_protegida(PAPEL_ADMIN, PAPEL_BARBEIRO)
def listar():
    filtros = schema_filtro.load(request.args.to_dict())
    clientes, total = obter_servico().listar(**filtros)
    return jsonify(
        montar_pagina(
            schema_lista_clientes.dump(clientes),
            total,
            filtros["pagina"],
            filtros["por_pagina"],
        )
    )


@blueprint_clientes.route("/<int:cliente_id>", methods=["GET"])
@rota_protegida(PAPEL_ADMIN, PAPEL_BARBEIRO)
def detalhar(cliente_id):
    return jsonify(schema_cliente.dump(obter_servico().buscar(cliente_id)))


@blueprint_clientes.route("", methods=["POST"])
@rota_protegida(PAPEL_ADMIN)
def cadastrar():
    dados = schema_cadastro.load(request.get_json())
    cliente = obter_servico().cadastrar(dados)
    return jsonify(schema_cliente.dump(cliente)), 201


@blueprint_clientes.route("/<int:cliente_id>", methods=["PUT"])
@rota_protegida(PAPEL_ADMIN)
def atualizar(cliente_id):
    dados = schema_atualizacao.load(request.get_json())
    cliente = obter_servico().atualizar(cliente_id, dados)
    return jsonify(schema_cliente.dump(cliente))


@blueprint_clientes.route("/<int:cliente_id>", methods=["DELETE"])
@rota_protegida(PAPEL_ADMIN)
def desativar(cliente_id):
    # Exclusao logica: o registro fica, so deixa de estar ativo (RF06).
    obter_servico().desativar(cliente_id)
    return "", 204
