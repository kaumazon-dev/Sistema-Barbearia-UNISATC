from sqlalchemy.orm import selectinload

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

    def listar_do_produto(self, produto_id, tipo=None, pagina=1, por_pagina=20):
        """Historico paginado do produto, da mais recente para a mais antiga.

        Usa o indice (produto_id, criado_em).
        """
        consulta = (
            db.select(self.model)
            .options(selectinload(self.model.usuario))
            .where(self.model.produto_id == produto_id)
        )
        if tipo is not None:
            consulta = consulta.where(self.model.tipo == tipo)
        consulta = consulta.order_by(self.model.criado_em.desc(), self.model.id.desc())
        return self.paginar(consulta, pagina, por_pagina)
