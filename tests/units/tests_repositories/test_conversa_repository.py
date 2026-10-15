"""
Testes para ConversaRepository.

Valida:
- Criar nova conversa
- Buscar conversa por ID
- Buscar conversa por usuário
- Adicionar mensagem ao histórico
- Obter últimas mensagens
- Atualizar contexto
- Limpar histórico
- Validações e tratamento de erros
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from app.repositories.conversa_repository import ConversaRepository
from app.models import Conversa


class TestConversaRepository:
    """Testes para ConversaRepository."""

    @pytest.fixture
    def repository(self):
        """Instancia um novo repositório."""
        return ConversaRepository()

    @pytest.fixture
    def mock_db(self):
        """Mock da sessão do banco de dados."""
        return MagicMock()

    @pytest.fixture
    def mock_conversa(self):
        """Mock de uma conversa."""
        conversa = MagicMock(spec=Conversa)
        conversa.id = 1
        conversa.usuario_id = 123
        conversa.mensagens = []
        conversa.contexto = {}
        conversa.criado_em = datetime.utcnow()
        conversa.atualizado_em = datetime.utcnow()
        return conversa

    def test_criar_conversa(self, repository, mock_db):
        """Deve criar uma nova conversa."""
        usuario_id = 123
        contexto = {"viagem_id": 1}

        result = repository.criar(
            usuario_id,
            contexto,
            mock_db
        )

        assert isinstance(result, Conversa)
        assert result.usuario_id == usuario_id
        assert result.contexto == contexto
        assert result.mensagens == []
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_criar_conversa_sem_contexto(self, repository, mock_db):
        """Deve criar conversa com contexto vazio."""
        usuario_id = 123

        result = repository.criar(
            usuario_id,
            None,
            mock_db
        )

        assert result.usuario_id == usuario_id
        assert result.contexto == {}

    def test_buscar_conversa_por_id(self, repository, mock_db, mock_conversa):
        """Deve buscar conversa por ID."""
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_conversa
        )

        result = repository.buscar_por_id(1, mock_db)

        assert result.id == 1
        assert result.usuario_id == 123
        mock_db.query.assert_called_once()

    def test_buscar_conversa_por_id_nao_encontrada(self, repository, mock_db):
        """Deve retornar None se conversa não existe."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = repository.buscar_por_id(999, mock_db)

        assert result is None

    def test_buscar_conversa_por_usuario(self, repository, mock_db, mock_conversa):
        """Deve buscar conversa mais recente por usuário."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = (
            mock_conversa
        )

        result = repository.buscar_por_usuario(123, mock_db)

        assert result.usuario_id == 123
        mock_db.query.assert_called_once()

    def test_buscar_conversa_por_usuario_nao_encontrada(self, repository, mock_db):
        """Deve retornar None se usuário não tem conversa."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = (
            None
        )

        result = repository.buscar_por_usuario(999, mock_db)

        assert result is None

    def test_adicionar_mensagem_usuario(self, repository, mock_db, mock_conversa):
        """Deve adicionar mensagem do usuário."""
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_conversa
        )

        result = repository.adicionar_mensagem(
            1,
            "user",
            "Qual é minha quilometragem?",
            db=mock_db
        )

        assert len(result.mensagens) == 1
        assert result.mensagens[0]["role"] == "user"
        assert result.mensagens[0]["content"] == "Qual é minha quilometragem?"

    def test_adicionar_mensagem_assistente(self, repository, mock_db, mock_conversa):
        """Deve adicionar mensagem do assistente."""
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_conversa
        )

        result = repository.adicionar_mensagem(
            1,
            "assistant",
            "Sua quilometragem é 1500 km",
            db=mock_db
        )

        assert len(result.mensagens) == 1
        assert result.mensagens[0]["role"] == "assistant"
        assert result.mensagens[0]["content"] == "Sua quilometragem é 1500 km"

    def test_adicionar_mensagem_com_timestamp_customizado(
        self, repository, mock_db, mock_conversa
    ):
        """Deve usar timestamp fornecido."""
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_conversa
        )
        timestamp = "2026-10-15T10:30:00"

        result = repository.adicionar_mensagem(
            1,
            "user",
            "Teste",
            timestamp,
            mock_db
        )

        assert result.mensagens[0]["timestamp"] == timestamp

    def test_adicionar_mensagem_role_invalido(self, repository, mock_db, mock_conversa):
        """Deve rejeitar role inválido."""
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_conversa
        )

        with pytest.raises(ValueError) as exc_info:
            repository.adicionar_mensagem(
                1,
                "moderador",
                "Teste",
                db=mock_db
            )

        assert "Role inválido" in str(exc_info.value)

    def test_adicionar_mensagem_conversa_inexistente(
        self, repository, mock_db
    ):
        """Deve lançar erro se conversa não existe."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError) as exc_info:
            repository.adicionar_mensagem(
                999,
                "user",
                "Teste",
                db=mock_db
            )

        assert "não encontrada" in str(exc_info.value)

    def test_obter_ultimas_mensagens(self, repository, mock_db, mock_conversa):
        """Deve obter as últimas N mensagens."""
        mensagens = [
            {"role": "user", "content": "Msg 1"},
            {"role": "assistant", "content": "Resp 1"},
            {"role": "user", "content": "Msg 2"},
        ]
        mock_conversa.mensagens = mensagens
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_conversa
        )

        result = repository.obter_ultimas_mensagens(1, limite=2, db=mock_db)

        assert len(result) == 2
        assert result[0]["content"] == "Resp 1"
        assert result[1]["content"] == "Msg 2"

    def test_obter_ultimas_mensagens_menos_que_limite(
        self, repository, mock_db, mock_conversa
    ):
        """Deve retornar todas se houver menos do que o limite."""
        mensagens = [
            {"role": "user", "content": "Msg 1"},
            {"role": "assistant", "content": "Resp 1"},
        ]
        mock_conversa.mensagens = mensagens
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_conversa
        )

        result = repository.obter_ultimas_mensagens(1, limite=10, db=mock_db)

        assert len(result) == 2

    def test_obter_ultimas_mensagens_conversa_vazia(
        self, repository, mock_db, mock_conversa
    ):
        """Deve retornar lista vazia se sem mensagens."""
        mock_conversa.mensagens = []
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_conversa
        )

        result = repository.obter_ultimas_mensagens(1, db=mock_db)

        assert result == []

    def test_obter_ultimas_mensagens_conversa_nao_encontrada(
        self, repository, mock_db
    ):
        """Deve retornar lista vazia se conversa não existe."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = repository.obter_ultimas_mensagens(999, db=mock_db)

        assert result == []

    def test_atualizar_contexto(self, repository, mock_db, mock_conversa):
        """Deve atualizar o contexto da conversa."""
        mock_conversa.contexto = {"viagem_id": 1}
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_conversa
        )

        novo_contexto = {"empresa_id": 2}
        result = repository.atualizar_contexto(1, novo_contexto, mock_db)

        assert result.contexto["viagem_id"] == 1
        assert result.contexto["empresa_id"] == 2

    def test_atualizar_contexto_merge(self, repository, mock_db, mock_conversa):
        """Deve fazer merge do novo contexto."""
        mock_conversa.contexto = {"a": 1, "b": 2}
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_conversa
        )

        result = repository.atualizar_contexto(1, {"b": 3, "c": 4}, mock_db)

        assert result.contexto == {"a": 1, "b": 3, "c": 4}

    def test_atualizar_contexto_conversa_inexistente(
        self, repository, mock_db
    ):
        """Deve lançar erro se conversa não existe."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError) as exc_info:
            repository.atualizar_contexto(999, {}, mock_db)

        assert "não encontrada" in str(exc_info.value)

    def test_limpar_historico(self, repository, mock_db, mock_conversa):
        """Deve limpar o histórico de mensagens."""
        mock_conversa.mensagens = [
            {"role": "user", "content": "Msg"},
            {"role": "assistant", "content": "Resp"},
        ]
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_conversa
        )

        result = repository.limpar_historico(1, mock_db)

        assert result.mensagens == []
        mock_db.add.assert_called()
        mock_db.commit.assert_called()

    def test_limpar_historico_conversa_inexistente(
        self, repository, mock_db
    ):
        """Deve lançar erro se conversa não existe."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError) as exc_info:
            repository.limpar_historico(999, mock_db)

        assert "não encontrada" in str(exc_info.value)

    def test_buscar_conversas_usuario(self, repository, mock_db, mock_conversa):
        """Deve buscar todas as conversas de um usuário."""
        mock_conversa2 = MagicMock(spec=Conversa)
        mock_conversa2.id = 2
        mock_conversa2.usuario_id = 123

        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_conversa,
            mock_conversa2,
        ]

        result = repository.buscar_conversas_usuario(123, limite=10, db=mock_db)

        assert len(result) == 2
        assert all(c.usuario_id == 123 for c in result)

    def test_buscar_conversas_usuario_vazio(self, repository, mock_db):
        """Deve retornar lista vazia se usuário não tem conversas."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = (
            []
        )

        result = repository.buscar_conversas_usuario(999, db=mock_db)

        assert result == []

    def test_adicionar_multiplas_mensagens(
        self, repository, mock_db, mock_conversa
    ):
        """Deve manter histórico de múltiplas mensagens."""
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_conversa
        )

        # Adicionar primeira mensagem
        repository.adicionar_mensagem(
            1, "user", "Primeira", db=mock_db
        )
        # Adicionar segunda mensagem
        repository.adicionar_mensagem(
            1, "assistant", "Resposta", db=mock_db
        )

        assert len(mock_conversa.mensagens) == 2
        assert mock_conversa.mensagens[0]["role"] == "user"
        assert mock_conversa.mensagens[1]["role"] == "assistant"
