"""
Testes para idempotência em RegistroRepository.

Valida que:
- Requisições duplicadas com mesma idempotency_key retornam o mesmo registro
- Sem idempotency_key, cada requisição cria um novo registro
- A coluna idempotency_key é corretamente indexada
"""

import pytest
from datetime import datetime, timezone

from app.models import Registro, Usuario, Empresa
from app.repositories.registro_repository import RegistroRepository


@pytest.fixture
def registro_repo():
    """Fixture para RegistroRepository"""
    return RegistroRepository()


@pytest.fixture
def usuario_teste(db):
    """Fixture para usuário de teste"""
    usuario = Usuario(
        telefone="11999999999",
        nome="Motorista Teste",
        perfil="motorista"
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@pytest.fixture
def empresa_teste(db):
    """Fixture para empresa de teste"""
    empresa = Empresa(
        nome="Transportadora Teste",
        cnpj="12345678000190"
    )
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return empresa


class TestRegistroRepositorioIdempotencia:
    """Testes de idempotência em RegistroRepository"""

    def test_salvar_sem_idempotencia(self, registro_repo, usuario_teste, db):
        """Deve criar novo registro a cada chamada sem idempotency_key"""
        dados = {"quilometros": 100.0}

        # Primeira chamada
        registro1 = registro_repo.salvar(
            usuario_id=usuario_teste.id,
            tipo="registrar_km",
            dados=dados,
            db=db
        )

        # Segunda chamada com mesmos dados
        registro2 = registro_repo.salvar(
            usuario_id=usuario_teste.id,
            tipo="registrar_km",
            dados=dados,
            db=db
        )

        # Devem ser registros diferentes
        assert registro1.id != registro2.id
        assert len(db.query(Registro).all()) == 2

    def test_salvar_idempotente_requisicao_duplicada(
        self,
        registro_repo,
        usuario_teste,
        db
    ):
        """Deve retornar mesmo registro para requisição duplicada"""
        dados = {"quilometros": 120.5}
        idempotency_key = "uuid-12345"

        # Primeira requisição
        registro1, foi_criado1 = registro_repo.salvar_idempotente(
            usuario_id=usuario_teste.id,
            tipo="registrar_km",
            dados=dados,
            idempotency_key=idempotency_key,
            db=db
        )

        # Segunda requisição com mesma idempotency_key (duplicada)
        registro2, foi_criado2 = registro_repo.salvar_idempotente(
            usuario_id=usuario_teste.id,
            tipo="registrar_km",
            dados=dados,
            idempotency_key=idempotency_key,
            db=db
        )

        # Devem ser o mesmo registro
        assert registro1.id == registro2.id
        assert foi_criado1 is True
        assert foi_criado2 is False
        assert len(db.query(Registro).all()) == 1

    def test_salvar_idempotente_requisicoes_diferentes(
        self,
        registro_repo,
        usuario_teste,
        db
    ):
        """Deve criar registros diferentes para idempotency_keys diferentes"""
        dados = {"quilometros": 100.0}

        # Primeira requisição
        registro1, _ = registro_repo.salvar_idempotente(
            usuario_id=usuario_teste.id,
            tipo="registrar_km",
            dados=dados,
            idempotency_key="uuid-1",
            db=db
        )

        # Segunda requisição com idempotency_key diferente
        registro2, _ = registro_repo.salvar_idempotente(
            usuario_id=usuario_teste.id,
            tipo="registrar_km",
            dados=dados,
            idempotency_key="uuid-2",
            db=db
        )

        # Devem ser registros diferentes
        assert registro1.id != registro2.id
        assert len(db.query(Registro).all()) == 2

    def test_salvar_idempotente_tipos_diferentes(
        self,
        registro_repo,
        usuario_teste,
        db
    ):
        """Deve criar registros diferentes para tipos diferentes"""
        idempotency_key = "uuid-duplicado"

        # Registro 1: registrar_km
        registro1, _ = registro_repo.salvar_idempotente(
            usuario_id=usuario_teste.id,
            tipo="registrar_km",
            dados={"quilometros": 100.0},
            idempotency_key=idempotency_key,
            db=db
        )

        # Registro 2: registrar_viagem com mesma idempotency_key
        # Devem ser diferentes porque tipo é diferente
        registro2, _ = registro_repo.salvar_idempotente(
            usuario_id=usuario_teste.id,
            tipo="registrar_viagem",
            dados={"origem": "SP", "destino": "RJ"},
            idempotency_key=idempotency_key,
            db=db
        )

        # Devem ser registros diferentes
        assert registro1.id != registro2.id
        assert registro1.tipo != registro2.tipo
        assert len(db.query(Registro).all()) == 2

    def test_buscar_por_idempotency_key(
        self,
        registro_repo,
        usuario_teste,
        db
    ):
        """Deve encontrar registro por idempotency_key"""
        dados = {"quilometros": 150.0}
        idempotency_key = "uuid-search"

        # Criar registro
        registro_criado, _ = registro_repo.salvar_idempotente(
            usuario_id=usuario_teste.id,
            tipo="registrar_km",
            dados=dados,
            idempotency_key=idempotency_key,
            db=db
        )

        # Buscar pelo idempotency_key
        registro_encontrado = registro_repo.buscar_por_idempotency_key(
            usuario_id=usuario_teste.id,
            tipo="registrar_km",
            idempotency_key=idempotency_key,
            db=db
        )

        assert registro_encontrado is not None
        assert registro_encontrado.id == registro_criado.id

    def test_buscar_por_idempotency_key_nao_encontrado(
        self,
        registro_repo,
        usuario_teste,
        db
    ):
        """Deve retornar None quando idempotency_key não existe"""
        registro = registro_repo.buscar_por_idempotency_key(
            usuario_id=usuario_teste.id,
            tipo="registrar_km",
            idempotency_key="uuid-inexistente",
            db=db
        )

        assert registro is None

    def test_salvar_idempotente_com_viagem_id(
        self,
        registro_repo,
        usuario_teste,
        db
    ):
        """Deve salvar idempotente com viagem_id"""
        from app.models import Viagem

        # Criar viagem
        viagem = Viagem(usuario_id=usuario_teste.id)
        db.add(viagem)
        db.commit()
        db.refresh(viagem)

        # Salvar com viagem_id
        registro, _ = registro_repo.salvar_idempotente(
            usuario_id=usuario_teste.id,
            tipo="registrar_km",
            dados={"quilometros": 100.0},
            idempotency_key="uuid-com-viagem",
            viagem_id=viagem.id,
            db=db
        )

        assert registro.viagem_id == viagem.id

    def test_salvar_idempotente_com_empresa_id(
        self,
        registro_repo,
        usuario_teste,
        empresa_teste,
        db
    ):
        """Deve salvar idempotente com empresa_id"""
        registro, _ = registro_repo.salvar_idempotente(
            usuario_id=usuario_teste.id,
            tipo="registrar_km",
            dados={"quilometros": 100.0},
            idempotency_key="uuid-com-empresa",
            empresa_id=empresa_teste.id,
            db=db
        )

        assert registro.empresa_id == empresa_teste.id

    def test_salvar_idempotente_criado_em_registrado(
        self,
        registro_repo,
        usuario_teste,
        db
    ):
        """Deve registrar criado_em corretamente"""
        antes = datetime.now(timezone.utc)

        registro, _ = registro_repo.salvar_idempotente(
            usuario_id=usuario_teste.id,
            tipo="registrar_km",
            dados={"quilometros": 100.0},
            idempotency_key="uuid-tempo",
            db=db
        )

        depois = datetime.now(timezone.utc)

        assert antes <= registro.criado_em <= depois

    def test_salvar_idempotente_usuarios_diferentes(
        self,
        registro_repo,
        db
    ):
        """Requisições de usuários diferentes devem criar registros diferentes"""
        from app.models import Usuario

        # Criar dois usuários
        usuario1 = Usuario(telefone="11111111111", perfil="motorista")
        usuario2 = Usuario(telefone="22222222222", perfil="motorista")
        db.add_all([usuario1, usuario2])
        db.commit()
        db.refresh(usuario1)
        db.refresh(usuario2)

        idempotency_key = "uuid-shared"

        # Mesmo idempotency_key, usuários diferentes
        registro1, _ = registro_repo.salvar_idempotente(
            usuario_id=usuario1.id,
            tipo="registrar_km",
            dados={"quilometros": 100.0},
            idempotency_key=idempotency_key,
            db=db
        )

        registro2, _ = registro_repo.salvar_idempotente(
            usuario_id=usuario2.id,
            tipo="registrar_km",
            dados={"quilometros": 100.0},
            idempotency_key=idempotency_key,
            db=db
        )

        # Devem ser registros diferentes (usuários diferentes)
        assert registro1.id != registro2.id
        assert registro1.usuario_id != registro2.usuario_id