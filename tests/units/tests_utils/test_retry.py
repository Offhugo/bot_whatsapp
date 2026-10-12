"""
Testes para utilitários de retry com backoff exponencial.

Valida que:
- Retry acontece para erros transitórios
- Não faz retry para erros permanentes
- Backoff exponencial funciona corretamente
- Jitter adiciona variância (evita thundering herd)
"""

import asyncio
import pytest
from unittest.mock import Mock, patch
from openai import RateLimitError, APIConnectionError, APITimeoutError, InvalidRequestError

from app.utils.retry import (
    RetryConfig,
    retry_with_backoff,
    async_retry_with_backoff,
    _should_retry,
)


class TestRetryConfig:
    """Testes para configuração de retry"""

    def test_delay_inicial(self):
        """Deve retornar delay inicial na primeira tentativa"""
        config = RetryConfig(
            initial_delay=1.0,
            exponential_base=2.0,
            jitter=False
        )

        delay = config.get_delay(0)
        assert delay == 1.0

    def test_delay_exponencial(self):
        """Deve crescer exponencialmente"""
        config = RetryConfig(
            initial_delay=1.0,
            exponential_base=2.0,
            jitter=False
        )

        delay_0 = config.get_delay(0)  # 1.0
        delay_1 = config.get_delay(1)  # 2.0
        delay_2 = config.get_delay(2)  # 4.0

        assert delay_0 == 1.0
        assert delay_1 == 2.0
        assert delay_2 == 4.0

    def test_delay_com_cap_maximo(self):
        """Deve respeitar cap máximo de delay"""
        config = RetryConfig(
            initial_delay=1.0,
            max_delay=5.0,
            exponential_base=2.0,
            jitter=False
        )

        delay_0 = config.get_delay(0)  # 1.0
        delay_1 = config.get_delay(1)  # 2.0
        delay_2 = config.get_delay(2)  # 4.0
        delay_3 = config.get_delay(3)  # 8.0 -> capped to 5.0
        delay_4 = config.get_delay(4)  # 16.0 -> capped to 5.0

        assert delay_0 == 1.0
        assert delay_1 == 2.0
        assert delay_2 == 4.0
        assert delay_3 == 5.0
        assert delay_4 == 5.0

    def test_delay_com_jitter(self):
        """Delay com jitter deve variar"""
        config = RetryConfig(
            initial_delay=10.0,
            exponential_base=2.0,
            jitter=True
        )

        delays = [config.get_delay(0) for _ in range(10)]

        # Com jitter, delays devem variar (não serem todos iguais)
        assert len(set(delays)) > 1

        # Mas todos devem estar próximos a 10.0 (±10%)
        for delay in delays:
            assert 9.0 <= delay <= 11.0


class TestShouldRetry:
    """Testes para classificação de erros"""

    def test_retry_rate_limit_error(self):
        """Deve fazer retry em RateLimitError"""
        error = RateLimitError("Rate limit exceeded")
        assert _should_retry(error) is True

    def test_retry_api_connection_error(self):
        """Deve fazer retry em APIConnectionError"""
        error = APIConnectionError("Connection failed")
        assert _should_retry(error) is True

    def test_retry_api_timeout_error(self):
        """Deve fazer retry em APITimeoutError"""
        error = APITimeoutError("Timeout")
        assert _should_retry(error) is True

    def test_nao_retry_invalid_request(self):
        """Não deve fazer retry em InvalidRequestError"""
        error = InvalidRequestError("Invalid request", response=None, body=None)
        assert _should_retry(error) is False

    def test_nao_retry_generic_exception(self):
        """Não deve fazer retry em exceção genérica"""
        error = Exception("Generic error")
        assert _should_retry(error) is False


class TestRetryWithBackoffSincrono:
    """Testes para decorator de retry síncrono"""

    def test_sucesso_primeira_tentativa(self):
        """Deve retornar resultado na primeira tentativa"""
        mock_func = Mock(return_value="sucesso")

        @retry_with_backoff()
        def funcao():
            return mock_func()

        resultado = funcao()

        assert resultado == "sucesso"
        assert mock_func.call_count == 1

    def test_retry_apos_erro_transitorio(self):
        """Deve fazer retry após erro transitório"""
        mock_func = Mock(side_effect=[
            RateLimitError("Rate limit"),
            "sucesso"
        ])

        @retry_with_backoff(RetryConfig(max_attempts=3))
        def funcao():
            return mock_func()

        resultado = funcao()

        assert resultado == "sucesso"
        assert mock_func.call_count == 2

    def test_nao_retry_apos_erro_permanente(self):
        """Não deve fazer retry após erro permanente"""
        mock_func = Mock(side_effect=InvalidRequestError(
            "Invalid request", response=None, body=None
        ))

        @retry_with_backoff(RetryConfig(max_attempts=3))
        def funcao():
            return mock_func()

        with pytest.raises(InvalidRequestError):
            funcao()

        assert mock_func.call_count == 1

    def test_esgota_tentativas(self):
        """Deve lançar exceção após esgotar tentativas"""
        mock_func = Mock(side_effect=RateLimitError("Rate limit"))

        @retry_with_backoff(RetryConfig(max_attempts=2))
        def funcao():
            return mock_func()

        with pytest.raises(RateLimitError):
            funcao()

        assert mock_func.call_count == 2

    def test_delay_entre_tentativas(self):
        """Deve aguardar entre tentativas"""
        mock_func = Mock(side_effect=[
            APIConnectionError("Connection error"),
            "sucesso"
        ])

        config = RetryConfig(max_attempts=2, initial_delay=0.1, jitter=False)

        with patch('time.sleep') as mock_sleep:
            @retry_with_backoff(config)
            def funcao():
                return mock_func()

            resultado = funcao()

            assert resultado == "sucesso"
            assert mock_sleep.call_count == 1
            mock_sleep.assert_called_with(0.1)

    def test_multiplos_retries(self):
        """Deve fazer múltiplas tentativas com backoff"""
        mock_func = Mock(side_effect=[
            RateLimitError("Rate limit"),
            RateLimitError("Rate limit"),
            "sucesso"
        ])

        config = RetryConfig(max_attempts=3, initial_delay=0.05, jitter=False)

        with patch('time.sleep') as mock_sleep:
            @retry_with_backoff(config)
            def funcao():
                return mock_func()

            resultado = funcao()

            assert resultado == "sucesso"
            assert mock_func.call_count == 3
            assert mock_sleep.call_count == 2


class TestAsyncRetryWithBackoff:
    """Testes para decorator de retry assíncrono"""

    @pytest.mark.anyio
    async def test_sucesso_primeira_tentativa_async(self):
        """Deve retornar resultado na primeira tentativa (async)"""
        mock_func = Mock(return_value="sucesso")

        @async_retry_with_backoff()
        async def funcao():
            return mock_func()

        resultado = await funcao()

        assert resultado == "sucesso"
        assert mock_func.call_count == 1

    @pytest.mark.anyio
    async def test_retry_apos_erro_transitorio_async(self):
        """Deve fazer retry após erro transitório (async)"""
        tentativas = 0

        @async_retry_with_backoff(RetryConfig(max_attempts=3))
        async def funcao():
            nonlocal tentativas
            tentativas += 1
            if tentativas == 1:
                raise RateLimitError("Rate limit")
            return "sucesso"

        resultado = await funcao()

        assert resultado == "sucesso"
        assert tentativas == 2

    @pytest.mark.anyio
    async def test_nao_retry_apos_erro_permanente_async(self):
        """Não deve fazer retry após erro permanente (async)"""
        tentativas = 0

        @async_retry_with_backoff(RetryConfig(max_attempts=3))
        async def funcao():
            nonlocal tentativas
            tentativas += 1
            raise InvalidRequestError("Invalid request", response=None, body=None)

        with pytest.raises(InvalidRequestError):
            await funcao()

        assert tentativas == 1

    @pytest.mark.anyio
    async def test_delay_entre_tentativas_async(self):
        """Deve aguardar entre tentativas (async)"""
        tentativas = 0

        config = RetryConfig(max_attempts=2, initial_delay=0.05, jitter=False)

        with patch('asyncio.sleep', new_callable=lambda: Mock(return_value=asyncio.sleep(0))) as mock_sleep:
            @async_retry_with_backoff(config)
            async def funcao():
                nonlocal tentativas
                tentativas += 1
                if tentativas == 1:
                    raise APIConnectionError("Connection error")
                return "sucesso"

            resultado = await funcao()

            assert resultado == "sucesso"
            assert tentativas == 2

    @pytest.mark.anyio
    async def test_multiplos_retries_async(self):
        """Deve fazer múltiplas tentativas com backoff (async)"""
        tentativas = 0

        config = RetryConfig(max_attempts=3, initial_delay=0.01, jitter=False)

        @async_retry_with_backoff(config)
        async def funcao():
            nonlocal tentativas
            tentativas += 1
            if tentativas < 3:
                raise RateLimitError("Rate limit")
            return "sucesso"

        resultado = await funcao()

        assert resultado == "sucesso"
        assert tentativas == 3

    @pytest.mark.anyio
    async def test_esgota_tentativas_async(self):
        """Deve lançar exceção após esgotar tentativas (async)"""
        tentativas = 0

        @async_retry_with_backoff(RetryConfig(max_attempts=2))
        async def funcao():
            nonlocal tentativas
            tentativas += 1
            raise RateLimitError("Rate limit")

        with pytest.raises(RateLimitError):
            await funcao()

        assert tentativas == 2