"""Service de estoque, sem banco e sem subir o Flask.

O repositorio falso imita a transacao: registrar() "commita" copiando o estado
do produto, desfazer() volta o produto para o ultimo estado commitado. Assim da
para provar que, se a gravacao falhar, a quantidade nao fica alterada.
"""

import re
from decimal import Decimal
from pathlib import Path

import pytest

from app.core.exceptions import NaoEncontrado, RegraDeNegocioViolada
from app.models.produto import TIPO_ENTRADA, TIPO_SAIDA, MovimentacaoEstoque, Produto
from app.repositories.movimentacao_estoque_repository import (
    MovimentacaoEstoqueRepository,
)
from app.services.estoque_service import EstoqueService, calcular_nova_quantidade

USUARIO_ID = 7


class RepositorioProdutoFalso:
    def __init__(self, produtos):
        self.produtos = {p.id: p for p in produtos}
        self.travados = []

    def get_by_id(self, produto_id):
        return self.produtos.get(produto_id)

    def buscar_para_movimentar(self, produto_id):
        self.travados.append(produto_id)
        return self.produtos.get(produto_id)


class RepositorioMovimentacaoFalso:
    def __init__(self, produtos, falhar_no_commit=False):
        self.produtos = produtos
        self.commitado = {p.id: p.quantidade_atual for p in produtos}
        self.movimentacoes = []
        self.falhar_no_commit = falhar_no_commit
        self.desfeitos = 0

    def registrar(self, produto, movimentacao):
        if self.falhar_no_commit:
            raise RuntimeError("banco caiu no commit")
        self.commitado[produto.id] = produto.quantidade_atual
        self.movimentacoes.append(movimentacao)
        return movimentacao

    def listar_do_produto(self, produto_id, **filtros):
        self.ultima_listagem = dict(filtros, produto_id=produto_id)
        return [], 0

    def desfazer(self):
        self.desfeitos += 1
        for produto in self.produtos:
            produto.quantidade_atual = self.commitado[produto.id]


def construir_produto(id, nome, quantidade, unidade="un", ativo=True):
    produto = Produto(
        nome=nome,
        unidade=unidade,
        quantidade_atual=Decimal(quantidade),
        estoque_minimo=Decimal("2"),
        ativo=ativo,
    )
    produto.id = id
    return produto


@pytest.fixture
def pomada():
    return construir_produto(1, "Pomada", "10")


@pytest.fixture
def inativo():
    return construir_produto(2, "Gel antigo", "5", ativo=False)


@pytest.fixture
def repositorios(pomada, inativo):
    produtos = [pomada, inativo]
    return RepositorioProdutoFalso(produtos), RepositorioMovimentacaoFalso(produtos)


@pytest.fixture
def service(repositorios):
    return EstoqueService(*repositorios)


# --- calculo puro do saldo ------------------------------------------------------


def test_entrada_soma(pomada):
    assert calcular_nova_quantidade(pomada, TIPO_ENTRADA, Decimal("3")) == Decimal("13")


def test_saida_subtrai(pomada):
    assert calcular_nova_quantidade(pomada, TIPO_SAIDA, Decimal("3")) == Decimal("7")


def test_saida_de_tudo_zera(pomada):
    assert calcular_nova_quantidade(pomada, TIPO_SAIDA, Decimal("10")) == 0


def test_calculo_nao_altera_o_produto(pomada):
    calcular_nova_quantidade(pomada, TIPO_SAIDA, Decimal("3"))
    assert pomada.quantidade_atual == Decimal("10")


def test_saida_maior_que_o_disponivel_recusa(pomada):
    with pytest.raises(RegraDeNegocioViolada) as erro:
        calcular_nova_quantidade(pomada, TIPO_SAIDA, Decimal("10.01"))
    assert erro.value.mensagem == (
        "Estoque insuficiente de Pomada: disponível 10 un, pedido 10.01 un."
    )


@pytest.mark.parametrize("quantidade", ["0", "-1"])
def test_quantidade_precisa_ser_positiva(pomada, quantidade):
    with pytest.raises(RegraDeNegocioViolada):
        calcular_nova_quantidade(pomada, TIPO_ENTRADA, Decimal(quantidade))


def test_tipo_invalido_recusa(pomada):
    with pytest.raises(RegraDeNegocioViolada):
        calcular_nova_quantidade(pomada, "ajuste", Decimal("1"))


# --- movimentar: quantidade e movimentacao andam juntas -------------------------


def test_entrada_altera_quantidade_e_grava_movimentacao(service, repositorios, pomada):
    _, movimentacoes = repositorios

    movimentacao = service.registrar_entrada(1, Decimal("5"), USUARIO_ID, "compra")

    assert pomada.quantidade_atual == Decimal("15")
    assert movimentacoes.movimentacoes == [movimentacao]
    assert movimentacao.produto is pomada
    assert movimentacao.tipo == TIPO_ENTRADA
    assert movimentacao.quantidade == Decimal("5")
    assert movimentacao.motivo == "compra"
    assert movimentacao.usuario_id == USUARIO_ID


def test_saida_altera_quantidade_e_grava_movimentacao(service, repositorios, pomada):
    _, movimentacoes = repositorios

    movimentacao = service.registrar_saida(1, Decimal("4"), USUARIO_ID)

    assert pomada.quantidade_atual == Decimal("6")
    assert movimentacao.tipo == TIPO_SAIDA
    assert movimentacoes.movimentacoes == [movimentacao]


def test_quantidade_e_sempre_positiva_na_movimentacao(service):
    # O sinal vem do tipo, nao da quantidade.
    movimentacao = service.registrar_saida(1, Decimal("4"), USUARIO_ID)
    assert movimentacao.quantidade == Decimal("4")


def test_saldo_bate_com_o_historico(service, repositorios, pomada):
    _, movimentacoes = repositorios
    service.registrar_entrada(1, Decimal("5"), USUARIO_ID)
    service.registrar_saida(1, Decimal("12"), USUARIO_ID)
    service.registrar_entrada(1, Decimal("0.5"), USUARIO_ID)

    saldo = Decimal("10")
    for m in movimentacoes.movimentacoes:
        saldo += m.quantidade if m.tipo == TIPO_ENTRADA else -m.quantidade
    assert pomada.quantidade_atual == saldo == Decimal("3.5")


def test_quantidade_float_vira_decimal_exato(service, pomada):
    service.registrar_entrada(1, 0.1, USUARIO_ID)
    assert pomada.quantidade_atual == Decimal("10.1")


def test_movimentar_trava_o_produto_antes_de_ler_o_saldo(service, repositorios):
    produtos, _ = repositorios
    service.registrar_saida(1, Decimal("1"), USUARIO_ID)
    assert produtos.travados == [1]


# --- recusas: nada muda e nada e gravado ----------------------------------------


def test_saida_maior_que_o_disponivel_nao_mexe_em_nada(service, repositorios, pomada):
    _, movimentacoes = repositorios

    with pytest.raises(RegraDeNegocioViolada):
        service.registrar_saida(1, Decimal("11"), USUARIO_ID)

    assert pomada.quantidade_atual == Decimal("10")
    assert movimentacoes.movimentacoes == []
    # Rollback tambem solta a trava do produto.
    assert movimentacoes.desfeitos == 1


def test_produto_inexistente(service, repositorios):
    _, movimentacoes = repositorios
    with pytest.raises(NaoEncontrado):
        service.registrar_entrada(99, Decimal("1"), USUARIO_ID)
    assert movimentacoes.movimentacoes == []


def test_produto_desativado_nao_movimenta(service, repositorios, inativo):
    _, movimentacoes = repositorios
    with pytest.raises(RegraDeNegocioViolada):
        service.registrar_entrada(2, Decimal("1"), USUARIO_ID)
    assert inativo.quantidade_atual == Decimal("5")
    assert movimentacoes.movimentacoes == []


def test_falha_ao_gravar_desfaz_a_quantidade(pomada, inativo):
    """Se a gravacao falhar, as duas escritas voltam: a quantidade nao pode
    ficar alterada sem a movimentacao correspondente.
    """
    produtos = [pomada, inativo]
    movimentacoes = RepositorioMovimentacaoFalso(produtos, falhar_no_commit=True)
    service = EstoqueService(RepositorioProdutoFalso(produtos), movimentacoes)

    with pytest.raises(RuntimeError):
        service.registrar_entrada(1, Decimal("5"), USUARIO_ID)

    assert movimentacoes.desfeitos == 1
    assert pomada.quantidade_atual == Decimal("10")
    assert movimentacoes.movimentacoes == []


# --- historico --------------------------------------------------------------------


def test_listar_movimentacoes_repassa_filtros(service, repositorios):
    _, movimentacoes = repositorios
    service.listar_movimentacoes(1, tipo=TIPO_SAIDA, pagina=2, por_pagina=5)
    assert movimentacoes.ultima_listagem == {
        "produto_id": 1,
        "tipo": TIPO_SAIDA,
        "pagina": 2,
        "por_pagina": 5,
    }


def test_listar_movimentacoes_de_produto_inexistente(service):
    with pytest.raises(NaoEncontrado):
        service.listar_movimentacoes(99)


# --- historico imutavel ---------------------------------------------------------


@pytest.mark.parametrize("operacao", ["update", "delete"])
def test_repositorio_nao_edita_nem_apaga_movimentacao(operacao):
    """Movimentacao e historico: correcao se faz com movimentacao contraria."""
    with pytest.raises(TypeError, match="historico"):
        getattr(MovimentacaoEstoqueRepository(), operacao)(MovimentacaoEstoque())


# --- guarda: ninguem altera a quantidade por fora do service --------------------

APP = Path(__file__).resolve().parents[2] / "app"
PERMITIDOS = {
    APP / "models" / "produto.py",  # declaracao da coluna
    APP / "services" / "estoque_service.py",  # o unico que escreve
}
ESCRITA_NA_QUANTIDADE = re.compile(
    r"quantidade_atual\s*[+\-*/]?=(?!=)"  # atribuicao ou argumento nomeado
    r"|[\"']quantidade_atual[\"']"  # setattr(produto, "quantidade_atual", ...)
    r"|set\s+quantidade_atual",  # UPDATE produto SET quantidade_atual
    re.IGNORECASE,
)


def test_nenhum_codigo_fora_do_service_escreve_na_quantidade():
    """RN04: so o EstoqueService pode alterar produto.quantidade_atual.

    Schemas ficam de fora: declaram o campo para serializar a saida. Se um
    schema aceitar quantidade_atual na entrada e algum service repassar, este
    teste pega no service.
    """
    infratores = []
    for arquivo in APP.rglob("*.py"):
        if arquivo in PERMITIDOS or "schemas" in arquivo.parts:
            continue
        for numero, linha in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), 1):
            if ESCRITA_NA_QUANTIDADE.search(linha):
                infratores.append(f"{arquivo.relative_to(APP)}:{numero}: {linha.strip()}")

    assert infratores == [], (
        "Quantidade de produto alterada fora do EstoqueService:\n"
        + "\n".join(infratores)
    )
