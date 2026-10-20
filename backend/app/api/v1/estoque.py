from flask import Blueprint, jsonify, request

from app.api.decoradores import rota_protegida, usuario_logado_id
from app.models.usuario import PAPEL_ADMIN
from app.repositories.movimentacao_estoque_repository import (
    MovimentacaoEstoqueRepository,
)
from app.repositories.produto_repository import ProdutoRepository
from app.schemas.paginacao_schema import montar_pagina
from app.schemas.produto_schema import (
    MovimentacaoCriacaoSchema,
    MovimentacaoFiltroSchema,
    MovimentacaoSchema,
    ProdutoAtualizacaoSchema,
    ProdutoCadastroSchema,
    ProdutoFiltroSchema,
    ProdutoSchema,
)
from app.services.estoque_service import EstoqueService
from app.services.produto_service import ProdutoService

blueprint_estoque = Blueprint("estoque", __name__, url_prefix="/produtos")

schema_cadastro = ProdutoCadastroSchema()
schema_atualizacao = ProdutoAtualizacaoSchema()
schema_filtro = ProdutoFiltroSchema()
schema_produto = ProdutoSchema()
schema_lista_produtos = ProdutoSchema(many=True)
schema_movimentacao_criacao = MovimentacaoCriacaoSchema()
schema_movimentacao_filtro = MovimentacaoFiltroSchema()
schema_movimentacao = MovimentacaoSchema()
schema_lista_movimentacoes = MovimentacaoSchema(many=True, exclude=("produto",))


def obter_produto_service():
    return ProdutoService(ProdutoRepository())


def obter_estoque_service():
    return EstoqueService(ProdutoRepository(), MovimentacaoEstoqueRepository())


# Estoque e area do admin (RF22). Todas as rotas exigem esse papel.
@blueprint_estoque.route("", methods=["GET"])
@rota_protegida(PAPEL_ADMIN)
def listar():
    filtros = schema_filtro.load(request.args.to_dict())
    produtos = obter_produto_service().listar(filtros["ativo"])
    return jsonify(schema_lista_produtos.dump(produtos))


@blueprint_estoque.route("/em-falta", methods=["GET"])
@rota_protegida(PAPEL_ADMIN)
def listar_em_falta():
    produtos = obter_produto_service().listar_em_falta()
    return jsonify(schema_lista_produtos.dump(produtos))


@blueprint_estoque.route("/<int:produto_id>", methods=["GET"])
@rota_protegida(PAPEL_ADMIN)
def detalhar(produto_id):
    return jsonify(schema_produto.dump(obter_produto_service().buscar(produto_id)))


@blueprint_estoque.route("", methods=["POST"])
@rota_protegida(PAPEL_ADMIN)
def cadastrar():
    dados = schema_cadastro.load(request.get_json())
    produto = obter_produto_service().cadastrar(dados)
    return jsonify(schema_produto.dump(produto)), 201


@blueprint_estoque.route("/<int:produto_id>", methods=["PUT"])
@rota_protegida(PAPEL_ADMIN)
def atualizar(produto_id):
    dados = schema_atualizacao.load(request.get_json(), partial=True)
    produto = obter_produto_service().atualizar(produto_id, dados)
    return jsonify(schema_produto.dump(produto))


@blueprint_estoque.route("/<int:produto_id>", methods=["DELETE"])
@rota_protegida(PAPEL_ADMIN)
def desativar(produto_id):
    # Exclusao logica: o historico de movimentacoes continua apontando para ele.
    obter_produto_service().desativar(produto_id)
    return "", 204


@blueprint_estoque.route("/<int:produto_id>/entradas", methods=["POST"])
@rota_protegida(PAPEL_ADMIN)
def registrar_entrada(produto_id):
    dados = schema_movimentacao_criacao.load(request.get_json())
    movimentacao = obter_estoque_service().registrar_entrada(
        produto_id, dados["quantidade"], usuario_logado_id(), dados.get("motivo")
    )
    return jsonify(schema_movimentacao.dump(movimentacao)), 201


@blueprint_estoque.route("/<int:produto_id>/saidas", methods=["POST"])
@rota_protegida(PAPEL_ADMIN)
def registrar_saida(produto_id):
    dados = schema_movimentacao_criacao.load(request.get_json())
    movimentacao = obter_estoque_service().registrar_saida(
        produto_id, dados["quantidade"], usuario_logado_id(), dados.get("motivo")
    )
    return jsonify(schema_movimentacao.dump(movimentacao)), 201


@blueprint_estoque.route("/<int:produto_id>/movimentacoes", methods=["GET"])
@rota_protegida(PAPEL_ADMIN)
def listar_movimentacoes(produto_id):
    filtros = schema_movimentacao_filtro.load(request.args.to_dict())
    movimentacoes, total = obter_estoque_service().listar_movimentacoes(
        produto_id, **filtros
    )
    return jsonify(
        montar_pagina(
            schema_lista_movimentacoes.dump(movimentacoes),
            total,
            filtros["pagina"],
            filtros["por_pagina"],
        )
    )
