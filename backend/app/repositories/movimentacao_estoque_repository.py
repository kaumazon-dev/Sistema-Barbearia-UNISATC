from app.extensions import db
from app.models.produto import MovimentacaoEstoque
from app.repositories.base_repository import BaseRepository


class MovimentacaoEstoqueRepository(BaseRepository):
    def __init__(self):
        super().__init__(MovimentacaoEstoque)

    def registrar(self, produto, movimentacao):
        """Grava a nova quantidade do produto e a movimentacao num commit so.

        Um commit = uma transacao: ou as duas escritas entram, ou nenhuma.
        Nao usar create()/update() do BaseRepository aqui, porque cada um faz
        o proprio commit e as escritas ficariam em transacoes separadas.
        """
        db.session.add(produto)
        db.session.add(movimentacao)
        db.session.commit()
        return movimentacao
