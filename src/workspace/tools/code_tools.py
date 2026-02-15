"""Code Tools - Ferramentas para trabalhar com código"""
import subprocess
import os
import logging

from config.settings import config

logger = logging.getLogger(__name__)

async def search_code(query: str, path: str = None, extensions: list = None) -> dict:
    if extensions is None:
        extensions = [".py", ".js", ".ts", ".jsx", ".tsx"]
    
    try:
        # Usa config.BASE_DIR como path padrão se não especificado
        if path is None:
            full_path = str(config.BASE_DIR)
        else:
            full_path = os.path.expanduser(path)
        
        # Constrói o comando grep com argumentos separados (sem shell=True)
        cmd = ["grep", "-rn", query]
        for ext in extensions:
            cmd.extend(["--include", f"*{ext}"])
        cmd.append(full_path)
        
        result = subprocess.run(cmd, shell=False, capture_output=True, text=True, timeout=10)
        
        return {"success": True, "results": result.stdout, "matches": len(result.stdout.split('\n')) if result.stdout else 0}
    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        return {"success": False, "error": str(e)}

async def git_status(repo_path: str = None) -> dict:
    if repo_path is None:
        repo_path = str(config.BASE_DIR)
    try:
        full_path = os.path.expanduser(repo_path)
        result = subprocess.run(["git", "status"], cwd=full_path, capture_output=True, text=True, timeout=5)
        return {"success": True, "status": result.stdout}
    except Exception as e:
        logger.error(f"Erro no git: {e}")
        return {"success": False, "error": str(e)}

async def git_diff(repo_path: str = "~/clawd") -> dict:
    try:
        full_path = os.path.expanduser(repo_path)
        result = subprocess.run(["git", "diff"], cwd=full_path, capture_output=True, text=True, timeout=5)
        return {"success": True, "diff": result.stdout}
    except Exception as e:
        logger.error(f"Erro no git diff: {e}")
        return {"success": False, "error": str(e)}

SEARCH_CODE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_code",
        "description": "Busca termo em arquivos de código",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Termo a buscar"},
                "path": {"type": "string", "description": "Diretório (padrão: ~/clawd)"},
                "extensions": {"type": "array", "items": {"type": "string"}, "description": "Extensões de arquivo"}
            },
            "required": ["query"]
        }
    }
}

GIT_STATUS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "git_status",
        "description": "Mostra status do repositório git",
        "parameters": {
            "type": "object",
            "properties": {"repo_path": {"type": "string", "description": "Caminho do repo"}}
        }
    }
}

GIT_DIFF_SCHEMA = {
    "type": "function",
    "function": {
        "name": "git_diff",
        "description": "Mostra diferenças não commitadas",
        "parameters": {
            "type": "object",
            "properties": {"repo_path": {"type": "string", "description": "Caminho do repo"}}
        }
    }
}
