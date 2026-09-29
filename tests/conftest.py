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
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()