"""
Agent Module - Arquitetura de Memoria em 3 Camadas
"""

from pathlib import Path
from config import config

# Paths principais
AGENT_DIR = config.WORKSPACE_DIR / "agent"
RUNS_DIR = config.WORKSPACE_DIR / "runs"
MEMORY_DIR = config.WORKSPACE_DIR / "memory"

# Arquivos core da Camada 1
IDENTITY_FILE = AGENT_DIR / "IDENTITY.md"
POLICIES_FILE = AGENT_DIR / "POLICIES.md"
STYLE_FILE = AGENT_DIR / "STYLE.md"
EXAMPLES_FILE = AGENT_DIR / "EXAMPLES.md"
RUNBOOK_FILE = AGENT_DIR / "RUNBOOK.md"
CURRENT_STATE_FILE = AGENT_DIR / "CURRENT_STATE.md"
CONTEXT_PACK_FILE = AGENT_DIR / "CONTEXT_PACK.md"
CHANGELOG_FILE = AGENT_DIR / "CHANGELOG.md"
META_FILE = AGENT_DIR / "META.md"

__all__ = [
    "AGENT_DIR",
    "RUNS_DIR",
    "MEMORY_DIR",
    "IDENTITY_FILE",
    "POLICIES_FILE",
    "STYLE_FILE",
    "EXAMPLES_FILE",
    "RUNBOOK_FILE",
    "CURRENT_STATE_FILE",
    "CONTEXT_PACK_FILE",
    "CHANGELOG_FILE",
    "META_FILE",
]