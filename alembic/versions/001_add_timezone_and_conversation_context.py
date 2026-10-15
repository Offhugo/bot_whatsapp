"""
Add timezone to usuario and viagem_id/empresa_id to conversa.

Items 9 e 10: Persistir contexto de viagem/empresa e normalizar timezones.

Revision ID: 001
Revises:
Create Date: 2026-10-15 18:08:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """
    Upgrade schema para Items 9 e 10.
    """

    # ============================================================
    # Item 10: Adicionar timezone ao Usuario
    # ============================================================

    op.add_column(
        'usuarios',
        sa.Column(
            'timezone',
            sa.String(),
            nullable=False,
            server_default='America/Fortaleza'
        )
    )

    # ============================================================
    # Item 9: Adicionar viagem_id e empresa_id ao Conversa
    # ============================================================

    op.add_column(
        'conversas',
        sa.Column('viagem_id', sa.Integer(), nullable=True)
    )

    op.add_column(
        'conversas',
        sa.Column('empresa_id', sa.Integer(), nullable=True)
    )

    # Foreign keys para integridade referencial
    op.create_foreign_key(
        'fk_conversa_viagem_id',
        'conversas',
        'viagens',
        ['viagem_id'],
        ['id']
    )

    op.create_foreign_key(
        'fk_conversa_empresa_id',
        'conversas',
        'empresas',
        ['empresa_id'],
        ['id']
    )

    # Índices para performance em queries
    op.create_index(
        'ix_conversas_viagem_id',
        'conversas',
        ['viagem_id']
    )

    op.create_index(
        'ix_conversas_empresa_id',
        'conversas',
        ['empresa_id']
    )

    op.create_index(
        'ix_usuarios_timezone',
        'usuarios',
        ['timezone']
    )


def downgrade():
    """
    Downgrade schema para reverter Items 9 e 10.
    """

    # Remover índices
    op.drop_index('ix_usuarios_timezone', table_name='usuarios')
    op.drop_index('ix_conversas_empresa_id', table_name='conversas')
    op.drop_index('ix_conversas_viagem_id', table_name='conversas')

    # Remover foreign keys
    op.drop_constraint('fk_conversa_empresa_id', 'conversas')
    op.drop_constraint('fk_conversa_viagem_id', 'conversas')

    # Remover colunas
    op.drop_column('conversas', 'empresa_id')
    op.drop_column('conversas', 'viagem_id')
    op.drop_column('usuarios', 'timezone')
