"""
RAG (Retrieval-Augmented Generation) Simplificado
Gerencia memória em arquivo JSON local
Módulo refatorado para uso como função Python pura
"""

import json
import os
from datetime import datetime
from pathlib import Path


def get_storage_path() -> Path:
    """Retorna o caminho do arquivo de memória"""
    # Usar diretório dentro do projeto (não mais ~/.clawdbot/)
    storage_dir = Path.home() / ".assistente" / "data"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir / "memory.json"


def load_memory() -> dict:
    """Carrega a memória do arquivo JSON"""
    storage_file = get_storage_path()

    if storage_file.exists():
        with open(storage_file, "r", encoding="utf-8") as f:
            return json.load(f)

    return {"knowledge": [], "conversations": [], "documents": []}


def save_memory(data: dict) -> None:
    """Salva a memória no arquivo JSON"""
    storage_file = get_storage_path()
    storage_file.parent.mkdir(parents=True, exist_ok=True)

    with open(storage_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_knowledge(text: str) -> dict:
    """
    Adiciona conhecimento à memória

    Args:
        text: Texto a ser armazenado

    Returns:
        dict com success e message
    """
    try:
        memory = load_memory()
        memory["knowledge"].append(
            {"text": text, "timestamp": datetime.now().isoformat()}
        )
        save_memory(memory)
        return {"success": True, "message": "Informação salva na memória"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def search_memory(query: str) -> dict:
    """
    Busca na memória por query

    Args:
        query: Termo de busca

    Returns:
        dict com success e results (lista de matches)
    """
    try:
        memory = load_memory()
        results = []
        query_lower = query.lower()

        for item in memory.get("knowledge", []):
            if query_lower in item.get("text", "").lower():
                results.append(item)

        return {"success": True, "results": results}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Funções async para compatibilidade com o resto do código
async def rag_search(query: str) -> dict:
    """Wrapper async para search_memory"""
    return search_memory(query)


async def save_to_memory(content: str, category: str = "general") -> dict:
    """Wrapper async para add_knowledge"""
    return add_knowledge(content)
