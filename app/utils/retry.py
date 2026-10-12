"""
Utilitários para retry com backoff exponencial.

Fornece decorators e funções para retry automático de operações
que podem falhar temporariamente (como chamadas a APIs).
"""

import asyncio
import functools
import logging
import time
from typing import Callable, Optional, Type, TypeVar, Union

from openai import (
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    APIError,
    OpenAIError,
)


logger = logging.getLogger(__name__)

T = TypeVar('T')


# ============================================================
# Configurações de Retry
# ============================================================

class RetryConfig:
    """Configuração para comportamento de retry"""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 32.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        """
        Args:
            max_attempts: Máximo de tentativas (padrão: 3)
            initial_delay: Delay inicial em segundos (padrão: 1.0s)
            max_delay: Delay máximo em segundos (padrão: 32.0s)
            exponential_base: Base para exponencial (padrão: 2.0)
            jitter: Adicionar jitter ao delay (padrão: True)
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """
        Calcula o delay para uma tentativa específica.

        Usa backoff exponencial com cap e jitter opcional.

        Args:
            attempt: Número da tentativa (0-indexed)

        Returns:
            Delay em segundos
        """
        # Backoff exponencial: inicial_delay * (exponential_base ^ attempt)
        delay = self.initial_delay * (self.exponential_base ** attempt)

        # Cap no máximo delay
        delay = min(delay, self.max_delay)

        # Adicionar jitter (±10%)
        if self.jitter:
            jitter_amount = delay * 0.1
            delay = delay + (jitter_amount * (2 * (time.time() % 1) - 1))

        return max(delay, self.initial_delay)


# ============================================================
# Classificação de Erros
# ============================================================

def _should_retry(exception: Exception) -> bool:
    """
    Determina se um erro deve ser retentado.

    Alguns erros são transitórios e merecem retry:
    - RateLimitError: API está sobrecarregada, vai passar
    - APIConnectionError: Problema de conexão, pode se recuperar
    - APITimeoutError: Timeout, pode tentar novamente

    Outros erros são permanentes e não devem ser retentados:
    - InvalidRequestError: Erro na requisição (cliente culpa), sem retry
    - AuthenticationError: Erro de autenticação, sem retry
    - NotFoundError: Recurso não existe, sem retry

    Args:
        exception: Exceção a classificar

    Returns:
        True se deve fazer retry, False senão
    """
    # Erros transitórios que devem ser retentados
    retryable_errors = (
        RateLimitError,
        APIConnectionError,
        APITimeoutError,
    )

    if isinstance(exception, retryable_errors):
        return True

    # Outros erros da OpenAI não devem ser retentados
    if isinstance(exception, OpenAIError):
        return False

    # Por padrão, não fazer retry
    return False


def _log_retry(
    exception: Exception,
    attempt: int,
    delay: float,
    context: str = ""
) -> None:
    """
    Loga informações sobre um retry.

    Args:
        exception: Exceção que causou o retry
        attempt: Número da tentativa
        delay: Delay até próxima tentativa
        context: Contexto adicional para logging
    """
    logger.warning(
        f"Retry #{attempt}: {type(exception).__name__}: {str(exception)}. "
        f"Aguardando {delay:.1f}s antes de próxima tentativa. {context}"
    )


# ============================================================
# Decorator para Retry Síncrono
# ============================================================

def retry_with_backoff(
    config: Optional[RetryConfig] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator para retry automático com backoff exponencial.

    Uso:
        @retry_with_backoff()
        def chamar_api():
            # Pode falhar com erro transitório
            pass

    Args:
        config: RetryConfig customizada (padrão: RetryConfig())

    Returns:
        Decorator
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception: Optional[Exception] = None

            for attempt in range(config.max_attempts):
                try:
                    result = func(*args, **kwargs)

                    if attempt > 0:
                        logger.info(
                            f"Sucesso após {attempt} tentativas em {func.__name__}"
                        )

                    return result

                except Exception as e:
                    last_exception = e

                    # Se não deve fazer retry, relança imediatamente
                    if not _should_retry(e):
                        logger.error(
                            f"Erro não-retentável em {func.__name__}: "
                            f"{type(e).__name__}: {str(e)}"
                        )
                        raise

                    # Se foi última tentativa, relança
                    if attempt == config.max_attempts - 1:
                        logger.error(
                            f"Esgotadas {config.max_attempts} tentativas "
                            f"em {func.__name__}: {type(e).__name__}"
                        )
                        raise

                    # Calcular delay e aguardar
                    delay = config.get_delay(attempt)
                    _log_retry(
                        e,
                        attempt + 1,
                        delay,
                        f"(função: {func.__name__})"
                    )
                    time.sleep(delay)

            # Nunca deveria chegar aqui, mas por segurança
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


# ============================================================
# Decorator para Retry Assíncrono
# ============================================================

def async_retry_with_backoff(
    config: Optional[RetryConfig] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator para retry automático com backoff exponencial (assíncrono).

    Uso:
        @async_retry_with_backoff()
        async def chamar_api_async():
            # Pode falhar com erro transitório
            pass

    Args:
        config: RetryConfig customizada (padrão: RetryConfig())

    Returns:
        Decorator
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception: Optional[Exception] = None

            for attempt in range(config.max_attempts):
                try:
                    result = await func(*args, **kwargs)

                    if attempt > 0:
                        logger.info(
                            f"Sucesso após {attempt} tentativas em {func.__name__}"
                        )

                    return result

                except Exception as e:
                    last_exception = e

                    # Se não deve fazer retry, relança imediatamente
                    if not _should_retry(e):
                        logger.error(
                            f"Erro não-retentável em {func.__name__}: "
                            f"{type(e).__name__}: {str(e)}"
                        )
                        raise

                    # Se foi última tentativa, relança
                    if attempt == config.max_attempts - 1:
                        logger.error(
                            f"Esgotadas {config.max_attempts} tentativas "
                            f"em {func.__name__}: {type(e).__name__}"
                        )
                        raise

                    # Calcular delay e aguardar
                    delay = config.get_delay(attempt)
                    _log_retry(
                        e,
                        attempt + 1,
                        delay,
                        f"(função async: {func.__name__})"
                    )
                    await asyncio.sleep(delay)

            # Nunca deveria chegar aqui, mas por segurança
            if last_exception:
                raise last_exception

        return wrapper

    return decorator