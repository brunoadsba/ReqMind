"""Cliente para Kimi K2.5 via Moonshot AI ou NVIDIA (fallback)."""

import logging
import time
import os
from typing import List, Dict, Optional

import requests

logger = logging.getLogger(__name__)

# Endpoints
MOONSHOT_BASE_URL = "https://api.moonshot.cn/v1/chat/completions"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

# Modelos
MOONSHOT_MODEL = "moonshot-v1-8k"
NVIDIA_MODEL = "moonshotai/kimi-k2.5"

# Timeout
DEFAULT_TIMEOUT = 25
MAX_RETRIES = 2


def _make_request(
    url: str,
    headers: dict,
    payload: dict,
    timeout: float,
) -> Optional[str]:
    """Executa a requisição HTTP."""
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            return None
        except requests.exceptions.HTTPError as e:
            logger.warning(f"Erro HTTP Kimi ({url}) [{attempt+1}]: {e} - Resp: {response.text[:200]}")
            if response.status_code in (400, 401, 403):
                return None  # Erro fatal de auth/request, não retry
        except Exception as e:
            logger.warning(f"Erro request Kimi ({url}) [{attempt+1}]: {e}")
            
        if attempt < MAX_RETRIES:
            time.sleep(1.5 * (attempt + 1))
            
    return None


def chat_completion_sync(
    api_key: str,  # Chave NVIDIA como fallback
    messages: List[Dict[str, str]],
    max_tokens: int = 4096,
    temperature: float = 0.7,
    thinking: bool = True,
    timeout: float = DEFAULT_TIMEOUT,
) -> Optional[str]:
    """
    Chamada síncrona à API do Kimi com Failover Múltiplo.
    1. Tenta Moonshot AI (se KIMI_API_KEY existir).
    2. Se falhar (auth/erro), tenta NVIDIA NIM (se api_key/NVIDIA_API_KEY existir).
    """
    
    # 1. TENTATIVA MOONSHOT
    moonshot_key = os.getenv("KIMI_API_KEY", "").strip()
    if moonshot_key:
        logger.info("Tentando Kimi via Moonshot API Oficial...")
        headers = {
            "Authorization": f"Bearer {moonshot_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": MOONSHOT_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }
        res = _make_request(MOONSHOT_BASE_URL, headers, payload, timeout)
        if res:
            return res
        else:
            logger.warning("Falha na Moonshot API. Tentando fallback para NVIDIA...")

    # 2. TENTATIVA NVIDIA (Fallback)
    nvidia_key = api_key or os.getenv("NVIDIA_API_KEY", "").strip()
    if not nvidia_key:
        logger.warning("Nenhuma chave NVIDIA disponível para fallback.")
        return None

    logger.info("Tentando Kimi via NVIDIA NIM...")
    headers = {
        "Authorization": f"Bearer {nvidia_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": NVIDIA_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
        "chat_template_kwargs": {"thinking": thinking},
    }
    
    return _make_request(NVIDIA_BASE_URL, headers, payload, timeout)
