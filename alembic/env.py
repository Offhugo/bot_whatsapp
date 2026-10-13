
from logging.config import fileConfig

from alembic import context

from app.database import DATABASE_URL, engine
from app.models import (
    Empresa,
    Mensagem,
    Registro,
    Usuario,
    UsuarioEmpresa,
    Viagem,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Mantém os models importados e disponibiliza
# todas as tabelas para o autogenerate.
target_metadata = Usuario.metadata

# Utiliza a mesma URL de conexão da aplicação.
config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL.render_as_string(hide_password=False).replace("%", "%%"),
)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

