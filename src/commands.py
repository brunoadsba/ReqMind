"""Comandos do bot Telegram (/start, /clear, /status)"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from workspace.core.agent import Agent
from workspace.storage.sqlite_store import SQLiteStore

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
            f"🟢 Sistema operacional\n\n"
            f"Ferramentas disponíveis: {len(tools)}\n"
            f"• {', '.join(tools)}"
        )
    return handler
