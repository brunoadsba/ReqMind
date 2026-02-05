"""Handlers do bot Telegram organizados por tipo de mídia"""

from .message import handle_message
from .photo import handle_photo
from .video import handle_video
from .voice import handle_voice
from .audio import handle_audio
from .document import handle_document

__all__ = [
    "handle_message",
    "handle_photo",
    "handle_video",
    "handle_voice",
    "handle_audio",
    "handle_document",
]
