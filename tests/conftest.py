import os

import pytest

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from app.models import Base


# Carrega as variáveis do arquivo .env
load_dotenv()


# Puxa as configurações do banco
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
TEST_DB_NAME = os.getenv("TEST_DB_NAME")


# Monta a URL do banco de testes de forma segura.
# URL.create() trata corretamente caracteres especiais
# presentes na senha.
TEST_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=TEST_DB_NAME
)


# Cria a conexão com o banco de testes
test_engine = create_engine(TEST_DATABASE_URL)


# Cria as sessões utilizadas pelos testes
TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


@pytest.fixture(scope="session", autouse=True)
def criar_tabelas():
    # Cria as tabelas no banco de testes antes dos testes.
    Base.metadata.create_all(bind=test_engine)

    yield

    # Remove as tabelas ao finalizar a sessão de testes.
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db():
    """
    Fixture que fornece uma sessão de banco de dados para os testes.

    Utiliza transação com rollback para isolar dados entre testes,
    evitando conflitos de integridade (duplicação de telefones, etc).
    """
    # Inicia uma transação
    connection = test_engine.connect()
    transaction = connection.begin()

    # Cria uma sessão vinculada à transação
    session = TestSessionLocal(bind=connection)

    try:
        yield session
    finally:
        # Desfaz todas as mudanças feitas durante o teste
        transaction.rollback()
        session.close()
        connection.close()


@pytest.fixture
def anyio_backend():
    """
    Fixture que configura o backend asyncio para testes assincronos.
    Necessário para @pytest.mark.anyio funcionar corretamente.
    """
    return "asyncio"