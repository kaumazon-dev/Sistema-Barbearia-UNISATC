from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property

from app.extensions import db

UNIDADES = ("un", "ml", "g")

TIPO_ENTRADA = "entrada"
TIPO_SAIDA = "saida"
TIPOS_MOVIMENTACAO = (TIPO_ENTRADA, TIPO_SAIDA)


class Produto(db.Model):
    """quantidade_atual nunca e alterada direto: so o EstoqueService mexe nela,
    sempre junto com a movimentacao correspondente (RN04).
    """

    __tablename__ = "produto"
    __table_args__ = (
        # Rede de seguranca da RF26: o service ja recusa, mas se algum caminho
        # escapar o banco nao aceita estoque negativo.
        db.CheckConstraint(
            "quantidade_atual >= 0", name="ck_produto_quantidade_nao_negativa"
        ),
        db.CheckConstraint(
            "estoque_minimo >= 0", name="ck_produto_estoque_minimo_nao_negativo"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    # un, ml, g
    unidade = db.Column(db.String(10), nullable=False)
    # Numeric e nao Integer: ml e g podem ser fracionados.
    quantidade_atual = db.Column(
        db.Numeric(10, 2), nullable=False, server_default=db.text("0")
    )
    estoque_minimo = db.Column(
        db.Numeric(10, 2), nullable=False, server_default=db.text("0")
    )
    ativo = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))

    @hybrid_property
    def em_falta(self):
        """Quantidade no minimo ou abaixo dele (RF27).

        hybrid_property: a mesma regra vale no Python (produto.em_falta) e no
        SQL (where(Produto.em_falta)), sem duas definicoes para divergir.
        """
        return self.quantidade_atual <= self.estoque_minimo

    def __repr__(self):
        return f"<Produto {self.id} {self.nome} {self.quantidade_atual}{self.unidade}>"


class MovimentacaoEstoque(db.Model):
    """Historico de toda mudanca de quantidade. O dashboard le daqui."""

    __tablename__ = "movimentacao_estoque"
    __table_args__ = (
        # Sempre positiva: o sinal vem de tipo.
        db.CheckConstraint(
            "quantidade > 0", name="ck_movimentacao_quantidade_positiva"
        ),
        db.Index("idx_movimentacao_produto_data", "produto_id", "criado_em"),
    )

    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"), nullable=False)
    # Quem registrou (RF24).
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    tipo = db.Column(
        db.Enum(*TIPOS_MOVIMENTACAO, name="movimentacao_tipo"), nullable=False
    )
    quantidade = db.Column(db.Numeric(10, 2), nullable=False)
    motivo = db.Column(db.String(160))
    criado_em = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    produto = db.relationship("Produto")
    usuario = db.relationship("Usuario")

    def __repr__(self):
        return f"<MovimentacaoEstoque {self.id} {self.tipo} {self.quantidade}>"
