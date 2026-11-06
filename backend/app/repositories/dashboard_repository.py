from sqlalchemy import func

from app.core.fuso import FUSO_BARBEARIA
from app.extensions import db
from app.models.agendamento import Agendamento, AgendamentoServico
from app.models.servico import Servico


class DashboardRepository:
    """Consultas agregadas do dashboard (RF28 a RF31).

    Nao herda de BaseRepository: o dashboard nao tem model proprio nem CRUD.
    Toda agregacao roda no banco (GROUP BY, SUM, COUNT), nunca percorrendo
    listas em Python. Quais status entram em cada metrica e decisao do service,
    por isso o status chega como argumento.
    """

    def _periodo(self, unidade):
        # Truncar no fuso da barbearia: domingo 22h em Brasilia ja e segunda em
        # UTC e cairia na semana seguinte. A mesma expressao vai no select, no
        # group_by e no order_by; escrita tres vezes, o Postgres recusa.
        return func.date_trunc(
            unidade, func.timezone(FUSO_BARBEARIA.key, Agendamento.inicio)
        )

    def _no_intervalo(self, inicio, fim):
        # [inicio, fim), comparando a coluna crua: o intervalo ja chega com fuso.
        return Agendamento.inicio >= inicio, Agendamento.inicio < fim

    def contar_atendimentos(self, inicio, fim, unidade, status):
        """[(periodo, quantidade)]. Sem JOIN nos itens: agendamento com corte e
        barba viraria duas linhas e seria contado duas vezes.
        """
        periodo = self._periodo(unidade)
        consulta = (
            db.select(periodo, func.count())
            .where(Agendamento.status == status, *self._no_intervalo(inicio, fim))
            .group_by(periodo)
            .order_by(periodo)
        )
        return db.session.execute(consulta).all()

    def somar_faturamento(self, inicio, fim, unidade, status):
        """[(periodo, total)]. Soma preco_cobrado, nunca servico.preco: um
        reajuste nao pode reescrever meses ja fechados (RN02).
        """
        periodo = self._periodo(unidade)
        consulta = (
            db.select(periodo, func.sum(AgendamentoServico.preco_cobrado))
            .select_from(Agendamento)
            .join(AgendamentoServico, AgendamentoServico.agendamento_id == Agendamento.id)
            .where(Agendamento.status == status, *self._no_intervalo(inicio, fim))
            .group_by(periodo)
            .order_by(periodo)
        )
        return db.session.execute(consulta).all()

    def ranking_servicos(self, inicio, fim, status, limite):
        """[(servico_id, nome, quantidade, receita)], do mais vendido ao menos."""
        quantidade = func.count().label("quantidade")
        consulta = (
            db.select(
                Servico.id.label("servico_id"),
                Servico.nome,
                quantidade,
                func.sum(AgendamentoServico.preco_cobrado).label("receita"),
            )
            .select_from(AgendamentoServico)
            .join(Agendamento, Agendamento.id == AgendamentoServico.agendamento_id)
            .join(Servico, Servico.id == AgendamentoServico.servico_id)
            .where(Agendamento.status == status, *self._no_intervalo(inicio, fim))
            .group_by(Servico.id, Servico.nome)
            .order_by(quantidade.desc(), Servico.nome)
            .limit(limite)
        )
        return db.session.execute(consulta).all()

    def contar_por_status(self, inicio, fim, status):
        """[(status, quantidade)] para os status pedidos. Status sem nenhum
        agendamento no periodo nao aparece.
        """
        consulta = (
            db.select(Agendamento.status, func.count())
            .where(Agendamento.status.in_(status), *self._no_intervalo(inicio, fim))
            .group_by(Agendamento.status)
        )
        return db.session.execute(consulta).all()
