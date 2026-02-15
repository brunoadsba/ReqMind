"""Comandos do bot Telegram (/start, /clear, /status, /lembretes)"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from workspace.core.agent import Agent
from workspace.storage.sqlite_store import SQLiteStore
from workspace.tools.reminder_notifier import notifier

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler do comando /start"""
    await update.message.reply_text(
        "🤖 Olá! Sou seu assistente pessoal.\n\n"
        "Posso ajudar você com:\n"
        "• 💬 Chat inteligente e respostas em áudio\n"
        "• 🌐 Busca na web (DuckDuckGo)\n"
        "• 🧠 Memória persistente de conversas\n"
        "• 📁 Operações de arquivos (ler/escrever/listar)\n"
        "• 🔍 Busca em código e análise Git\n"
        "• 🖼️ Análise de imagens, vídeos e documentos\n"
        "• 🎬 Transcrição de áudio e vídeos\n"
        "• 🌤️ Clima, notícias e lembretes\n"
        "• 📊 Criação de gráficos e visualizações\n\n"
        "Como posso ser útil para você hoje?"
    )


def make_clear_handler(store: SQLiteStore):
    """Factory para criar handler de /clear: limpa apenas o histórico deste chat."""

    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        store.clear_history(chat_id=chat_id)
        await update.message.reply_text("✅ Histórico deste chat limpo!")

    return handler


def make_status_handler(agent: Agent):
    """Factory para criar handler de /status com agent injetado"""

    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        tools = agent.tools.list_tools()
        await update.message.reply_text(
            f"🟢 Sistema operacional\n\nFerramentas disponíveis: {len(tools)}\n• {', '.join(tools)}"
        )

    return handler


async def lembretes_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler do comando /lembretes: lista lembretes pendentes."""
    try:
        pending = notifier.list_pending_reminders()
        if not pending:
            await update.message.reply_text(
                "📅 **Lembretes**\n\n"
                "Você não tem lembretes pendentes.\n\n"
                "💡 *Dica:* Crie um lembrete dizendo:\n"
                '"Lembre daqui 2 horas: ligar para cliente"'
            )
            return
        msg_lines = ["📅 **Seus próximos lembretes:**\n"]
        for i, r in enumerate(pending[:10], 1):
            msg_lines.append(f"{i}. 🕐 {r['datetime']}")
            msg_lines.append(f"   📝 {r['text']}\n")
        if len(pending) > 10:
            msg_lines.append(f"\n... e mais {len(pending) - 10} lembretes.")
        await update.message.reply_text("\n".join(msg_lines))
    except Exception as e:
        logger.error(f"Erro ao listar lembretes: {e}")
        await update.message.reply_text(
            "❌ Não foi possível listar os lembretes.\nTente novamente em alguns instantes."
        )
