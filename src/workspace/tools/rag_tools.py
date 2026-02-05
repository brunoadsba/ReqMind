"""RAG Tools - Ferramentas de memória"""

import logging
from workspace.tools.impl.rag_memory import rag_search as _rag_search, save_to_memory

logger = logging.getLogger(__name__)


async def rag_search(query: str) -> dict:
    try:
        result = await _rag_search(query)
        if result.get("success"):
            results = result.get("results", [])
            return {"success": True, "results": results}
        else:
            return {"success": False, "error": result.get("error", "Erro desconhecido")}
    except Exception as e:
        logger.error(f"Erro na busca RAG: {e}")
        return {"success": False, "error": str(e)}


async def save_memory(content: str, category: str = "general") -> dict:
    try:
        result = await save_to_memory(content, category=category)
        return result
    except Exception as e:
        logger.error(f"Erro ao salvar memória: {e}")
        return {"success": False, "error": str(e)}


RAG_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "rag_search",
        "description": "Busca informações na memória pessoal de Bruno",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "O que buscar"}},
            "required": ["query"],
        },
    },
}

SAVE_MEMORY_SCHEMA = {
    "type": "function",
    "function": {
        "name": "save_memory",
        "description": "Salva informação importante na memória",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Conteúdo a salvar"},
                "category": {"type": "string", "description": "Categoria (opcional)"},
            },
            "required": ["content"],
        },
    },
}
