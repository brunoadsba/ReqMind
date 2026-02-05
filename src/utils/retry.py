"""Retry decorator com exponential backoff"""

import functools
import asyncio
import random
import logging
from typing import Callable, Any, TypeVar, Optional, Tuple

logger = logging.getLogger(__name__)

T = TypeVar("T")


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    exceptions: Tuple[type, ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """
    Decorator para retry com exponential backoff

    Args:
        max_retries: Número máximo de tentativas
        initial_delay: Delay inicial em segundos
        max_delay: Delay máximo em segundos
        exceptions: Tupla de exceções para capturar
        on_retry: Callback opcional chamado em cada retry (recebe exceção e número da tentativa)

    Example:
        @retry_with_backoff(max_retries=3, exceptions=(ConnectionError, TimeoutError))
        async def fetch_data():
            return await api_call()
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries - 1:
                        logger.error(
                            f"Todas as {max_retries} tentativas falharam para {func.__name__}: {e}"
                        )
                        raise

                    # Chama callback se fornecido
                    if on_retry:
                        try:
                            on_retry(e, attempt + 1)
                        except Exception:
                            pass

                    # Jitter para evitar thundering herd
                    jitter = random.uniform(0, delay * 0.1)
                    actual_delay = delay + jitter

                    logger.warning(
                        f"Tentativa {attempt + 1}/{max_retries} falhou para {func.__name__}: {e}. "
                        f"Retry em {actual_delay:.2f}s"
                    )

                    await asyncio.sleep(actual_delay)

                    # Exponential backoff
                    delay = min(delay * 2, max_delay)

            # Não deveria chegar aqui, mas por segurança
            if last_exception:
                raise last_exception

        return async_wrapper

    return decorator


def retry_with_backoff_sync(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    exceptions: Tuple[type, ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """
    Versão síncrona do retry com exponential backoff
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            import time

            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries - 1:
                        logger.error(
                            f"Todas as {max_retries} tentativas falharam para {func.__name__}: {e}"
                        )
                        raise

                    if on_retry:
                        try:
                            on_retry(e, attempt + 1)
                        except Exception:
                            pass

                    jitter = random.uniform(0, delay * 0.1)
                    actual_delay = delay + jitter

                    logger.warning(
                        f"Tentativa {attempt + 1}/{max_retries} falhou para {func.__name__}: {e}. "
                        f"Retry em {actual_delay:.2f}s"
                    )

                    time.sleep(actual_delay)
                    delay = min(delay * 2, max_delay)

            if last_exception:
                raise last_exception

        return sync_wrapper

    return decorator
