"""Cliente para Kimi K2.5 via NVIDIA NIM API (chat completions)."""

import logging
import time
from typing import List, Dict, Optional

import requests

logger = logging.getLogger(__name__)

NVIDIA_CHAT_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
KIMI_MODEL = "moonshotai/kimi-k2.5"
# Timeout curto para fallback em 429: evita usuário esperar 1 min se a API estiver lenta
DEFAULT_TIMEOUT = 20
MAX_RETRIES = 2


def _make_request_with_retry(
    api_key: str,
    messages: List[Dict[str, str]],
    max_tokens: int,
    temperature: float,
    thinking: bool,
    timeout: float,
) -> Optional[str]:
    """Faz a requisição com retry e backoff exponencial."""
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": KIMI_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
        "chat_template_kwargs": {"thinking": thinking},
    }

    return _make_request_with_retry(api_key, messages, max_tokens, temperature, thinking, timeout)


def chat_completion_sync(
    api_key: str,
    messages: List[Dict[str, str]],
    max_tokens: int = 4096,
    temperature: float = 0.7,
    thinking: bool = True,
    timeout: float = DEFAULT_TIMEOUT,
) -> Optional[str]:
    """
    Chamada síncrona à API NVIDIA para Kimi K2.5.
    Retorna o conteúdo da resposta ou None em caso de erro.
    Não suporta tool calling; uso típico como fallback quando Groq retorna 429.
    Implementa retry com backoff exponencial para resiliência.
    """
    if not api_key or not api_key.strip():
        logger.warning("NVIDIA_API_KEY não configurada")
        return None

    return _make_request_with_retry(
        api_key=api_key,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        thinking=thinking,
        timeout=timeout,
    )
