"""cria tabelas produto e movimentacao_estoque

Revision ID: b7c41e2a9d10
Revises: 981650e2cfd3
Create Date: 2026-10-20 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7c41e2a9d10'
down_revision = '981650e2cfd3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('produto',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(length=120), nullable=False),
    sa.Column('unidade', sa.String(length=10), nullable=False),
    sa.Column('quantidade_atual', sa.Numeric(precision=10, scale=2), server_default=sa.text('0'), nullable=False),
    sa.Column('estoque_minimo', sa.Numeric(precision=10, scale=2), server_default=sa.text('0'), nullable=False),
    sa.Column('ativo', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.CheckConstraint('estoque_minimo >= 0', name='ck_produto_estoque_minimo_nao_negativo'),
    sa.CheckConstraint('quantidade_atual >= 0', name='ck_produto_quantidade_nao_negativa'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('movimentacao_estoque',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('produto_id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('tipo', sa.Enum('entrada', 'saida', name='movimentacao_tipo'), nullable=False),
    sa.Column('quantidade', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('motivo', sa.String(length=160), nullable=True),
    sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('quantidade > 0', name='ck_movimentacao_quantidade_positiva'),
    sa.ForeignKeyConstraint(['produto_id'], ['produto.id'], ),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('movimentacao_estoque', schema=None) as batch_op:
        batch_op.create_index('idx_movimentacao_produto_data', ['produto_id', 'criado_em'], unique=False)


def downgrade():
    with op.batch_alter_table('movimentacao_estoque', schema=None) as batch_op:
        batch_op.drop_index('idx_movimentacao_produto_data')

    op.drop_table('movimentacao_estoque')
    op.drop_table('produto')
    # O drop_table nao remove o tipo enum criado no upgrade.
    sa.Enum(name='movimentacao_tipo').drop(op.get_bind())
