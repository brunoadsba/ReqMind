"""Filesystem Tools - Operações de arquivo com validação de path"""
import os
import logging

from security.sanitizer import validate_path
from config.settings import config

logger = logging.getLogger(__name__)

def _allowed_bases():
    return [str(config.BASE_DIR), str(config.TEMP_DIR)]

async def read_file(path: str) -> dict:
    try:
        ok, resolved = validate_path(path, _allowed_bases())
        if not ok:
            return {"success": False, "error": resolved}
        full_path = resolved
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"success": True, "content": content, "path": full_path}
    except Exception as e:
        logger.error(f"Erro ao ler arquivo: {e}")
        return {"success": False, "error": str(e)}

async def write_file(path: str, content: str) -> dict:
    try:
        ok, resolved = validate_path(path, _allowed_bases())
        if not ok:
            return {"success": False, "error": resolved}
        full_path = resolved
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "message": f"Arquivo salvo em {full_path}"}
    except Exception as e:
        logger.error(f"Erro ao escrever arquivo: {e}")
        return {"success": False, "error": str(e)}

def _normalize_project_path(path: str) -> str:
    """Se o usuário/LLM pedir 'diretório atual' ou '.', usa BASE_DIR do projeto."""
    if not path or not (p := path.strip()):
        return str(config.BASE_DIR)
    p_lower = p.lower()
    if p in (".", "current", "atual"):
        return str(config.BASE_DIR)
    if any(
        x in p_lower
        for x in ("diretório atual", "diretorio atual", "atual do projeto", "diretório do projeto")
    ):
        return str(config.BASE_DIR)
    return path


async def list_directory(path: str) -> dict:
    try:
        path = _normalize_project_path(path)
        ok, resolved = validate_path(path, _allowed_bases())
        if not ok:
            return {"success": False, "error": resolved}
        full_path = resolved
        items = os.listdir(full_path)
        files = [i for i in items if os.path.isfile(os.path.join(full_path, i))]
        directories = [i for i in items if os.path.isdir(os.path.join(full_path, i))]
        return {"success": True, "path": full_path, "files": sorted(files), "directories": sorted(directories), "total": len(items)}
    except Exception as e:
        logger.error(f"Erro ao listar diretório: {e}")
        return {"success": False, "error": str(e)}

READ_FILE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Lê o conteúdo de um arquivo",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Caminho do arquivo"}},
            "required": ["path"]
        }
    }
}

WRITE_FILE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Escreve conteúdo em um arquivo",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Caminho do arquivo"},
                "content": {"type": "string", "description": "Conteúdo a escrever"}
            },
            "required": ["path", "content"]
        }
    }
}

LIST_DIRECTORY_SCHEMA = {
    "type": "function",
    "function": {
        "name": "list_directory",
        "description": "Lista arquivos e diretórios. Para 'diretório atual do projeto' use path '.' ou 'diretório atual do projeto' (lista a raiz do projeto).",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Caminho do diretório (use '.' para raiz do projeto)"}},
            "required": ["path"]
        }
    }
}
