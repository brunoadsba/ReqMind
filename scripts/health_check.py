#!/usr/bin/env python3
"""
Health check unificado: verifica as 3 camadas (motor, gateway, habilidades).
Uso: na raiz do projeto, PYTHONPATH=src python scripts/health_check.py
     ou: make health
"""
import os
import subprocess
import sys
from pathlib import Path

# Raiz do projeto = pai de scripts/
REPO_ROOT = Path(__file__).resolve().parent.parent
os.chdir(REPO_ROOT)
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

# Carrega .env da raiz
from dotenv import load_dotenv
load_dotenv(REPO_ROOT / ".env")

def ok(msg: str) -> None:
    print(f"  [OK]   {msg}")

def fail(msg: str) -> None:
    print(f"  [FAIL] {msg}")

def main() -> int:
    print("Health check (modelo 3 camadas)\n")
    failures = 0

    # --- Camada 1: Motor (processo/container) ---
    print("1. Motor (processo/container)")
    try:
        out = subprocess.run(
            ["docker", "ps", "--filter", "name=assistente-bot", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            ok("Container assistente-bot rodando")
        else:
            fail("Container assistente-bot não está rodando (use make start-docker)")
            failures += 1
    except FileNotFoundError:
        fail("Docker não encontrado (instale ou use make start sem Docker)")
        failures += 1
    except subprocess.TimeoutExpired:
        fail("Docker timeout")
        failures += 1

    # --- Variáveis de ambiente (motor + gateway) ---
    print("\n2. Variáveis de ambiente (.env)")
    telegram = os.getenv("TELEGRAM_TOKEN", "").strip()
    groq = os.getenv("GROQ_API_KEY", "").strip()
    if telegram:
        ok("TELEGRAM_TOKEN definido")
    else:
        fail("TELEGRAM_TOKEN ausente no .env")
        failures += 1
    if groq:
        ok("GROQ_API_KEY definido")
    else:
        fail("GROQ_API_KEY ausente no .env")
        failures += 1
    nvidia = os.getenv("NVIDIA_API_KEY", "").strip()
    glm = os.getenv("GLM_API_KEY", "").strip()
    if nvidia:
        ok("NVIDIA_API_KEY definido (fallback 429)")
    else:
        print("  [--]   NVIDIA_API_KEY não definido (fallback Kimi opcional)")
    if glm:
        ok("GLM_API_KEY definido (fallback 429)")
    else:
        print("  [--]   GLM_API_KEY não definido (fallback GLM opcional)")

    # --- Camada 3: Habilidades (agente + tools carregam) ---
    print("\n3. Habilidades (agente e tools)")
    try:
        from agent_setup import create_agent_no_sandbox
        agent = create_agent_no_sandbox()
        tools_list = agent.tools.list_tools() if hasattr(agent, "tools") else []
        if tools_list:
            ok(f"Agente e tools carregados ({len(tools_list)} tools)")
        else:
            ok("Agente carregado (tools vazias)")
    except Exception as e:
        fail(f"Falha ao carregar agente/tools: {e}")
        failures += 1

    print()
    if failures == 0:
        print("Resultado: tudo OK.")
        return 0
    print(f"Resultado: {failures} falha(s). Ver docs/COMPARATIVO_OPENCLAW_REQMIND.md (seção 'Se falhou, qual camada?').")
    return 1

if __name__ == "__main__":
    sys.exit(main())
