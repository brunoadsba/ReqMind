"""Cliente para Kimi K2.5 via NVIDIA NIM API (chat completions)."""

import logging
from typing import List, Dict, Optional

import requests

logger = logging.getLogger(__name__)

NVIDIA_CHAT_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
KIMI_MODEL = "moonshotai/kimi-k2.5"
# Timeout curto para fallback em 429: evita usuário esperar 1 min se a API estiver lenta
DEFAULT_TIMEOUT = 20


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
    """
    if not api_key or not api_key.strip():
        logger.warning("NVIDIA_API_KEY não configurada")
        return None

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

    try:
        resp = requests.post(
            NVIDIA_CHAT_URL,
            headers=headers,
            json=payload,
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            logger.warning("Resposta NVIDIA sem choices")
            return None
        content = (choices[0].get("message") or {}).get("content")
        return (content or "").strip() or None
    except requests.exceptions.Timeout:
        logger.warning("Timeout na API NVIDIA Kimi")
        return None
    except requests.exceptions.RequestException as e:
        logger.warning("Erro na API NVIDIA Kimi: %s", e)
        return None
    except (KeyError, TypeError, ValueError) as e:
        logger.warning("Resposta NVIDIA inesperada: %s", e)
        return None
