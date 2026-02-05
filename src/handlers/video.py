"""Handler para vídeos"""

import base64
import logging
from telegram import Update
from telegram.ext import ContextTypes

from security.auth import require_auth
from security import secure_files, SafeSubprocessExecutor
from workspace.storage.sqlite_store import SQLiteStore
from agent_setup import groq_client

logger = logging.getLogger(__name__)


@require_auth
async def handle_video(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    store: SQLiteStore,
):
    """Handler para vídeos (SecureFileManager + SafeSubprocessExecutor)"""
    logger.info("Vídeo recebido")

    await update.message.chat.send_action("typing")

    try:
        video = update.message.video
        video_file = await video.get_file()
        caption = update.message.caption or "Descreva o que você vê"

        with secure_files.temp_file(suffix=".mp4") as video_path:
            await video_file.download_to_drive(str(video_path))
            with secure_files.temp_file(suffix=".jpg") as frame_path:
                success_frame, _, err_frame = await SafeSubprocessExecutor.run(
                    ["ffmpeg", "-i", str(video_path), "-vframes", "1", "-q:v", "2", str(frame_path)],
                    timeout=30,
                )
                if not success_frame:
                    logger.warning(f"FFmpeg frame: {err_frame}")
                    raise RuntimeError("Falha ao extrair frame")

                with secure_files.temp_file(suffix=".mp3") as audio_path:
                    success_audio, _, _ = await SafeSubprocessExecutor.run(
                        ["ffmpeg", "-i", str(video_path), "-vn", "-acodec", "mp3", str(audio_path)],
                        timeout=30,
                    )
                    has_audio = success_audio and audio_path.stat().st_size > 1000

                    with open(frame_path, "rb") as f:
                        image_data = base64.b64encode(f.read()).decode("utf-8")

                    vision_response = groq_client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": f"Descreva esta imagem em detalhes: {caption}"},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
                                ],
                            }
                        ],
                        temperature=0.5,
                        max_completion_tokens=512,
                    )
                    visual_analysis = vision_response.choices[0].message.content

                    audio_transcription = ""
                    if has_audio:
                        try:
                            with open(audio_path, "rb") as audio_file:
                                transcription = groq_client.audio.transcriptions.create(
                                    file=audio_file,
                                    model="whisper-large-v3-turbo",
                                    response_format="text",
                                )
                                audio_transcription = transcription
                        except Exception as ae:
                            logger.debug(f"Transcrição de áudio falhou: {ae}")

                    response_parts = ["🎬 Vídeo analisado:\n", f"📸 {visual_analysis}"]
                    if audio_transcription and len(audio_transcription.strip()) > 5:
                        response_parts.append(f'\n\n🎤 Áudio: "{audio_transcription.strip()}"')
                    result = "\n".join(response_parts)

                    store.add_message("user", f"[VÍDEO] {caption}")
                    store.add_message("assistant", result)
                    await update.message.reply_text(result)

    except Exception as e:
        logger.error(f"Erro ao processar vídeo: {e}", exc_info=True)
        await update.message.reply_text("Ocorreu um erro ao analisar o vídeo. Tente novamente.")
