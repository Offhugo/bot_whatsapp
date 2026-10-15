"""
Testes para ConversationContextService.

Valida:
- Obter ou criar conversa
- Adicionar mensagens (usuário e assistente)
- Obter histórico formatado para prompt
- Gerenciar contexto
- Renovar conversa
- Limpar histórico
- Tratamento de erros
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from app.services.conversation_context_service import ConversationContextService
from app.models import Conversa


class TestConversationContextService:
    """Testes para ConversationContextService."""

    @pytest.fixture
    def service(self):
        """Cria instância do serviço."""
        return ConversationContextService()

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

    def test_obter_ou_criar_conversa_nova(self, service, mock_db):
        """Deve criar conversa se usuário não tem uma."""
        with patch.object(
            service.repository, "buscar_por_usuario", return_value=None
        ) as mock_buscar:
            with patch.object(
                service.repository, "criar", return_value=MagicMock(spec=Conversa)
            ) as mock_criar:
                result = service.obter_ou_criar_conversa(123, db=mock_db)

                mock_buscar.assert_called_once_with(123, mock_db)
                mock_criar.assert_called_once()
                assert result is not None

    def test_obter_ou_criar_conversa_existente(self, service, mock_db, mock_conversa):
        """Deve retornar conversa existente."""
        with patch.object(
            service.repository,
            "buscar_por_usuario",
            return_value=mock_conversa
        ) as mock_buscar:
            result = service.obter_ou_criar_conversa(123, db=mock_db)

            mock_buscar.assert_called_once_with(123, mock_db)
            assert result == mock_conversa

    def test_obter_ou_criar_com_novo_contexto(
        self, service, mock_db, mock_conversa
    ):
        """Deve atualizar contexto se fornecido."""
        novo_contexto = {"viagem_id": 1}

        with patch.object(
            service.repository,
            "buscar_por_usuario",
            return_value=mock_conversa
        ):
            with patch.object(
                service.repository, "atualizar_contexto"
            ) as mock_atualizar:
                service.obter_ou_criar_conversa(
                    123, novo_contexto, db=mock_db
                )

                mock_atualizar.assert_called_once_with(
                    mock_conversa.id,
                    novo_contexto,
                    mock_db
                )

    def test_adicionar_mensagem_usuario(self, service, mock_db):
        """Deve adicionar mensagem do usuário."""
        with patch.object(
            service.repository, "adicionar_mensagem"
        ) as mock_adicionar:
            service.adicionar_mensagem_usuario(
                1,
                "Qual é minha quilometragem?",
                mock_db
            )

            mock_adicionar.assert_called_once_with(
                1,
                role="user",
                conteudo="Qual é minha quilometragem?",
                db=mock_db
            )

    def test_adicionar_mensagem_assistente(self, service, mock_db):
        """Deve adicionar mensagem do assistente."""
        with patch.object(
            service.repository, "adicionar_mensagem"
        ) as mock_adicionar:
            service.adicionar_mensagem_assistente(
                1,
                "Sua quilometragem é 1500 km",
                mock_db
            )

            mock_adicionar.assert_called_once_with(
                1,
                role="assistant",
                conteudo="Sua quilometragem é 1500 km",
                db=mock_db
            )

    def test_obter_historico_para_prompt(self, service, mock_db):
        """Deve formatar histórico para API."""
        mensagens_db = [
            {"role": "user", "content": "Olá", "timestamp": "2026-10-15T10:00:00"},
            {"role": "assistant", "content": "Oi!", "timestamp": "2026-10-15T10:00:01"},
        ]

        with patch.object(
            service.repository,
            "obter_ultimas_mensagens",
            return_value=mensagens_db
        ):
            result = service.obter_historico_para_prompt(1, db=mock_db)

            assert len(result) == 2
            # Remover timestamp
            assert all("timestamp" not in msg for msg in result)
            assert result[0] == {"role": "user", "content": "Olá"}
            assert result[1] == {"role": "assistant", "content": "Oi!"}

    def test_obter_historico_limit_padrao(self, service, mock_db):
        """Deve usar MAX_HISTORICO como padrão."""
        with patch.object(
            service.repository, "obter_ultimas_mensagens"
        ) as mock_obter:
            service.obter_historico_para_prompt(1, db=mock_db)

            # Deve chamar com MAX_HISTORICO
            call_args = mock_obter.call_args
            assert call_args[0][1] == service.MAX_HISTORICO

    def test_obter_historico_limite_customizado(self, service, mock_db):
        """Deve usar limite fornecido."""
        with patch.object(
            service.repository, "obter_ultimas_mensagens"
        ) as mock_obter:
            service.obter_historico_para_prompt(1, limite=5, db=mock_db)

            call_args = mock_obter.call_args
            assert call_args[0][1] == 5

    def test_obter_historico_vazio(self, service, mock_db):
        """Deve retornar lista vazia se nenhuma mensagem."""
        with patch.object(
            service.repository,
            "obter_ultimas_mensagens",
            return_value=[]
        ):
            result = service.obter_historico_para_prompt(1, db=mock_db)

            assert result == []

    def test_obter_historico_erro(self, service, mock_db):
        """Deve retornar lista vazia em caso de erro."""
        with patch.object(
            service.repository,
            "obter_ultimas_mensagens",
            side_effect=Exception("Erro DB")
        ):
            result = service.obter_historico_para_prompt(1, db=mock_db)

            assert result == []

    def test_obter_contexto(self, service, mock_db, mock_conversa):
        """Deve retornar contexto da conversa."""
        mock_conversa.contexto = {"viagem_id": 1, "empresa_id": 2}

        with patch.object(
            service.repository,
            "buscar_por_id",
            return_value=mock_conversa
        ):
            result = service.obter_contexto(1, mock_db)

            assert result == {"viagem_id": 1, "empresa_id": 2}

    def test_obter_contexto_vazio(self, service, mock_db, mock_conversa):
        """Deve retornar dicionário vazio se contexto é None."""
        mock_conversa.contexto = None

        with patch.object(
            service.repository,
            "buscar_por_id",
            return_value=mock_conversa
        ):
            result = service.obter_contexto(1, mock_db)

            assert result == {}

    def test_obter_contexto_conversa_nao_encontrada(self, service, mock_db):
        """Deve retornar dicionário vazio se conversa não existe."""
        with patch.object(
            service.repository, "buscar_por_id", return_value=None
        ):
            result = service.obter_contexto(999, mock_db)

            assert result == {}

    def test_renovar_conversa(self, service, mock_db):
        """Deve criar nova conversa."""
        nova_conversa = MagicMock(spec=Conversa)
        novo_contexto = {"viagem_id": 2}

        with patch.object(
            service.repository, "criar", return_value=nova_conversa
        ) as mock_criar:
            result = service.renovar_conversa(123, novo_contexto, mock_db)

            mock_criar.assert_called_once_with(123, novo_contexto, mock_db)
            assert result == nova_conversa

    def test_limpar_historico(self, service, mock_db):
        """Deve limpar histórico da conversa."""
        with patch.object(
            service.repository, "limpar_historico"
        ) as mock_limpar:
            service.limpar_historico(1, mock_db)

            mock_limpar.assert_called_once_with(1, mock_db)

    def test_obter_tamanho_historico(self, service, mock_db, mock_conversa):
        """Deve retornar número de mensagens."""
        mock_conversa.mensagens = [
            {"role": "user", "content": "Msg 1"},
            {"role": "assistant", "content": "Resp 1"},
        ]

        with patch.object(
            service.repository,
            "buscar_por_id",
            return_value=mock_conversa
        ):
            result = service.obter_tamanho_historico(1, mock_db)

            assert result == 2

    def test_obter_tamanho_historico_vazio(
        self, service, mock_db, mock_conversa
    ):
        """Deve retornar 0 se sem mensagens."""
        mock_conversa.mensagens = []

        with patch.object(
            service.repository,
            "buscar_por_id",
            return_value=mock_conversa
        ):
            result = service.obter_tamanho_historico(1, mock_db)

            assert result == 0

    def test_obter_tamanho_historico_conversa_nao_encontrada(
        self, service, mock_db
    ):
        """Deve retornar 0 se conversa não existe."""
        with patch.object(
            service.repository, "buscar_por_id", return_value=None
        ):
            result = service.obter_tamanho_historico(999, mock_db)

            assert result == 0

    def test_obter_ultima_mensagem(self, service, mock_db):
        """Deve retornar última mensagem."""
        ultima = {"role": "assistant", "content": "Última"}

        with patch.object(
            service.repository,
            "obter_ultimas_mensagens",
            return_value=[ultima]
        ):
            result = service.obter_ultima_mensagem(1, mock_db)

            assert result == ultima

    def test_obter_ultima_mensagem_vazio(self, service, mock_db):
        """Deve retornar None se sem histórico."""
        with patch.object(
            service.repository,
            "obter_ultimas_mensagens",
            return_value=[]
        ):
            result = service.obter_ultima_mensagem(1, mock_db)

            assert result is None

    def test_obter_ultima_mensagem_erro(self, service, mock_db):
        """Deve retornar None em caso de erro."""
        with patch.object(
            service.repository,
            "obter_ultimas_mensagens",
            side_effect=Exception("Erro")
        ):
            result = service.obter_ultima_mensagem(1, mock_db)

            assert result is None

    def test_fluxo_completo_conversa(self, service, mock_db, mock_conversa):
        """Deve executar fluxo completo de conversa."""
        # Obter ou criar
        with patch.object(
            service.repository,
            "buscar_por_usuario",
            return_value=None
        ):
            with patch.object(
                service.repository,
                "criar",
                return_value=mock_conversa
            ):
                conversa = service.obter_ou_criar_conversa(123, db=mock_db)

        # Adicionar mensagem
        with patch.object(
            service.repository, "adicionar_mensagem"
        ) as mock_add:
            service.adicionar_mensagem_usuario(
                conversa.id,
                "Olá",
                mock_db
            )
            mock_add.assert_called_once()

        # Obter histórico
        with patch.object(
            service.repository,
            "obter_ultimas_mensagens",
            return_value=[{"role": "user", "content": "Olá"}]
        ):
            historico = service.obter_historico_para_prompt(
                conversa.id,
                db=mock_db
            )
            assert len(historico) == 1

    def test_max_historico_attribute(self, service):
        """Deve ter MAX_HISTORICO configurado."""
        assert hasattr(service, "MAX_HISTORICO")
        assert service.MAX_HISTORICO == 20

    def test_adicionar_mensagem_erro_propagado(self, service, mock_db):
        """Deve propagar erro ao adicionar mensagem."""
        with patch.object(
            service.repository,
            "adicionar_mensagem",
            side_effect=ValueError("Erro")
        ):
            with pytest.raises(ValueError):
                service.adicionar_mensagem_usuario(
                    1,
                    "Teste",
                    mock_db
                )

    def test_renovar_conversa_erro_propagado(self, service, mock_db):
        """Deve propagar erro ao renovar conversa."""
        with patch.object(
            service.repository,
            "criar",
            side_effect=Exception("Erro DB")
        ):
            with pytest.raises(Exception):
                service.renovar_conversa(123, db=mock_db)

    def test_obter_ou_criar_with_exception_fallback(
        self, service, mock_db
    ):
        """Deve continuar mesmo com erro no histórico."""
        with patch.object(
            service.repository,
            "buscar_por_usuario",
            side_effect=Exception("Erro DB")
        ):
            with pytest.raises(Exception):
                service.obter_ou_criar_conversa(123, db=mock_db)
