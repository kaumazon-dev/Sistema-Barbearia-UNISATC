from sqlalchemy.orm import selectinload

from app.extensions import db
from app.models.agendamento import Agendamento, AgendamentoServico
from app.repositories.base_repository import BaseRepository


class AgendamentoRepository(BaseRepository):
    def __init__(self):
        super().__init__(Agendamento)

    def buscar_do_barbeiro_no_intervalo(self, barbeiro_id, inicio, fim):
        """Agendamentos do barbeiro que tocam [inicio, fim), de qualquer status.

        So busca: quem decide o que e conflito (cancelado, o proprio agendamento
        na remarcacao) e o service. Usa o indice (barbeiro_id, inicio).
        """
        consulta = (
            db.select(self.model)
            .where(
                self.model.barbeiro_id == barbeiro_id,
                self.model.inicio < fim,
                self.model.fim > inicio,
            )
            .order_by(self.model.inicio)
        )
        return db.session.execute(consulta).scalars().all()

    def listar(
        self,
        inicio=None,
        fim=None,
        barbeiro_id=None,
        cliente_id=None,
        status=None,
        pagina=1,
        por_pagina=20,
    ):
        """Lista paginada em ordem de horario. inicio/fim filtram pelo comeco
        do agendamento: [inicio, fim) e o dia pedido (RF17).
        """
        consulta = db.select(self.model).options(
            selectinload(self.model.cliente),
            selectinload(self.model.barbeiro),
            selectinload(self.model.itens).selectinload(AgendamentoServico.servico),
        )
        if inicio is not None:
            consulta = consulta.where(self.model.inicio >= inicio)
        if fim is not None:
            consulta = consulta.where(self.model.inicio < fim)
        if barbeiro_id is not None:
            consulta = consulta.where(self.model.barbeiro_id == barbeiro_id)
        if cliente_id is not None:
            consulta = consulta.where(self.model.cliente_id == cliente_id)
        if status is not None:
            consulta = consulta.where(self.model.status == status)
        consulta = consulta.order_by(self.model.inicio, self.model.id)
        return self.paginar(consulta, pagina, por_pagina)
