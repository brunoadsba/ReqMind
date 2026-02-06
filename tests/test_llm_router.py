"""Testes para LlmRouter e controle simples de quotas diárias."""

import os
from pathlib import Path

from config.settings import config
from workspace.core.llm_router import LlmRouter
from workspace.storage import llm_usage


def test_has_reached_daily_limit_false_when_zero_limit(tmp_path, monkeypatch):
    """Limite 0 deve ser interpretado como 'sem limite'."""
    assert llm_usage.has_reached_daily_limit("groq", 0) is False
    assert llm_usage.has_reached_daily_limit("groq", -1) is False


def test_llm_usage_add_and_get(tmp_path, monkeypatch):
    """Registrar uso de tokens deve acumular valores para o dia atual."""
    # Isola arquivo de uso em diretório temporário
    monkeypatch.setenv("MOLTBOT_DIR", str(tmp_path))

    # Limpa estado anterior
    usage_file = config.DATA_DIR / "llm_usage.json"
    if usage_file.exists():
        usage_file.unlink()

    llm_usage.add_usage("groq", 100, 50)
    llm_usage.add_usage("groq", 20, 30)

    used_in, used_out = llm_usage.get_usage("groq")
    assert used_in == 120
    assert used_out == 80


def test_has_reached_daily_limit_true(tmp_path, monkeypatch):
    """Quando uso acumulado >= limite, has_reached_daily_limit deve ser True."""
    monkeypatch.setenv("MOLTBOT_DIR", str(tmp_path))

    # Zera estado
    usage_file = config.DATA_DIR / "llm_usage.json"
    if usage_file.exists():
        usage_file.unlink()

    llm_usage.add_usage("groq", 500, 500)
    assert llm_usage.has_reached_daily_limit("groq", 900) is True
    assert llm_usage.has_reached_daily_limit("groq", 1001) is False

