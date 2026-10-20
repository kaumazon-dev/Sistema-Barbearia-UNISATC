"""Service de produto e regra de "em falta", sem banco e sem subir o Flask."""

from decimal import Decimal

import pytest

from app.core.exceptions import NaoEncontrado
from app.models.produto import Produto
from app.services.produto_service import ProdutoService


class RepositorioFalso:
    def __init__(self, produtos=None):
        self.produtos = list(produtos or [])
        self.proximo_id = len(self.produtos) + 1

    def get_by_id(self, id):
        return next((p for p in self.produtos if p.id == id), None)

    def listar_em_falta(self):
        return [p for p in self.produtos if p.ativo and p.em_falta]

    def create(self, entidade):
        entidade.id = self.proximo_id
        self.proximo_id += 1
        self.produtos.append(entidade)
        return entidade

    def update(self, entidade):
        return entidade


def construir_produto(id, nome="Pomada", quantidade="10", minimo="2", ativo=True):
    produto = Produto(
        nome=nome,
        unidade="un",
        quantidade_atual=Decimal(quantidade),
        estoque_minimo=Decimal(minimo),
        ativo=ativo,
    )
    produto.id = id
    return produto


# --- regra de "em falta" (RF27) -------------------------------------------------


@pytest.mark.parametrize(
    "quantidade, minimo, esperado",
    [
        ("3", "2", False),
        ("2", "2", True),  # no minimo ja conta como em falta
        ("1.5", "2", True),
        ("0", "0", True),  # sem estoque nenhum
    ],
)
def test_em_falta(quantidade, minimo, esperado):
    produto = construir_produto(1, quantidade=quantidade, minimo=minimo)
    assert produto.em_falta is esperado


def test_em_falta_tambem_vira_sql():
    # hybrid_property: no nivel da classe vira expressao para o WHERE.
    sql = str(Produto.em_falta.expression)
    assert "quantidade_atual <= " in sql and "estoque_minimo" in sql


def test_listar_em_falta_ignora_inativo():
    em_falta = construir_produto(1, "Pomada", quantidade="1")
    inativo = construir_produto(2, "Gel", quantidade="0", ativo=False)
    sobrando = construir_produto(3, "Shampoo", quantidade="50")
    service = ProdutoService(RepositorioFalso([em_falta, inativo, sobrando]))

    assert service.listar_em_falta() == [em_falta]


# --- cadastro -------------------------------------------------------------------


def test_cadastrar_nao_define_quantidade():
    """A quantidade nasce do server_default (zero) e so muda por movimentacao."""
    produto = ProdutoService(RepositorioFalso()).cadastrar(
        {"nome": "Pomada", "unidade": "g", "estoque_minimo": Decimal("5")}
    )

    assert produto.id == 1
    assert produto.quantidade_atual is None
    assert produto.estoque_minimo == Decimal("5")


def test_buscar_inexistente_recusa():
    with pytest.raises(NaoEncontrado):
        ProdutoService(RepositorioFalso()).buscar(1)


def test_atualizar_altera_so_os_campos_enviados():
    existente = construir_produto(1)
    ProdutoService(RepositorioFalso([existente])).atualizar(
        1, {"estoque_minimo": Decimal("4")}
    )

    assert existente.estoque_minimo == Decimal("4")
    assert existente.nome == "Pomada"
    assert existente.quantidade_atual == Decimal("10")


def test_atualizar_ignora_quantidade_mesmo_se_chegar():
    # O schema ja recusa, mas o service tambem nao repassa.
    existente = construir_produto(1)
    ProdutoService(RepositorioFalso([existente])).atualizar(
        1, {"quantidade_atual": Decimal("999")}
    )
    assert existente.quantidade_atual == Decimal("10")


def test_desativar_nao_apaga_so_marca_inativo():
    existente = construir_produto(1)
    repositorio = RepositorioFalso([existente])

    ProdutoService(repositorio).desativar(1)

    assert existente.ativo is False
    assert existente in repositorio.produtos
