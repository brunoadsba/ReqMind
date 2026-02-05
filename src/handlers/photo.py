"""Handler para fotos"""

import base64
import logging
import requests
from telegram import Update
from telegram.ext import ContextTypes

from security.auth import require_auth
from workspace.storage.sqlite_store import SQLiteStore
from agent_setup import groq_client

logger = logging.getLogger(__name__)


@require_auth
async def handle_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    store: SQLiteStore,
):
    """Handler para fotos"""
    logger.info("Foto recebida")

    await update.message.chat.send_action("typing")

    try:
        # Pega a foto de maior resolução
        photo = update.message.photo[-1]
        photo_file = await photo.get_file()
        photo_url = photo_file.file_path

        # Pega caption se houver
        caption = update.message.caption or "Descreva esta imagem em detalhes"

        # Usa Groq Vision diretamente (mais rápido e confiável)
        logger.info(f"Baixando imagem de: {photo_url}")
        img_response = requests.get(photo_url, timeout=10)
        img_data = base64.b64encode(img_response.content).decode("utf-8")

        logger.info("Analisando com Groq Vision...")
        vision_response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": caption},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_data}"},
                        },
                    ],
                }
            ],
            temperature=0.5,
            max_completion_tokens=512,
        )
        response = vision_response.choices[0].message.content

        store.add_message("user", f"[IMAGEM] {caption}")
        store.add_message("assistant", response)

        await update.message.reply_text(response)
        logger.info("Imagem analisada com sucesso")

    except Exception as e:
        logger.error(f"Erro ao processar imagem: {e}", exc_info=True)
        await update.message.reply_text("Ocorreu um erro ao analisar a imagem. Tente novamente.")
