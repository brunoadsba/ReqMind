"""Handler para mensagens de texto"""

import os
import re
import logging
import glob
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

import pytz

from config.settings import config
from security.auth import require_auth
from workspace.core.agent import Agent
from workspace.storage.sqlite_store import SQLiteStore
from agent_setup import text_to_speech, groq_client

logger = logging.getLogger(__name__)

# Perguntas que pedem apenas data/hora: responder direto, sem chamar o agente
_DATETIME_PATTERN = re.compile(
    r"^(que\s+)?(data|hora|horas?|dia)\s+(é\s+hoje|são|atual)?|"
    r"data\s+(e|de)\s+hoje|horário\s+atual|que\s+horas?\s+são\s*\??\s*$",
    re.IGNORECASE,
)


def _is_simple_datetime_question(text: str) -> bool:
    """True se a mensagem pede apenas data e/ou hora (máx. 60 caracteres)."""
    t = (text or "").strip()
    if len(t) > 60:
        return False
    return bool(_DATETIME_PATTERN.search(t))


def _format_datetime_reply() -> str:
    tz = pytz.timezone("America/Sao_Paulo")
    now = datetime.now(tz)
    return now.strftime("Hoje é %d/%m/%Y e são %H:%M.").replace(" 0", " ")


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

    chat_id = update.effective_chat.id

    # Perguntas só de data/hora: resposta direta, sem agente (economiza tokens e evita tools)
    if _is_simple_datetime_question(user_message):
        reply = _format_datetime_reply()
        store.add_message("user", user_message, chat_id=chat_id)
        store.add_message("assistant", reply, chat_id=chat_id)
        await update.message.reply_text(reply)
        return

    await update.message.chat.send_action("typing")

    try:
        history = store.get_history(limit=config.CHAT_HISTORY_LIMIT, chat_id=chat_id)
        response = await agent.run(user_message, history, user_id=update.effective_user.id)

        store.add_message("user", user_message, chat_id=chat_id)
        store.add_message("assistant", response, chat_id=chat_id)
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
