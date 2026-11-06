"""
Migration base: cria o schema completo a partir de app/models.py.

Inclui os itens 3, 9 e 10:
- conversas (histórico, viagem_id, empresa_id)
- usuarios.timezone

Esta migration deve ser a primeira aplicada em um banco vazio.
Não há migrations anteriores: nenhuma tabela é criada fora daqui.

Revision ID: 001
Revises:
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================
    # usuarios
    # ============================================================
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("telefone", sa.String(), nullable=False),
        sa.Column("nome", sa.String(), nullable=True),
        sa.Column("perfil", sa.String(), nullable=False),
        sa.Column("perfil_dinamico", postgresql.JSONB(), nullable=True),
        sa.Column("timezone", sa.String(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usuarios_id", "usuarios", ["id"], unique=False)
    op.create_index("ix_usuarios_telefone", "usuarios", ["telefone"], unique=True)

    # ============================================================
    # empresas
    # ============================================================
    op.create_table(
        "empresas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("cnpj", sa.String(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_empresas_id", "empresas", ["id"], unique=False)
    op.create_index("ix_empresas_cnpj", "empresas", ["cnpj"], unique=True)

    # ============================================================
    # usuarios_empresas
    # ============================================================
    op.create_table(
        "usuarios_empresas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "usuario_id", "empresa_id", name="uq_usuario_empresa"
        ),
    )
    op.create_index(
        "ix_usuarios_empresas_id", "usuarios_empresas", ["id"], unique=False
    )

    # ============================================================
    # mensagens
    # ============================================================
    op.create_table(
        "mensagens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("remetente", sa.String(), nullable=True),
        sa.Column("texto", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mensagens_id", "mensagens", ["id"], unique=False)

    # ============================================================
    # viagens
    # ============================================================
    op.create_table(
        "viagens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("empresa_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("detalhes", postgresql.JSONB(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_viagens_id", "viagens", ["id"], unique=False)

    # ============================================================
    # registros
    # ============================================================
    op.create_table(
        "registros",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("viagem_id", sa.Integer(), nullable=True),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=True),
        sa.Column("tipo", sa.String(), nullable=False),
        sa.Column("dados", postgresql.JSONB(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["viagem_id"], ["viagens.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_registros_id", "registros", ["id"], unique=False)

    # ============================================================
    # conversas
    # ============================================================
    op.create_table(
        "conversas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("viagem_id", sa.Integer(), nullable=True),
        sa.Column("empresa_id", sa.Integer(), nullable=True),
        sa.Column("mensagens", postgresql.JSONB(), nullable=False),
        sa.Column("contexto", postgresql.JSONB(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["viagem_id"], ["viagens.id"]),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversas_id", "conversas", ["id"], unique=False)
    op.create_index(
        "ix_conversas_usuario_id", "conversas", ["usuario_id"], unique=False
    )
    op.create_index(
        "ix_conversas_viagem_id", "conversas", ["viagem_id"], unique=False
    )
    op.create_index(
        "ix_conversas_empresa_id", "conversas", ["empresa_id"], unique=False
    )


def downgrade() -> None:
    # Ordem inversa das dependências de chave estrangeira.
    op.drop_index("ix_conversas_empresa_id", table_name="conversas")
    op.drop_index("ix_conversas_viagem_id", table_name="conversas")
    op.drop_index("ix_conversas_usuario_id", table_name="conversas")
    op.drop_index("ix_conversas_id", table_name="conversas")
    op.drop_table("conversas")

    op.drop_index("ix_registros_id", table_name="registros")
    op.drop_table("registros")

    op.drop_index("ix_viagens_id", table_name="viagens")
    op.drop_table("viagens")

    op.drop_index("ix_mensagens_id", table_name="mensagens")
    op.drop_table("mensagens")

    op.drop_index(
        "ix_usuarios_empresas_id", table_name="usuarios_empresas"
    )
    op.drop_table("usuarios_empresas")

    op.drop_index("ix_empresas_cnpj", table_name="empresas")
    op.drop_index("ix_empresas_id", table_name="empresas")
    op.drop_table("empresas")

    op.drop_index("ix_usuarios_telefone", table_name="usuarios")
    op.drop_index("ix_usuarios_id", table_name="usuarios")
    op.drop_table("usuarios")
