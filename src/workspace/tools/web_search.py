"""Web Search - Busca na web usando DuckDuckGo"""

import logging
from workspace.tools.impl import search_ddg

logger = logging.getLogger(__name__)


async def web_search(query: str, max_results: int = 5) -> dict:
    try:
        return await search_ddg(query, max_results=max_results)
    except Exception as e:
        logger.error(f"Erro na busca web: {e}")
        return {"success": False, "error": str(e)}


WEB_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Busca informações na web usando DuckDuckGo",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Termo ou pergunta para buscar",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Número máximo de resultados",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}
