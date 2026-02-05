"""Configuração centralizada do Moltbot"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Config:
    """Configuração centralizada do sistema"""

    # Paths
    BASE_DIR: Path = field(
        default_factory=lambda: Path(
            os.getenv("MOLTBOT_DIR", Path(__file__).parent.parent.resolve())
        )
    )

    TEMP_DIR: Path = field(
        default_factory=lambda: Path(os.getenv("MOLTBOT_TEMP", "/tmp/moltbot_secure"))
    )

    @property
    def DATA_DIR(self) -> Path:
        return self.BASE_DIR / "dados"

    @property
    def WORKSPACE_DIR(self) -> Path:
        return self.BASE_DIR / "workspace"

    @property
    def SECURITY_DIR(self) -> Path:
        return self.BASE_DIR / "security"

    @property
    def CONFIG_DIR(self) -> Path:
        return self.BASE_DIR / "config"

    # API Models
    GROQ_MODEL_VISION: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    GROQ_MODEL_CHAT: str = "llama-3.3-70b-versatile"
    WHISPER_MODEL: str = "whisper-large-v3-turbo"

    # ElevenLabs
    ELEVENLABS_VOICE_ID: str = "ErXwobaYiN019PkySvjV"  # Antoni - voz masculina
    ELEVENLABS_MODEL: str = "eleven_multilingual_v2"

    # Limits
    MAX_FILE_SIZE_MB: int = 50
    MAX_VIDEO_DURATION_MIN: int = 10
    REQUEST_TIMEOUT: float = 30.0
    MAX_ITERATIONS: int = 5  # Máximo de iterações do agent

    # Rate Limiting
    RATE_LIMIT_MESSAGES: int = 20  # mensagens por minuto
    RATE_LIMIT_MEDIA: int = 5  # mídia por minuto
    RATE_LIMIT_YOUTUBE: int = 3  # YouTube por 5 minutos

    # Security
    @property
    def ALLOWED_USERS(self) -> List[int]:
        users_env = os.getenv("ALLOWED_USERS", "")
        if users_env:
            try:
                return [int(uid.strip()) for uid in users_env.split(",") if uid.strip()]
            except ValueError:
                return []
        return []

    # Database
    @property
    def DATABASE_PATH(self) -> Path:
        return self.BASE_DIR / "moltbot.db"

    # Reminders
    @property
    def REMINDERS_FILE(self) -> Path:
        return self.TEMP_DIR / "moltbot_reminders.json"

    # Timezone
    TIMEZONE: str = "America/Sao_Paulo"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# Instância global de configuração
config = Config()
