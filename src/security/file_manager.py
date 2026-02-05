"""Sandbox - Gerenciamento seguro de arquivos temporários"""

import os
import re
import tempfile
import logging
import shutil
from pathlib import Path
from contextlib import contextmanager
from typing import List, Set

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

logger = logging.getLogger(__name__)


class SecureFileManager:
    """Gerencia arquivos temporários com sanitização rigorosa"""

    ALLOWED_EXTENSIONS: Set[str] = {
        "xlsx",
        "xls",
        "csv",
        "docx",
        "md",
        "txt",
        "jpg",
        "jpeg",
        "png",
        "gif",
        "webp",
        "mp4",
        "mov",
        "avi",
        "mkv",
        "mp3",
        "ogg",
        "wav",
        "m4a",
    }

    MAX_FILE_SIZE_MB = 50

    def __init__(self, base_temp_dir: str = "/tmp/moltbot_secure"):
        self.base_path = Path(base_temp_dir)
        self.base_path.mkdir(parents=True, exist_ok=True, mode=0o700)
        logger.info(f"SecureFileManager inicializado em {self.base_path}")

    def sanitize_filename(self, filename: str) -> str:
        """Remove path traversal e caracteres perigosos"""
        # Remove qualquer path component
        filename = os.path.basename(filename)

        # Remove caracteres não-alfanuméricos (exceto . - _)
        filename = re.sub(r"[^\w\-\.]", "_", filename)

        # Remove múltiplos pontos (path traversal)
        filename = re.sub(r"\.{2,}", ".", filename)

        # Limita tamanho do nome
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:195] + ext

        # Garante extensão permitida
        if "." in filename:
            ext = filename.rsplit(".", 1)[-1].lower()
            if ext not in self.ALLOWED_EXTENSIONS:
                raise ValueError(f"Extensão '{ext}' não permitida")

        return filename

    def validate_mime_type(self, file_path: Path, expected_types: List[str]) -> bool:
        """Valida MIME type real do arquivo (evita bypass por extensão)"""
        if not MAGIC_AVAILABLE:
            logger.warning(
                "python-magic não disponível, pulando validação de MIME type"
            )
            return True

        try:
            mime = magic.from_file(str(file_path), mime=True)
            return any(expected in mime for expected in expected_types)
        except Exception as e:
            logger.error(f"Erro ao validar MIME type de {file_path}: {e}")
            return False

    def validate_file_size(self, file_path: Path) -> bool:
        """Valida tamanho do arquivo"""
        try:
            size = file_path.stat().st_size
            max_size = self.MAX_FILE_SIZE_MB * 1024 * 1024
            if size > max_size:
                size_mb = size / 1024 / 1024
                logger.warning(
                    f"Arquivo muito grande: {size_mb:.1f}MB (máx: {self.MAX_FILE_SIZE_MB}MB)"
                )
                return False
            return True
        except Exception as e:
            logger.error(f"Erro ao verificar tamanho de {file_path}: {e}")
            return False

    @contextmanager
    def temp_file(self, suffix: str, prefix: str = "moltbot_"):
        """Context manager que garante limpeza mesmo em caso de exceção"""
        # Valida extensão
        ext = suffix.lstrip(".").lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Extensão não permitida: {suffix}")

        # Garante que o suffix comece com ponto
        if not suffix.startswith("."):
            suffix = "." + suffix

        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=self.base_path)
        os.close(fd)  # Fecha file descriptor imediatamente

        file_path = Path(path)
        logger.debug(f"Arquivo temporário criado: {file_path}")

        try:
            yield file_path
        finally:
            # Garante deleção mesmo se ocorrer exceção
            try:
                if file_path.exists():
                    file_path.unlink()
                    logger.debug(f"Arquivo temporário removido: {file_path}")
            except Exception as e:
                logger.error(f"Falha ao remover arquivo temporário {path}: {e}")

    @contextmanager
    def temp_directory(self, prefix: str = "moltbot_dir_"):
        """Context manager para diretório temporário seguro"""
        dir_path = tempfile.mkdtemp(prefix=prefix, dir=self.base_path)
        path = Path(dir_path)
        logger.debug(f"Diretório temporário criado: {path}")

        try:
            yield path
        finally:
            try:
                if path.exists():
                    shutil.rmtree(path)
                    logger.debug(f"Diretório temporário removido: {path}")
            except Exception as e:
                logger.error(f"Falha ao remover diretório temporário {path}: {e}")

    def cleanup_old_files(self, max_age_hours: int = 24):
        """Remove arquivos temporários antigos"""
        import time

        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600

            for item in self.base_path.iterdir():
                try:
                    item_time = item.stat().st_mtime
                    if current_time - item_time > max_age_seconds:
                        if item.is_file():
                            item.unlink()
                            logger.info(f"Arquivo antigo removido: {item}")
                        elif item.is_dir():
                            shutil.rmtree(item)
                            logger.info(f"Diretório antigo removido: {item}")
                except Exception as e:
                    logger.error(f"Erro ao processar {item}: {e}")
        except Exception as e:
            logger.error(f"Erro ao limpar arquivos antigos: {e}")


# Instância global
secure_files = SecureFileManager()
