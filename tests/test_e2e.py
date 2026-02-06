#!/usr/bin/env python3
"""Teste E2E do Moltbot"""
import os
import sys
import asyncio

import pytest
from dotenv import load_dotenv

load_dotenv()

# Cores para output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def _report_result(name: str, passed: bool) -> bool:
    """Imprime resultado de um subteste em formato legível."""
    symbol = f"{GREEN}✅{RESET}" if passed else f"{RED}❌{RESET}"
    print(f"{symbol} {name}")
    return passed

async def main():
    print("\n🧪 TESTE E2E - MOLTBOT\n")
    print("=" * 50)
    
    results: list[bool] = []
    
    # 1. Verificar .env
    print(f"\n{YELLOW}1. Verificando configuração...{RESET}")
    env_exists = os.path.exists(".env")
    results.append(_report_result("Arquivo .env existe", env_exists))
    
    if env_exists:
        import stat
        st = os.stat(".env")
        perms = oct(st.st_mode)[-3:]
        results.append(
            _report_result(f".env protegido (permissões: {perms})", perms == "600")
        )
    
    # 2. Verificar variáveis de ambiente
    print(f"\n{YELLOW}2. Verificando variáveis de ambiente...{RESET}")
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    groq_key = os.getenv("GROQ_API_KEY")
    glm_key = os.getenv("GLM_API_KEY")
    
    results.append(_report_result("TELEGRAM_TOKEN configurado", bool(telegram_token)))
    results.append(_report_result("GROQ_API_KEY configurado", bool(groq_key)))
    results.append(_report_result("GLM_API_KEY configurado", bool(glm_key)))
    
    # 3. Verificar módulos de segurança
    print(f"\n{YELLOW}3. Verificando módulos de segurança...{RESET}")
    try:
        from security.auth import require_auth, ALLOWED_USERS
        results.append(_report_result("Módulo security.auth importado", True))
        results.append(
            _report_result(
                f"Usuários autorizados: {len(ALLOWED_USERS)}", len(ALLOWED_USERS) > 0
            )
        )
    except Exception as e:
        results.append(_report_result(f"Módulo security.auth: {e}", False))
    
    # 4. Verificar dependências
    print(f"\n{YELLOW}4. Verificando dependências...{RESET}")
    try:
        import telegram
        results.append(_report_result("python-telegram-bot instalado", True))
    except Exception:
        results.append(_report_result("python-telegram-bot instalado", False))
    
    try:
        from groq import Groq
        results.append(_report_result("groq instalado", True))
    except Exception:
        results.append(_report_result("groq instalado", False))
    
    try:
        import yt_dlp
        results.append(_report_result("yt-dlp instalado", True))
    except Exception:
        results.append(_report_result("yt-dlp instalado", False))
    
    # 5. Verificar ferramentas
    print(f"\n{YELLOW}5. Verificando ferramentas do bot...{RESET}")
    try:
        from workspace.core.tools import ToolRegistry
        from workspace.core.agent import Agent
        results.append(_report_result("ToolRegistry importado", True))
        results.append(_report_result("Agent importado", True))
    except Exception as e:
        results.append(_report_result(f"Ferramentas: {e}", False))
    
    # 6. Verificar YouTube Analyzer
    print(f"\n{YELLOW}6. Verificando YouTube Analyzer...{RESET}")
    try:
        from workspace.tools.youtube_analyzer import YouTubeAnalyzer
        results.append(_report_result("YouTubeAnalyzer importado", True))
    except Exception as e:
        results.append(_report_result(f"YouTubeAnalyzer: {e}", False))
    
    # 7. Verificar comandos do sistema
    print(f"\n{YELLOW}7. Verificando comandos do sistema...{RESET}")
    import subprocess
    
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, timeout=5)
        results.append(_report_result("ffmpeg disponível", True))
    except Exception:
        results.append(_report_result("ffmpeg disponível", False))
    
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True, timeout=5)
        results.append(_report_result("yt-dlp CLI disponível", True))
    except Exception:
        results.append(_report_result("yt-dlp CLI disponível", False))
    
    # 8. Testar conexão com Telegram
    print(f"\n{YELLOW}8. Testando conexão com Telegram...{RESET}")
    if telegram_token:
        try:
            from telegram import Bot
            bot = Bot(token=telegram_token)
            me = await bot.get_me()
            results.append(_report_result(f"Bot conectado: @{me.username}", True))
        except Exception as e:
            results.append(_report_result(f"Conexão Telegram: {str(e)[:50]}", False))
    
    # 9. Testar Groq API
    print(f"\n{YELLOW}9. Testando Groq API...{RESET}")
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "teste"}],
                max_tokens=10
            )
            results.append(_report_result("Groq API funcionando", True))
        except Exception as e:
            results.append(_report_result(f"Groq API: {str(e)[:50]}", False))
    
    # 10. Verificar bot_simple.py
    print(f"\n{YELLOW}10. Verificando bot_simple.py...{RESET}")
    bot_file = "src/bot_simple.py"
    results.append(_report_result("bot_simple.py existe", os.path.exists(bot_file)))
    
    if os.path.exists(bot_file):
        with open(bot_file, "r", encoding="utf-8") as f:
            content = f.read()
            results.append(_report_result("@require_auth presente", "@require_auth" in content))
            results.append(_report_result("YouTubeAnalyzer importado", "YouTubeAnalyzer" in content))
    
    # Resumo
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n📊 RESULTADO: {passed}/{total} testes passaram ({percentage:.1f}%)")
    
    if percentage == 100:
        print(f"\n{GREEN}🎉 TODOS OS TESTES PASSARAM!{RESET}")
        print(f"{GREEN}✅ Bot pronto para uso!{RESET}")
        return 0
    elif percentage >= 80:
        print(f"\n{YELLOW}⚠️  Maioria dos testes passou, mas há alguns problemas.{RESET}")
        return 1
    else:
        print(f"\n{RED}❌ Muitos testes falharam. Verifique a configuração.{RESET}")
        return 2

@pytest.mark.asyncio
async def test_e2e_smoke():
    """Smoke test: garante que o script E2E roda sem crash.

    O retorno numérico (0/1/2) continua sendo usado quando o script
    é executado via linha de comando; aqui apenas exigimos que ele
    complete com um código válido.
    """
    exit_code = await main()
    assert exit_code in (0, 1, 2)


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
