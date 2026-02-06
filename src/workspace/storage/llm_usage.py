"""Registro simples de uso diário de tokens por provedor de LLM.

Implementação leve baseada em arquivo JSON em `config.DATA_DIR`, adequada
para uso pessoal (um usuário, uma máquina).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, Tuple

from config.settings import config


def _usage_file() -> Path:
    """Retorna o caminho do arquivo de uso."""
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    return config.DATA_DIR / "llm_usage.json"


def _load() -> Dict[str, Dict[str, Dict[str, int]]]:
    """Carrega o arquivo de uso ou retorna estrutura vazia."""
    path = _usage_file()
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save(data: Dict[str, Dict[str, Dict[str, int]]]) -> None:
    """Persiste o arquivo de uso."""
    path = _usage_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _today_key() -> str:
    """Chave de data no formato YYYY-MM-DD (UTC simples é suficiente para uso pessoal)."""
    return date.today().isoformat()


def add_usage(provider: str, input_tokens: int, output_tokens: int) -> None:
    """Acumula uso de tokens para o provedor no dia atual."""
    if not provider:
        return
    if input_tokens < 0 or output_tokens < 0:
        return

    data = _load()
    day = _today_key()

    prov = data.setdefault(provider, {})
    entry = prov.setdefault(day, {"input_tokens": 0, "output_tokens": 0})

    entry["input_tokens"] += int(input_tokens)
    entry["output_tokens"] += int(output_tokens)

    _save(data)


def get_usage(provider: str) -> Tuple[int, int]:
    """Retorna (input_tokens, output_tokens) consumidos hoje por um provedor."""
    if not provider:
        return (0, 0)
    data = _load()
    day = _today_key()
    prov = data.get(provider, {})
    entry = prov.get(day, {})
    return int(entry.get("input_tokens", 0)), int(entry.get("output_tokens", 0))


def has_reached_daily_limit(provider: str, daily_limit_tokens: int) -> bool:
    """Verifica se o provedor atingiu o limite diário de tokens.

    `daily_limit_tokens <= 0` significa \"sem limite\".
    """
    if daily_limit_tokens is None or daily_limit_tokens <= 0:
        return False
    used_input, used_output = get_usage(provider)
    total = used_input + used_output
    return total >= int(daily_limit_tokens)

