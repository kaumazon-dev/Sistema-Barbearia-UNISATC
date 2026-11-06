"""movimentacao_estoque imutavel: trigger recusa UPDATE e DELETE

Revision ID: d3a8f5c21e47
Revises: b7c41e2a9d10
Create Date: 2026-10-23 19:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'd3a8f5c21e47'
down_revision = 'b7c41e2a9d10'
branch_labels = None
depends_on = None


def upgrade():
    # Escrita a mao: o autogenerate nao enxerga funcao nem trigger.
    # movimentacao_estoque e historico (o dashboard depende dela): registro
    # gravado nunca e editado nem apagado. Correcao = movimentacao contraria.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION bloquear_alteracao_movimentacao() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'movimentacao_estoque e historico: % nao e permitido.', TG_OP
                USING ERRCODE = 'restrict_violation';
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_movimentacao_estoque_imutavel
            BEFORE UPDATE OR DELETE ON movimentacao_estoque
            FOR EACH ROW EXECUTE FUNCTION bloquear_alteracao_movimentacao()
        """
    )


def downgrade():
    op.execute(
        "DROP TRIGGER IF EXISTS trg_movimentacao_estoque_imutavel ON movimentacao_estoque"
    )
    op.execute("DROP FUNCTION IF EXISTS bloquear_alteracao_movimentacao()")
