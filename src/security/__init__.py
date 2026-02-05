"""Módulo de segurança - __init__.py"""

from .auth import require_auth, is_admin, ALLOWED_USERS
from .sanitizer import (
    sanitize_youtube_url,
    sanitize_filename,
    validate_path,
    safe_subprocess,
)
from .rate_limiter import message_limiter, media_limiter, youtube_limiter
from .media_validator import (
    validate_image,
    validate_video,
    validate_audio,
    validate_file_size,
)
from .file_manager import SecureFileManager, secure_files
from .executor import SafeSubprocessExecutor, safe_run

__all__ = [
    "require_auth",
    "is_admin",
    "ALLOWED_USERS",
    "sanitize_youtube_url",
    "sanitize_filename",
    "validate_path",
    "safe_subprocess",
    "message_limiter",
    "media_limiter",
    "youtube_limiter",
    "validate_image",
    "validate_video",
    "validate_audio",
    "validate_file_size",
    "SecureFileManager",
    "secure_files",
    "SafeSubprocessExecutor",
    "safe_run",
]
