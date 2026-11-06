from app.extensions import db


class Servico(db.Model):
    __tablename__ = "servico"
    # Ultima linha de defesa: o schema ja valida, mas o banco nao confia em ninguem.
    __table_args__ = (
        db.CheckConstraint("duracao_minutos > 0", name="ck_servico_duracao_positiva"),
        db.CheckConstraint("preco >= 0", name="ck_servico_preco_nao_negativo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    # Base do calculo do fim do agendamento e da regra de conflito (Fase 4).
    duracao_minutos = db.Column(db.Integer, nullable=False)
    # Numeric e nao Float: float erra centavos (RNF09). E o preco vigente; o
    # valor cobrado de fato fica copiado em agendamento_servico (RN02).
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))

    def __repr__(self):
        return f"<Servico {self.id} {self.nome}>"
