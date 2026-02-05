"""
Web Search usando DuckDuckGo Instant Answer API (Grátis, sem cadastro)
Módulo refatorado para uso como função Python pura
"""

import requests
import json


def search_duckduckgo(query: str) -> dict:
    """
    Busca usando DuckDuckGo Instant Answer API

    Args:
        query: Termo de busca

    Returns:
        dict com query, results, total e source
    """
    try:
        url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        results = []

        # Abstract (resposta principal)
        if data.get("Abstract"):
            results.append(
                {
                    "type": "abstract",
                    "title": data.get("Heading", "Resultado"),
                    "text": data.get("Abstract"),
                    "url": data.get("AbstractURL", ""),
                }
            )

        # Related Topics
        for topic in data.get("RelatedTopics", [])[:5]:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append(
                    {
                        "type": "related",
                        "title": topic.get("Text", "").split(" - ")[0],
                        "text": topic.get("Text", ""),
                        "url": topic.get("FirstURL", ""),
                    }
                )

        return {
            "query": query,
            "results": results,
            "total": len(results),
            "source": "DuckDuckGo Instant Answer API",
        }

    except Exception as e:
        return {"error": str(e), "results": []}


async def search_ddg(query: str, max_results: int = 5) -> dict:
    """
    Função async wrapper para search_duckduckgo

    Args:
        query: Termo de busca
        max_results: Número máximo de resultados (não usado, mantido para compatibilidade)

    Returns:
        dict no formato {"success": bool, "results": list} ou {"success": bool, "error": str}
    """
    try:
        result = search_duckduckgo(query)

        if "error" in result and result["error"]:
            return {"success": False, "error": result["error"]}

        # Limitar resultados se necessário
        if max_results and len(result.get("results", [])) > max_results:
            result["results"] = result["results"][:max_results]
            result["total"] = len(result["results"])

        return {"success": True, "results": result.get("results", [])}
    except Exception as e:
        return {"success": False, "error": str(e)}
