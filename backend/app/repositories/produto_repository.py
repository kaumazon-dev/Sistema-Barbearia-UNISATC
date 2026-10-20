from app.extensions import db
from app.models.produto import Produto
from app.repositories.base_repository import BaseRepository


class ProdutoRepository(BaseRepository):
    def __init__(self):
        super().__init__(Produto)

    def listar(self, ativo=None):
        consulta = db.select(self.model).order_by(self.model.nome, self.model.id)
        if ativo is not None:
            consulta = consulta.where(self.model.ativo == ativo)
        return db.session.execute(consulta).scalars().all()

    def listar_em_falta(self):
        """Produtos ativos com quantidade_atual <= estoque_minimo (RF27, RF32).

        O filtro roda no banco: em_falta e hybrid_property e vira SQL aqui.
        """
        consulta = (
            db.select(self.model)
            .where(self.model.ativo.is_(True), self.model.em_falta)
            .order_by(self.model.nome, self.model.id)
        )
        return db.session.execute(consulta).scalars().all()

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
