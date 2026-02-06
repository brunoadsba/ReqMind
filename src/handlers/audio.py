"""Handler para arquivos de áudio"""

import os
import logging
from telegram import Update
from telegram.ext import ContextTypes

from security.auth import require_auth
from workspace.core.agent import Agent
from workspace.storage.sqlite_store import SQLiteStore
from agent_setup import groq_client
from config.settings import config

logger = logging.getLogger(__name__)


@require_auth
async def handle_audio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    agent: Agent,
    store: SQLiteStore,
):
    """Handler para arquivos de áudio"""
    logger.info("Arquivo de áudio recebido")

    await update.message.chat.send_action("typing")

    chat_id = update.effective_chat.id

    try:
        # Download do áudio
        audio = update.message.audio
        audio_file_obj = await audio.get_file()
        audio_path = str(config.TEMP_DIR / f"moltbot_audio_{audio.file_id}.mp3")
        await audio_file_obj.download_to_drive(audio_path)

        # Transcreve com Groq Whisper
        with open(audio_path, "rb") as audio_file:
            transcription = groq_client.audio.transcriptions.create(
                file=audio_file, model="whisper-large-v3-turbo", response_format="text"
            )

        store.add_message("user", f"[ÁUDIO] {transcription}", chat_id=chat_id)

        history = store.get_history(limit=10, chat_id=chat_id)
        response = await agent.run(transcription, history)

        store.add_message("assistant", response, chat_id=chat_id)

        # Responde
        await update.message.reply_text(
            f'🎵 Você disse:\n"{transcription}"\n\n{response}'
        )

        # Limpa arquivo
        os.unlink(audio_path)

    except Exception as e:
        logger.error(f"Erro ao processar áudio: {e}", exc_info=True)
        await update.message.reply_text("Ocorreu um erro ao processar o áudio. Tente novamente.")
