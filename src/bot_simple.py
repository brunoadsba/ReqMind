"""Telegram Bot - Versão modularizada"""

import os
import logging
import sys
import signal
import asyncio
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de paths
from config.settings import config

sys.path.insert(0, str(config.BASE_DIR))

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from workspace.storage.sqlite_store import SQLiteStore

# Imports dos módulos criados
from workspace.core.agent import Agent
from agent_setup import create_agent_no_sandbox
from commands import start, make_clear_handler, make_status_handler, lembretes_handler
from handlers import (
    handle_message,
    handle_photo,
    handle_video,
    handle_voice,
    handle_audio,
    handle_document,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Diagnóstico: presença de chaves de fallback (não exibe valor)
logger.info(
    "Config: NVIDIA_KEY=%s GLM_KEY=%s",
    "SET" if os.getenv("NVIDIA_API_KEY") else "MISSING",
    "SET" if os.getenv("GLM_API_KEY") else "MISSING",
)

# Oculta logs de requisições HTTP (getUpdates, etc.)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

# Inicializa componentes globais
agent = create_agent_no_sandbox()
store = SQLiteStore()


def make_message_handler(agent: Agent, store: SQLiteStore):
    """Factory para criar handler de mensagem com dependências injetadas"""

    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await handle_message(update, context, agent, store)

    return handler


def make_photo_handler(store: SQLiteStore):
    """Factory para criar handler de foto com dependências injetadas"""

    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await handle_photo(update, context, store)

    return handler


def make_video_handler(store: SQLiteStore):
    """Factory para criar handler de vídeo com dependências injetadas"""

    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await handle_video(update, context, store)

    return handler


def make_voice_handler(agent: Agent, store: SQLiteStore):
    """Factory para criar handler de voz com dependências injetadas"""

    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await handle_voice(update, context, agent, store)

    return handler


def make_audio_handler(agent: Agent, store: SQLiteStore):
    """Factory para criar handler de áudio com dependências injetadas"""

    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await handle_audio(update, context, agent, store)

    return handler


def make_document_handler(agent: Agent, store: SQLiteStore):
    """Factory para criar handler de documento com dependências injetadas"""

    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await handle_document(update, context, agent, store)

    return handler


async def main():
    """Função principal do bot"""
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN não configurado!")

    logger.info("boot_iniciando_bot")

    # Inicia monitoramento de lembretes como task asyncio (não thread)
    from workspace.tools.reminder_notifier import notifier

    reminder_task = asyncio.create_task(notifier.start_monitoring())
    logger.info("lembretes_iniciados canal=email+telegram")

    # Configura handlers
    app = Application.builder().token(token).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", make_clear_handler(store)))
    app.add_handler(CommandHandler("status", make_status_handler(agent)))
    app.add_handler(CommandHandler("lembretes", lembretes_handler))

    # Handlers de mídia
    app.add_handler(MessageHandler(filters.PHOTO, make_photo_handler(store)))
    app.add_handler(MessageHandler(filters.VOICE, make_voice_handler(agent, store)))
    app.add_handler(MessageHandler(filters.AUDIO, make_audio_handler(agent, store)))
    app.add_handler(MessageHandler(filters.VIDEO, make_video_handler(store)))
    app.add_handler(MessageHandler(filters.Document.ALL, make_document_handler(agent, store)))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, make_message_handler(agent, store))
    )

    # Inicializa e inicia o bot
    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    logger.info("bot_pronto status=aguardando_mensagens")

    # Aguarda sinal de parada
    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("🛑 Sinal de parada recebido")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_event_loop().add_signal_handler(sig, signal_handler)

    await stop_event.wait()

    # Cleanup: ordem obrigatória (PTB v20) – parar updater antes de stop/shutdown
    logger.info("🧹 Limpando recursos...")
    reminder_task.cancel()
    try:
        await reminder_task
    except asyncio.CancelledError:
        pass

    if app.updater and app.updater.running:
        try:
            await asyncio.wait_for(app.updater.stop(), timeout=15.0)
        except (asyncio.TimeoutError, Exception) as e:
            logger.warning("Updater.stop() falhou (continuando shutdown): %s", e)

    try:
        await app.stop()
        await app.shutdown()
    except RuntimeError as e:
        if "still running" in str(e):
            logger.warning("Shutdown com updater ainda ativo: %s", e)
        else:
            raise
    logger.info("👋 Bot finalizado")


def run_bot():
    """Entry point síncrono para o bot"""
    asyncio.run(main())


if __name__ == "__main__":
    run_bot()
