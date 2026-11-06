"""Unico lugar do sistema que altera produto.quantidade_atual (RN04, RF25).

Regra de ouro: a quantidade nunca muda sem a movimentacao correspondente, e as
duas escritas vao na mesma transacao. Se uma falhar, as duas voltam; senao o
estoque diverge do historico e o dashboard mente.

tests/unit/test_estoque_service.py tem um teste que varre app/ e falha se
aparecer escrita em quantidade_atual fora deste arquivo.
"""

from decimal import Decimal

from app.core.exceptions import NaoEncontrado, RegraDeNegocioViolada
from app.models.produto import (
    TIPO_ENTRADA,
    TIPO_SAIDA,
    TIPOS_MOVIMENTACAO,
    MovimentacaoEstoque,
)


def calcular_nova_quantidade(produto, tipo, quantidade):
    """Saldo do produto depois da movimentacao. Nao altera o produto.

    Recusa saida maior que o disponivel (RF26).

    Estoque negativo e erro de negocio (vendeu o que nao tinha), entao quem
    barra e o service com mensagem legivel. A CHECK do banco e so a ultima
    linha de defesa.
    """
    if tipo not in TIPOS_MOVIMENTACAO:
        raise RegraDeNegocioViolada(f"Tipo de movimentação inválido: {tipo}.")
    if quantidade <= 0:
        raise RegraDeNegocioViolada("A quantidade da movimentação deve ser positiva.")
    atual = produto.quantidade_atual
    if tipo == TIPO_ENTRADA:
        return atual + quantidade
    if quantidade > atual:
        raise RegraDeNegocioViolada(
            f"Estoque insuficiente de {produto.nome}: disponível "
            f"{atual} {produto.unidade}, pedido {quantidade} {produto.unidade}."
        )
    return atual - quantidade


class EstoqueService:
    """Quem registra chega por argumento (usuario_id), vindo da rota (RF24)."""

    def __init__(self, produto_repositorio, movimentacao_repositorio):
        self.produto_repositorio = produto_repositorio
        self.movimentacao_repositorio = movimentacao_repositorio

    def listar_movimentacoes(self, produto_id, tipo=None, pagina=1, por_pagina=20):
        if self.produto_repositorio.get_by_id(produto_id) is None:
            raise NaoEncontrado(f"Produto {produto_id} não existe.")
        return self.movimentacao_repositorio.listar_do_produto(
            produto_id, tipo=tipo, pagina=pagina, por_pagina=por_pagina
        )

    def registrar_entrada(self, produto_id, quantidade, usuario_id, motivo=None):
        return self.movimentar(
            produto_id,
            {"tipo": TIPO_ENTRADA, "quantidade": quantidade, "motivo": motivo},
            usuario_id,
        )

    def registrar_saida(self, produto_id, quantidade, usuario_id, motivo=None):
        return self.movimentar(
            produto_id,
            {"tipo": TIPO_SAIDA, "quantidade": quantidade, "motivo": motivo},
            usuario_id,
        )

    def movimentar(self, produto_id, dados, usuario_id):
        """Altera a quantidade e grava a movimentacao numa transacao so.

        dados: {"tipo": "entrada" | "saida", "quantidade": Decimal, "motivo": str}
        """
        # Daqui ate o commit/rollback a linha do produto fica travada.
        produto = self.produto_repositorio.buscar_para_movimentar(produto_id)
        try:
            if produto is None:
                raise NaoEncontrado(f"Produto {produto_id} não existe.")
            if not produto.ativo:
                raise RegraDeNegocioViolada(
                    f"Produto {produto.nome} está desativado e não pode ser movimentado."
                )

            tipo = dados["tipo"]
            # Decimal(str()): float viraria dizima (Decimal(0.1) != 0.1).
            quantidade = Decimal(str(dados["quantidade"]))
            nova_quantidade = calcular_nova_quantidade(produto, tipo, quantidade)

            movimentacao = MovimentacaoEstoque(
                produto=produto,
                usuario_id=usuario_id,
                tipo=tipo,
                quantidade=quantidade,
                motivo=dados.get("motivo"),
            )
            produto.quantidade_atual = nova_quantidade
            return self.movimentacao_repositorio.registrar(produto, movimentacao)
        except Exception:
            # Desfaz tudo: a quantidade em memoria, a movimentacao pendente e a
            # trava do produto. Vale tanto para regra violada quanto para erro
            # do banco no commit.
            self.movimentacao_repositorio.desfazer()
            raise
