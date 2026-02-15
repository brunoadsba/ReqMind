"""
Utilitários para validação e diagnóstico do bot.

Este módulo contém funções auxiliares para verificar se o bot está
funcionando corretamente, especialmente em relação à memória e lembretes.
"""

import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime


def validar_memoria(fact_store_path: str) -> Dict[str, Any]:
    """
    Verifica se o FactStore contém dados e se o bot consegue acessá-los.

    Args:
        fact_store_path: Caminho para o arquivo facts.jsonl

    Returns:
        Dict com informações sobre o estado da memória
    """
    result = {"exists": False, "total_facts": 0, "sample_facts": [], "error": None}

    if not os.path.exists(fact_store_path):
        result["error"] = f"❌ FactStore não encontrado em: {fact_store_path}"
        return result

    result["exists"] = True

    try:
        with open(fact_store_path, "r") as f:
            facts = []
            for line in f:
                line = line.strip()
                if line:
                    try:
                        fact = json.loads(line)
                        facts.append(fact)
                    except json.JSONDecodeError:
                        continue

        result["total_facts"] = len(facts)

        if facts:
            result["sample_facts"] = facts[:3]
            print(f"✅ FactStore carregado. Total de fatos: {len(facts)}")
            for fact in facts[:3]:
                content = fact.get("content", "N/A")
                print(f"   - {content[:80]}...")
        else:
            print("⚠️ FactStore existe mas está vazio")

    except Exception as e:
        result["error"] = f"❌ Erro ao ler FactStore: {e}"

    return result


def list_reminders_logic(reminders_file: str) -> str:
    """
    Lógica sugerida para o comando /lembretes.

    Args:
        reminders_file: Caminho para o arquivo de lembretes

    Returns:
        String formatada com a lista de lembretes
    """
    if not os.path.exists(reminders_file):
        return "📅 **Lembretes**\n\nVocê não tem lembretes pendentes."

    try:
        with open(reminders_file, "r") as f:
            reminders = json.load(f)

        if not reminders:
            return "📅 **Lembretes**\n\nVocê não tem lembretes pendentes."

        now = datetime.now()
        pending = []

        for r in reminders:
            try:
                reminder_time = datetime.fromisoformat(r.get("timestamp", ""))
                if reminder_time > now:
                    pending.append(
                        {
                            "text": r.get("text", ""),
                            "datetime": r.get("datetime", ""),
                            "timestamp": r["timestamp"],
                        }
                    )
            except (KeyError, ValueError):
                continue

        if not pending:
            return "📅 **Lembretes**\n\nNenhum lembrete pendente."

        pending.sort(key=lambda x: x["timestamp"])

        msg_lines = ["📅 **Seus próximos lembretes:**\n"]
        for i, r in enumerate(pending[:10], 1):
            msg_lines.append(f"{i}. 🕐 {r['datetime']}")
            msg_lines.append(f"   📝 {r['text']}\n")

        if len(pending) > 10:
            msg_lines.append(f"\n... e mais {len(pending) - 10} lembretes.")

        return "\n".join(msg_lines)

    except Exception as e:
        return f"❌ Erro ao carregar lembretes: {e}"


def testar_memoria_pergunta() -> List[str]:
    """
    Retorna perguntas de teste para validar se a memória está funcionando.

    Use estas perguntas no Telegram para testar:
    """
    return [
        "O que você sabe sobre mim?",
        "Quais minhas preferências?",
        "Qual meu contexto de trabalho?",
        "O que eu gosto?",
    ]


def verificar_envs() -> Dict[str, Any]:
    """
    Verifica se todas as variáveis de ambiente necessárias estão configuradas.

    Returns:
        Dict com status de cada variável
    """
    envs = {
        "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "NVIDIA_API_KEY": os.getenv("NVIDIA_API_KEY"),
        "GLM_API_KEY": os.getenv("GLM_API_KEY"),
        "EMAIL_ADDRESS": os.getenv("EMAIL_ADDRESS"),
        "SMTP_SERVER": os.getenv("SMTP_SERVER"),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD"),
    }

    result = {}
    for name, value in envs.items():
        if value:
            if (
                value.startswith('"')
                or value.endswith('"')
                or value.startswith("'")
                or value.endswith("'")
            ):
                result[name] = "⚠️ CONFIGURADO (mas tem aspas!)"
            else:
                result[name] = "✅ CONFIGURADO"
        else:
            if name in ["TELEGRAM_TOKEN", "GROQ_API_KEY"]:
                result[name] = "❌ OBRIGATÓRIO - Faltando"
            else:
                result[name] = "⭕ Opcional - Não configurado"

    return result


def diagnostico_completo():
    """
    Executa um diagnóstico completo do bot.
    Imprime informações úteis para debug.
    """
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DO BOT")
    print("=" * 60)

    print("\n📋 Variáveis de Ambiente:")
    envs = verificar_envs()
    for name, status in envs.items():
        print(f"  {name}: {status}")

    print("\n🧠 Memória (FactStore):")
    try:
        from config import config

        fact_store_path = str(config.WORKSPACE_DIR / "memory" / "facts.jsonl")
        validar_memoria(fact_store_path)
    except Exception as e:
        print(f"  ❌ Erro ao verificar memória: {e}")

    print("\n⏰ Lembretes:")
    try:
        from config import config

        reminders_file = str(config.REMINDERS_FILE)
        if os.path.exists(reminders_file):
            with open(reminders_file, "r") as f:
                reminders = json.load(f)
            print(f"  ✅ Arquivo existe: {len(reminders)} lembretes")
        else:
            print(f"  ⚠️ Arquivo não existe ainda (será criado no primeiro lembrete)")
    except Exception as e:
        print(f"  ❌ Erro ao verificar lembretes: {e}")

    print("\n💡 Perguntas para testar a memória:")
    for pergunta in testar_memoria_pergunta():
        print(f"  • {pergunta}")

    print("\n" + "=" * 60)


# Sugestão de Melhoria no System Prompt para Memória:
SYSTEM_PROMPT_MEMORY_ENHANCEMENT = """
[INSTRUÇÃO DE MEMÓRIA]

Você tem acesso a uma memória de longo prazo (FactStore). Sempre que o usuário perguntar 
sobre si mesmo ou suas preferências, consulte o contexto fornecido em <memory_context> 
e responda de forma personalizada, demonstrando que você se lembra dessas informações.

Quando o usuário perguntar "o que você sabe sobre mim" ou "quais minhas preferências",
cite especificamente os fatos da memória de forma natural, como em uma conversa entre amigos.

Exemplo de resposta boa:
"Sei que você trabalha com projetos em /home/bruno/projetos e prefere usar Python. 
Também vi que tem interesse em NR-29."

Exemplo de resposta ruim (genérica):
"Tenho algumas informações sobre você no sistema."
"""


if __name__ == "__main__":
    diagnostico_completo()
