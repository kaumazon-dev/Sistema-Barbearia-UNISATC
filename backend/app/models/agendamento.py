from sqlalchemy import DDL, event, func
from sqlalchemy.dialects.postgresql import ExcludeConstraint

from app.extensions import db

STATUS_AGENDADO = "agendado"
STATUS_CONCLUIDO = "concluido"
STATUS_CANCELADO = "cancelado"
STATUS = (STATUS_AGENDADO, STATUS_CONCLUIDO, STATUS_CANCELADO)


class Agendamento(db.Model):
    __tablename__ = "agendamento"
    __table_args__ = (
        db.CheckConstraint("fim > inicio", name="ck_agendamento_fim_depois_inicio"),
        db.Index("idx_agendamento_barbeiro_inicio", "barbeiro_id", "inicio"),
        # Rede de seguranca da RN01 contra condicao de corrida: duas requisicoes
        # simultaneas passam juntas pela checagem do service, mas o banco so
        # aceita a primeira. tstzrange e [inicio, fim), entao encostar e valido.
        ExcludeConstraint(
            ("barbeiro_id", "="),
            (func.tstzrange(db.column("inicio"), db.column("fim")), "&&"),
            name="ex_agendamento_sem_sobreposicao",
            using="gist",
            where=db.text("status <> 'cancelado'"),
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    inicio = db.Column(db.DateTime(timezone=True), nullable=False)
    # Gravado, nao calculado na leitura: e o que permite achar conflito em SQL
    # e o que impede que mudar a duracao de um servico desloque a agenda (RN03).
    fim = db.Column(db.DateTime(timezone=True), nullable=False)
    status = db.Column(
        db.Enum(*STATUS, name="agendamento_status"),
        nullable=False,
        server_default=STATUS_AGENDADO,
    )
    observacao = db.Column(db.Text)
    criado_em = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    cliente = db.relationship("Usuario", foreign_keys=[cliente_id])
    barbeiro = db.relationship("Usuario", foreign_keys=[barbeiro_id])
    itens = db.relationship(
        "AgendamentoServico",
        back_populates="agendamento",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Agendamento {self.id} barbeiro={self.barbeiro_id} {self.inicio}>"


class AgendamentoServico(db.Model):
    """N:N. Um agendamento pode ter corte + barba."""

    __tablename__ = "agendamento_servico"
    __table_args__ = (
        db.CheckConstraint(
            "preco_cobrado >= 0", name="ck_agendamento_servico_preco_nao_negativo"
        ),
    )

    agendamento_id = db.Column(
        db.Integer, db.ForeignKey("agendamento.id"), primary_key=True
    )
    servico_id = db.Column(db.Integer, db.ForeignKey("servico.id"), primary_key=True)
    # Copia de servico.preco no momento da marcacao (RN02).
    preco_cobrado = db.Column(db.Numeric(10, 2), nullable=False)

    agendamento = db.relationship("Agendamento", back_populates="itens")
    servico = db.relationship("Servico")


# O "=" de inteiro dentro de um indice gist vem da extensao btree_gist. A
# migration cria a extensao; isto cobre o create_all dos testes.
event.listen(
    Agendamento.__table__,
    "before_create",
    DDL("CREATE EXTENSION IF NOT EXISTS btree_gist"),
)
