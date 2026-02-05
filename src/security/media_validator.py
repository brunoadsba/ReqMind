"""Validação de arquivos de mídia"""
import os
import logging

logger = logging.getLogger(__name__)

# Limites de tamanho (em bytes)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
MAX_AUDIO_SIZE = 20 * 1024 * 1024  # 20MB

# Extensões permitidas
ALLOWED_IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ALLOWED_VIDEO_EXTS = {'.mp4', '.mov', '.avi', '.mkv'}
ALLOWED_AUDIO_EXTS = {'.mp3', '.ogg', '.wav', '.m4a'}

def validate_file_size(file_path: str, max_size: int) -> tuple[bool, str]:
    """Valida tamanho do arquivo"""
    try:
        size = os.path.getsize(file_path)
        if size > max_size:
            size_mb = size / 1024 / 1024
            max_mb = max_size / 1024 / 1024
            return False, f"Arquivo muito grande: {size_mb:.1f}MB (máx: {max_mb:.1f}MB)"
        return True, "OK"
    except Exception as e:
        return False, f"Erro ao verificar tamanho: {e}"

def validate_image(file_path: str) -> tuple[bool, str]:
    """Valida arquivo de imagem"""
    # Verifica extensão
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTS:
        return False, f"Extensão não permitida: {ext}"
    
    # Verifica tamanho
    return validate_file_size(file_path, MAX_IMAGE_SIZE)

def validate_video(file_path: str) -> tuple[bool, str]:
    """Valida arquivo de vídeo"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ALLOWED_VIDEO_EXTS:
        return False, f"Extensão não permitida: {ext}"
    
    return validate_file_size(file_path, MAX_VIDEO_SIZE)

def validate_audio(file_path: str) -> tuple[bool, str]:
    """Valida arquivo de áudio"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ALLOWED_AUDIO_EXTS:
        return False, f"Extensão não permitida: {ext}"
    
    return validate_file_size(file_path, MAX_AUDIO_SIZE)
