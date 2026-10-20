from app.core.exceptions import NaoEncontrado
from app.models.produto import Produto


class ProdutoService:
    """Cadastro de produto (RF22). Nao mexe na quantidade.

    Produto nasce com quantidade zero (server_default do banco) e o estoque
    inicial entra como uma movimentacao de entrada, pelo EstoqueService (RN04).
    Produto nunca e apagado de fato, so desativado: o historico aponta para ele.
    """

    def __init__(self, repositorio):
        self.repositorio = repositorio

    def listar(self, ativo=None):
        return self.repositorio.listar(ativo)

    def listar_em_falta(self):
        """Produtos ativos no estoque minimo ou abaixo (RF27). Usado tambem pelo
        card "produtos em falta" do dashboard (RF32).
        """
        return self.repositorio.listar_em_falta()

    def buscar(self, produto_id):
        produto = self.repositorio.get_by_id(produto_id)
        if produto is None:
            raise NaoEncontrado(f"Produto {produto_id} não existe.")
        return produto

    def cadastrar(self, dados):
        produto = Produto(
            nome=dados["nome"],
            unidade=dados["unidade"],
            estoque_minimo=dados["estoque_minimo"],
        )
        return self.repositorio.create(produto)

    def atualizar(self, produto_id, dados):
        produto = self.buscar(produto_id)
        for campo in ("nome", "unidade", "estoque_minimo", "ativo"):
            if campo in dados:
                setattr(produto, campo, dados[campo])
        return self.repositorio.update(produto)

    def desativar(self, produto_id):
        produto = self.buscar(produto_id)
        produto.ativo = False
        return self.repositorio.update(produto)
