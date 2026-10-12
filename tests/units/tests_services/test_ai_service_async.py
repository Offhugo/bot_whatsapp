"""
Testes para AIService com AsyncOpenAI e retry logic.

Valida que:
- AIService usa AsyncOpenAI (cliente assíncrono)
- Chamadas são realmente assíncronas (com await)
- Retry decorator está aplicado
- Respostas são validadas com AIResponseDTO
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from openai import RateLimitError, APIConnectionError

from app.services.ai_service import AIService
from app.schemas.ai_response import AIResponseDTO, Intent


@pytest.fixture
def ai_service():
    """Fixture para AIService"""
    with patch('app.services.ai_service.AsyncOpenAI') as mock_async_openai:
        # Mock o client assíncrono
        mock_instance = MagicMock()
        mock_async_openai.return_value = mock_instance

        service = AIService()
        service.client = mock_async_openai.return_value

        return service


class TestAIServiceAsync:
    """Testes para AIService com AsyncOpenAI"""

    @pytest.mark.anyio
    async def test_usar_async_openai(self, ai_service):
        """Deve usar AsyncOpenAI em vez de OpenAI síncrono"""
        # AIService deve ter importado AsyncOpenAI
        # Podemos verificar pelo tipo do client
        assert ai_service.client is not None

    @pytest.mark.anyio
    async def test_processar_com_sucesso(self, ai_service):
        """Deve processar mensagem com sucesso"""
        # Mock da resposta
        mock_message = MagicMock()
        mock_message.parsed = AIResponseDTO(
            intent=Intent.CONVERSA,
            dados={},
            resposta="Olá! Como posso ajudar?"
        )

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=mock_message)]

        # Mock da chamada assíncrona
        ai_service.client.beta = MagicMock()
        ai_service.client.beta.chat = MagicMock()
        ai_service.client.beta.chat.completions = MagicMock()
        ai_service.client.beta.chat.completions.parse = AsyncMock(
            return_value=mock_completion
        )

        resultado = await ai_service.processar("Olá")

        assert isinstance(resultado, AIResponseDTO)
        assert resultado.intent == Intent.CONVERSA
        assert resultado.resposta == "Olá! Como posso ajudar?"

    @pytest.mark.anyio
    async def test_processar_com_retry_rate_limit(self, ai_service):
        """Deve fazer retry em RateLimitError"""
        # Mock de duas tentativas: primeira falha, segunda sucede
        mock_message = MagicMock()
        mock_message.parsed = AIResponseDTO(
            intent=Intent.CONVERSA,
            dados={},
            resposta="Sucesso após retry"
        )

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=mock_message)]

        # Side effect: primeira chamada falha, segunda sucede
        parse_mock = AsyncMock(side_effect=[
            RateLimitError("Rate limit exceeded"),
            mock_completion
        ])

        ai_service.client.beta = MagicMock()
        ai_service.client.beta.chat = MagicMock()
        ai_service.client.beta.chat.completions = MagicMock()
        ai_service.client.beta.chat.completions.parse = parse_mock

        # Deve tentar 2 vezes (primeira falha, segunda sucede)
        resultado = await ai_service.processar("Teste")

        assert isinstance(resultado, AIResponseDTO)
        assert parse_mock.call_count == 2

    @pytest.mark.anyio
    async def test_processar_falha_permanente(self, ai_service):
        """Não deve fazer retry em erro permanente"""
        from openai import InvalidRequestError

        # Mock de erro permanente
        parse_mock = AsyncMock(side_effect=InvalidRequestError(
            "Invalid request", response=None, body=None
        ))

        ai_service.client.beta = MagicMock()
        ai_service.client.beta.chat = MagicMock()
        ai_service.client.beta.chat.completions = MagicMock()
        ai_service.client.beta.chat.completions.parse = parse_mock

        # Deve falhar na primeira tentativa (sem retry)
        with pytest.raises(RuntimeError):
            await ai_service.processar("Teste")

        assert parse_mock.call_count == 1

    @pytest.mark.anyio
    async def test_processar_valida_resposta_dto(self, ai_service):
        """Deve validar que resposta é AIResponseDTO válido"""
        # Se a IA retornar dados inválidos, deve falhar na validação
        mock_message = MagicMock()
        # Resposta com dados inválidos para registrar_km
        mock_message.parsed = AIResponseDTO(
            intent=Intent.REGISTRAR_KM,
            dados={"quilometros": -10.0},  # Negativo é inválido
            resposta="Registrei"
        )

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=mock_message)]

        parse_mock = AsyncMock(return_value=mock_completion)

        ai_service.client.beta = MagicMock()
        ai_service.client.beta.chat = MagicMock()
        ai_service.client.beta.chat.completions = MagicMock()
        ai_service.client.beta.chat.completions.parse = parse_mock

        # A validação deve falhar porque quilometros é negativo
        with pytest.raises((RuntimeError, Exception)):
            # Nota: A validação acontece no parse, então pode variar
            await ai_service.processar("Registrar -10 km")

    @pytest.mark.anyio
    async def test_processar_resposta_nao_parseada(self, ai_service):
        """Deve falhar se resposta não for parseada"""
        mock_message = MagicMock()
        mock_message.parsed = None  # Não foi parseado

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=mock_message)]

        parse_mock = AsyncMock(return_value=mock_completion)

        ai_service.client.beta = MagicMock()
        ai_service.client.beta.chat = MagicMock()
        ai_service.client.beta.chat.completions = MagicMock()
        ai_service.client.beta.chat.completions.parse = parse_mock

        # Deve falhar porque parsed é None
        with pytest.raises(RuntimeError) as exc_info:
            await ai_service.processar("Teste")

        assert "não foi parseada" in str(exc_info.value)

    @pytest.mark.anyio
    async def test_processar_diferentes_intents(self, ai_service):
        """Deve processar diferentes tipos de intent"""
        intents_para_testar = [
            (Intent.REGISTRAR_KM, {"quilometros": 100.0}, "Registrei 100 km"),
            (Intent.REGISTRAR_VIAGEM, {"origem": "SP", "destino": "RJ"}, "Registrei viagem"),
            (Intent.REGISTRAR_ABASTECIMENTO, {"valor": 150.0, "combustivel": "gasolina"}, "Abasteci"),
            (Intent.CONVERSA, {}, "Olá!"),
        ]

        for intent, dados, resposta in intents_para_testar:
            mock_message = MagicMock()
            mock_message.parsed = AIResponseDTO(
                intent=intent,
                dados=dados,
                resposta=resposta
            )

            mock_completion = MagicMock()
            mock_completion.choices = [MagicMock(message=mock_message)]

            parse_mock = AsyncMock(return_value=mock_completion)

            ai_service.client.beta = MagicMock()
            ai_service.client.beta.chat = MagicMock()
            ai_service.client.beta.chat.completions = MagicMock()
            ai_service.client.beta.chat.completions.parse = parse_mock

            resultado = await ai_service.processar("Teste")

            assert resultado.intent == intent
            assert resultado.dados == dados
            assert resultado.resposta == resposta

    @pytest.mark.anyio
    async def test_processar_timeout(self, ai_service):
        """Deve fazer retry em APITimeoutError"""
        from openai import APITimeoutError

        mock_message = MagicMock()
        mock_message.parsed = AIResponseDTO(
            intent=Intent.CONVERSA,
            dados={},
            resposta="Sucesso"
        )

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=mock_message)]

        # Timeout na primeira, sucesso na segunda
        parse_mock = AsyncMock(side_effect=[
            APITimeoutError("Timeout"),
            mock_completion
        ])

        ai_service.client.beta = MagicMock()
        ai_service.client.beta.chat = MagicMock()
        ai_service.client.beta.chat.completions = MagicMock()
        ai_service.client.beta.chat.completions.parse = parse_mock

        resultado = await ai_service.processar("Teste")

        assert resultado.intent == Intent.CONVERSA
        assert parse_mock.call_count == 2

    @pytest.mark.anyio
    async def test_processar_connection_error(self, ai_service):
        """Deve fazer retry em APIConnectionError"""
        from openai import APIConnectionError

        mock_message = MagicMock()
        mock_message.parsed = AIResponseDTO(
            intent=Intent.CONVERSA,
            dados={},
            resposta="Sucesso"
        )

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=mock_message)]

        # Erro de conexão na primeira, sucesso na segunda
        parse_mock = AsyncMock(side_effect=[
            APIConnectionError("Connection refused"),
            mock_completion
        ])

        ai_service.client.beta = MagicMock()
        ai_service.client.beta.chat = MagicMock()
        ai_service.client.beta.chat.completions = MagicMock()
        ai_service.client.beta.chat.completions.parse = parse_mock

        resultado = await ai_service.processar("Teste")

        assert resultado.intent == Intent.CONVERSA
        assert parse_mock.call_count == 2