"""Git Manager - Ferramentas para gerenciar repositórios Git"""
import subprocess
import os
import logging
import asyncio
from typing import List, Optional
from config.settings import config

logger = logging.getLogger(__name__)

async def _ensure_repos_dir():
    repos_dir = config.DATA_DIR / "repos"
    os.makedirs(repos_dir, exist_ok=True)
    return repos_dir

async def git_clone(repo_url: str, dest_name: str = None) -> dict:
    """Clona um repositório Git público"""
    try:
        repos_dir = await _ensure_repos_dir()
        
        # Se não fornecer nome, usa o nome do repo
        if not dest_name:
            if repo_url.endswith(".git"):
                dest_name = repo_url.split("/")[-1][:-4]
            else:
                dest_name = repo_url.split("/")[-1]
        
        # Sanitizar nome do diretório
        dest_name = "".join([c for c in dest_name if c.isalnum() or c in ('-', '_')])
        target_path = repos_dir / dest_name
        
        if target_path.exists():
            return {"success": False, "error": f"Repositório '{dest_name}' já existe. Use git_pull para atualizar."}

        # Executa git clone
        process = await asyncio.create_subprocess_exec(
            "git", "clone", repo_url, str(target_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return {
                "success": True, 
                "message": f"Repositório clonado em {target_path}",
                "path": str(target_path)
            }
        else:
            return {"success": False, "error": stderr.decode()}
            
    except Exception as e:
        logger.error(f"Erro no git clone: {e}")
        return {"success": False, "error": str(e)}

async def git_pull(repo_name: str) -> dict:
    """Atualiza um repositório existente"""
    try:
        repos_dir = await _ensure_repos_dir()
        target_path = repos_dir / repo_name
        
        if not target_path.exists():
            return {"success": False, "error": f"Repositório '{repo_name}' não encontrado."}
            
        # Executa git pull
        process = await asyncio.create_subprocess_exec(
            "git", "pull",
            cwd=str(target_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return {
                "success": True, 
                "message": f"Repositório '{repo_name}' atualizado.",
                "output": stdout.decode()
            }
        else:
             return {"success": False, "error": stderr.decode()}

    except Exception as e:
        logger.error(f"Erro no git pull: {e}")
        return {"success": False, "error": str(e)}

async def git_list_repos() -> dict:
    """Lista repositórios clonados"""
    try:
        repos_dir = await _ensure_repos_dir()
        repos = [d.name for d in repos_dir.iterdir() if d.is_dir()]
        return {"success": True, "repos": repos}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Schemas para o Agente
GIT_CLONE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "git_clone",
        "description": "Clona um repositório Git público para análise",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_url": {"type": "string", "description": "URL HTTPS do repositório"},
                "dest_name": {"type": "string", "description": "Nome da pasta destino (opcional)"}
            },
            "required": ["repo_url"]
        }
    }
}

GIT_PULL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "git_pull",
        "description": "Atualiza um repositório Git existente",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_name": {"type": "string", "description": "Nome da pasta do repositório"}
            },
            "required": ["repo_name"]
        }
    }
}

GIT_LIST_REPOS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "git_list_repos",
        "description": "Lista repositórios clonados disponíveis",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}
