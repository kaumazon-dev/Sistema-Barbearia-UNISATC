from app.extensions import db
from app.models.produto import Produto
from app.repositories.base_repository import BaseRepository


class ProdutoRepository(BaseRepository):
    def __init__(self):
        super().__init__(Produto)

    def buscar_para_movimentar(self, produto_id):
        """Busca o produto travando a linha (SELECT ... FOR UPDATE).

        Duas saidas simultaneas do mesmo produto leriam o mesmo saldo e as duas
        passariam na checagem do service. Com a trava, a segunda espera a
        primeira terminar e le o saldo ja atualizado. A trava solta no commit
        ou no rollback.

        populate_existing: se o produto ja estava na sessao, recarrega do banco
        em vez de confiar na copia em memoria.
        """
        return db.session.get(
            self.model, produto_id, with_for_update=True, populate_existing=True
        )
