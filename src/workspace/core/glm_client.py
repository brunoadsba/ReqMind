"""Cliente para GLM (Zhipu / BigModel) como fallback de chat quando Groq retorna 429."""

import os
import time
import logging
from typing import List, Dict, Optional

import requests

logger = logging.getLogger(__name__)

# Zhipu BigModel v4 (OpenAI-compatible)
DEFAULT_GLM_BASE = "https://open.bigmodel.cn/api/paas/v4"
DEFAULT_GLM_MODEL = "glm-4.7-flash"
DEFAULT_TIMEOUT = 25
MAX_RETRIES = 2


def _make_request_with_retry(
    api_key: str,
    messages: List[Dict[str, str]],
    base_url: Optional[str],
    model: str,
    max_tokens: int,
    temperature: float,
    timeout: float,
) -> Optional[str]:
    """Faz a requisição com retry e backoff exponencial."""
    url = (base_url or os.getenv("GLM_API_BASE_URL") or DEFAULT_GLM_BASE).rstrip("/")
    if not url.endswith("/chat/completions"):
        url = f"{url}/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }

    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices") or []
                if choices:
                    msg = choices[0].get("message") or {}
                    content = (msg.get("content") or "").strip()
                    if not content and msg.get("reasoning_content"):
                        content = (msg.get("reasoning_content") or "").strip()
                    if content:
                        return content
                logger.warning("Resposta GLM sem conteúdo válido: %s", data)
                return None
            elif resp.status_code in (429, 500, 502, 503, 504):
                if attempt < MAX_RETRIES:
                    delay = (2**attempt) + (hash(str(api_key)) % 1000 / 1000)
                    logger.warning(
                        "GLM retornou %s, tentando novamente em %.1fs...", resp.status_code, delay
                    )
                    time.sleep(delay)
                    continue
            logger.error(
                "Fallback GLM falhou (Status %s): %s",
                resp.status_code,
                resp.text[:500] if resp.text else "(sem body)",
            )
            return None
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                delay = 2**attempt
                logger.warning("Timeout GLM na tentativa %d, retry em %ds...", attempt + 1, delay)
                time.sleep(delay)
                continue
            logger.error("Fallback GLM falhou: Timeout após %d tentativas", MAX_RETRIES + 1)
            return None
        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES:
                delay = 2**attempt
                logger.warning(
                    "Erro GLM na tentativa %d: %s, retry em %ds...", attempt + 1, e, delay
                )
                time.sleep(delay)
                continue
            logger.warning("Erro na API GLM após %d tentativas: %s", MAX_RETRIES + 1, e)
            return None
    return None


def chat_completion_sync(
    api_key: str,
    messages: List[Dict[str, str]],
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    timeout: float = DEFAULT_TIMEOUT,
) -> Optional[str]:
    """
    Chamada síncrona à API GLM (Zhipu/BigModel ou provedor compatível).
    Retorna o conteúdo da resposta ou None em caso de erro.
    Não suporta tool calling; uso como fallback quando Groq (e opcionalmente Kimi) falham.
    Implementa retry com backoff exponencial para resiliência.
    """
    if not api_key or not api_key.strip():
        logger.warning("GLM_API_KEY não configurada")
        return None

    model = model or os.getenv("GLM_MODEL", DEFAULT_GLM_MODEL)

    return _make_request_with_retry(
        api_key=api_key,
        messages=messages,
        base_url=base_url,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        timeout=timeout,
    )
