"""Handler para mensagens de voz"""

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
async def handle_voice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    agent: Agent,
    store: SQLiteStore,
):
    """Handler para mensagens de voz"""
    logger.info("Áudio de voz recebido")

    await update.message.chat.send_action("typing")

    chat_id = update.effective_chat.id

    try:
        # Download do áudio
        voice = update.message.voice
        voice_file = await voice.get_file()
        voice_path = str(config.TEMP_DIR / f"moltbot_voice_{voice.file_id}.ogg")
        await voice_file.download_to_drive(voice_path)

        # Transcreve com Groq Whisper
        with open(voice_path, "rb") as audio_file:
            transcription = groq_client.audio.transcriptions.create(
                file=audio_file, model="whisper-large-v3-turbo", response_format="text"
            )

        store.add_message("user", f"[ÁUDIO] {transcription}", chat_id=chat_id)

        history = store.get_history(limit=10, chat_id=chat_id)
        response = await agent.run(transcription, history)

        store.add_message("assistant", response, chat_id=chat_id)

        # Responde com transcrição + resposta
        await update.message.reply_text(
            f'🎤 Você disse:\n"{transcription}"\n\n{response}'
        )

        # Limpa arquivo
        os.unlink(voice_path)

    except Exception as e:
        logger.error(f"Erro ao processar áudio: {e}", exc_info=True)
        await update.message.reply_text("Ocorreu um erro ao processar o áudio. Tente novamente.")
