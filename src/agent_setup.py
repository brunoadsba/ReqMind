"""Setup do agente e utilitários relacionados"""

import os
import logging
from groq import Groq

try:
    from elevenlabs import ElevenLabs, VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ElevenLabs = None
    VoiceSettings = None
    ELEVENLABS_AVAILABLE = False

from workspace.core.tools import ToolRegistry
from workspace.core.agent import Agent
from workspace.tools.web_search import web_search, WEB_SEARCH_SCHEMA
from workspace.tools.rag_tools import (
    rag_search,
    save_memory,
    RAG_SEARCH_SCHEMA,
    SAVE_MEMORY_SCHEMA,
)
from workspace.tools.filesystem import (
    read_file,
    write_file,
    list_directory,
    READ_FILE_SCHEMA,
    WRITE_FILE_SCHEMA,
    LIST_DIRECTORY_SCHEMA,
)
from workspace.tools.code_tools import (
    search_code,
    git_status,
    git_diff,
    SEARCH_CODE_SCHEMA,
    GIT_STATUS_SCHEMA,
    GIT_DIFF_SCHEMA,
)
from workspace.tools.extra_tools import (
    get_weather,
    get_news,
    create_reminder,
    create_chart,
    generate_image,
    WEATHER_SCHEMA,
    NEWS_SCHEMA,
    REMINDER_SCHEMA,
    CHART_SCHEMA,
    IMAGE_GEN_SCHEMA,
)

logger = logging.getLogger(__name__)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY")) if ELEVENLABS_AVAILABLE else None


def create_agent_no_sandbox():
    """Cria agente com todas as ferramentas registradas"""
    registry = ToolRegistry()
    registry.register("web_search", web_search, WEB_SEARCH_SCHEMA)
    registry.register("rag_search", rag_search, RAG_SEARCH_SCHEMA)
    registry.register("save_memory", save_memory, SAVE_MEMORY_SCHEMA)
    registry.register("search_code", search_code, SEARCH_CODE_SCHEMA)
    registry.register("read_file", read_file, READ_FILE_SCHEMA)
    registry.register("write_file", write_file, WRITE_FILE_SCHEMA)
    registry.register("list_directory", list_directory, LIST_DIRECTORY_SCHEMA)
    registry.register("git_status", git_status, GIT_STATUS_SCHEMA)
    registry.register("git_diff", git_diff, GIT_DIFF_SCHEMA)
    # Ferramentas extras (apenas as confiáveis)
    registry.register("get_weather", get_weather, WEATHER_SCHEMA)
    registry.register("get_news", get_news, NEWS_SCHEMA)
    registry.register("create_reminder", create_reminder, REMINDER_SCHEMA)
    registry.register("create_chart", create_chart, CHART_SCHEMA)
    registry.register("generate_image", generate_image, IMAGE_GEN_SCHEMA)
    return Agent(registry)


def text_to_speech(text: str) -> bytes:
    """Converte texto em áudio usando ElevenLabs (opcional)"""
    if not elevenlabs_client:
        logger.debug("ElevenLabs não disponível (pacote não instalado ou API key não configurada)")
        return None
    try:
        # Força português no texto
        text_pt = f"[pt-BR] {text}"

        # Voz masculina grave em português (Antoni - melhor para PT-BR)
        audio = elevenlabs_client.text_to_speech.convert(
            text=text_pt,
            voice_id="ErXwobaYiN019PkySvjV",  # Antoni - voz masculina
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.7, similarity_boost=0.85, style=0.3, use_speaker_boost=True
            ),
            output_format="mp3_44100_128",
        )

        # Converte generator para bytes
        audio_bytes = b"".join(audio)
        return audio_bytes
    except Exception as e:
        logger.error(f"Erro ao gerar áudio: {e}")
        return None
