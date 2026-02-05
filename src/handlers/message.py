"""Handler para mensagens de texto"""

import os
import logging
import glob
from telegram import Update
from telegram.ext import ContextTypes

from config.settings import config
from security.auth import require_auth
from workspace.core.agent import Agent
from workspace.storage.sqlite_store import SQLiteStore
from agent_setup import text_to_speech, groq_client

logger = logging.getLogger(__name__)


@require_auth
async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    agent: Agent,
    store: SQLiteStore,
):
    """Handler para mensagens de texto"""
    user_message = update.message.text
    user_id = update.effective_user.id
    logger.info(f"Mensagem recebida de user_id={user_id}, len={len(user_message)}")

    # Detecta se usuário quer resposta em áudio
    send_audio = any(
        keyword in user_message.lower()
        for keyword in ["em áudio", "com áudio", "responda em áudio", "fale", "voz"]
    )

    # Detecta link do YouTube
    if "youtube.com" in user_message or "youtu.be" in user_message:
        await update.message.reply_text(
            "🎬 Analisando vídeo do YouTube... Isso pode levar alguns minutos."
        )

        try:
            import re
            from workspace.tools.youtube_analyzer import YouTubeAnalyzer

            # Extrai apenas a URL do YouTube
            url_pattern = (
                r"(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]+)"
            )
            match = re.search(url_pattern, user_message)
            youtube_url = match.group(1) if match else user_message

            analyzer = YouTubeAnalyzer()
            result = await analyzer.analyze_youtube_video(youtube_url)

            await update.message.reply_text(result)
            return
        except Exception as e:
            logger.error(f"Erro ao analisar YouTube: {e}", exc_info=True)
            await update.message.reply_text("Ocorreu um erro ao analisar o vídeo. Tente novamente.")
            return

    await update.message.chat.send_action("typing")

    try:
        # Usa histórico vazio para evitar erros
        history = []
        response = await agent.run(user_message, history, user_id=update.effective_user.id)

        store.log_metric("message_processed", {"length": len(user_message)})

        # Verifica se há imagem de gráfico para enviar
        if "create_chart" in user_message.lower() or "gráfico" in user_message.lower():
            # Procura por arquivo de imagem temporário
            temp_images = glob.glob(str(config.TEMP_DIR / "tmp*.png"))
            if temp_images:
                # Envia a imagem mais recente
                latest_image = max(temp_images, key=os.path.getctime)
                with open(latest_image, "rb") as img:
                    await update.message.reply_photo(
                        photo=img, caption="📊 Gráfico gerado"
                    )
                os.unlink(latest_image)

        # Envia resposta em texto
        await update.message.reply_text(response)

        # Se solicitado, envia também em áudio
        if send_audio:
            await update.message.chat.send_action("record_voice")
            audio_bytes = text_to_speech(response)
            if audio_bytes:
                await update.message.reply_voice(voice=audio_bytes)
            else:
                await update.message.reply_text("⚠️ Não foi possível gerar o áudio.")

    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        await update.message.reply_text("Ocorreu um erro. Tente novamente.")
