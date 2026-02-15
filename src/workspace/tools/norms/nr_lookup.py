"""
Ferramenta de consulta às Normas Regulamentadoras (NRs).
Sistema híbrido: busca na memória local ou web search.

Uso via tool calling:
- "me explica a NR-35" → busca na memória (instantâneo)
- "o que diz a NR-18" → web search (sempre atual)
"""

import re
from typing import Optional

# NRs que estão na memória local (carregadas via scripts feed_nr*.py)
NR_MEMORY = {
    "nr-1": "NR-1 - Disposições Gerais e Gerenciamento de Riscos",
    "nr-5": "NR-5 - CIPA",
    "nr-6": "NR-6 - EPI",
    "nr-10": "NR-10 - Eletricidade",
    "nr-29": "NR-29 - Trabalho Portuário",
    "nr-33": "NR-33 - Espaço Confinado",
    "nr-35": "NR-35 - Trabalho em Altura",
}


def extract_nr_number(message: str) -> Optional[str]:
    """
    Extrai o número da NR de uma mensagem.

    Exemplos:
    - "NR-35" → "35"
    - "NR 35" → "35"
    - "nr35" → "35"
    - "Norma 10" → "10"
    """
    # Padrões: NR-35, NR 35, nr35, nr-35, Norma 10
    patterns = [
        r"nr[s]?\s*[-\s]*(\d+)",  # NR-35, NR 35, nr35, nr-35
        r"norma\s*[-\s]*(\d+)",  # Norma 35, norma-35
    ]

    message_lower = message.lower()

    for pattern in patterns:
        match = re.search(pattern, message_lower)
        if match:
            nr = match.group(1)
            # Remove zeros à esquerda
            nr = nr.lstrip("0") or "0"
            return nr

    return None


def is_nr_in_memory(nr_number: str) -> bool:
    """Verifica se a NR está na memória local."""
    nr_key = f"nr{nr_number}".lower()
    nr_key = re.sub(r"^nr0+", "nr-", nr_key)  # nr01 → nr-1
    return nr_key in NR_MEMORY


async def nr_lookup(query: str) -> dict:
    """
    Consulta uma Norma Regulamentadora.

    Args:
        query: Pergunta sobre NR (ex: "me explica a NR-35")

    Returns:
        dict com status, tipo (memória/web), conteúdo e fonte
    """
    try:
        # Extrai número da NR
        nr_number = extract_nr_number(query)

        if not nr_number:
            return {
                "success": False,
                "error": "Não foi possível identificar o número da NR na pergunta",
                "tip": "Use formato: 'NR-35', 'NR 35', 'nr35', etc.",
            }

        # Verifica se NR está na memória local
        if is_nr_in_memory(nr_number):
            from workspace.tools.impl.rag_memory import search_memory

            search_query = f"NR-{nr_number}"
            result = search_memory(search_query)

            if result.get("success") and result.get("results"):
                texts = [r.get("text", "") for r in result["results"][:2] if r.get("text")]
                if texts:
                    return {
                        "success": True,
                        "type": "memory",
                        "nr": f"NR-{nr_number}",
                        "nr_name": NR_MEMORY.get(f"nr-{nr_number}", f"NR-{nr_number}"),
                        "content": texts[0],
                        "source": "memória local (RAG)",
                        "query": query,
                    }

            return {
                "success": False,
                "error": f"NR-{nr_number} está registrada mas conteúdo não foi encontrado na memória",
                "tip": "Execute o script de feed correspondente: PYTHONPATH=src python scripts/feed_nr{nr_number}.py",
            }

        # NR não está na memória - precisa de web search
        from workspace.tools.web_search import web_search

        web_query = f"NR-{nr_number} Ministério do Trabalho Norma Regulamentadora"
        search_result = await web_search(web_query)

        if search_result.get("success") and search_result.get("results"):
            results = search_result["results"][:3]
            content_parts = [f"📋 Resultados para NR-{nr_number} (busca web):\n"]

            for i, r in enumerate(results, 1):
                title = r.get("title", "Sem título")
                snippet = r.get("body", r.get("snippet", "Sem descrição"))
                href = r.get("href", r.get("url", ""))

                content_parts.append(f"\n**{i}. {title}**")
                content_parts.append(f"{snippet[:300]}...")
                if href:
                    content_parts.append(f"🔗 {href}")

            return {
                "success": True,
                "type": "web_search",
                "nr": f"NR-{nr_number}",
                "nr_name": f"NR-{nr_number} - Não carregada na memória",
                "content": "\n".join(content_parts),
                "source": "web search (DuckDuckGo)",
                "results_count": len(results),
                "query": query,
            }

        return {
            "success": False,
            "error": f"Não foi possível encontrar informações sobre NR-{nr_number}",
            "tip": "Tente reformular a pergunta ou consultar diretamente no site do Ministério do Trabalho",
        }

    except ImportError as e:
        return {
            "success": False,
            "error": f"Dependência não disponível: {e}",
            "tip": "Verifique se as ferramentas necessárias estão instaladas",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao consultar NR: {str(e)}",
            "tip": "Tente novamente ou use web search diretamente",
        }


def get_memory_nr_list() -> list[dict]:
    """
    Retorna lista de NRs disponíveis na memória.

    Returns:
        Lista de dicts com número, nome e status
    """
    return [{"nr": nr, "name": name, "status": "memory"} for nr, name in NR_MEMORY.items()]


def format_nr_response(result: dict) -> str:
    """
    Formata o resultado da consulta NR para exibição.

    Args:
        result: Dict retornado por nr_lookup()

    Returns:
        String formatada para resposta ao usuário
    """
    if not result.get("success"):
        return f"❌ {result.get('error')}\n\n💡 {result.get('tip', '')}"

    # Header
    lines = [
        f"🔍 **{result['nr_name']}**",
        f"📦 Fonte: {result['source']}",
        "",
        result["content"],
    ]

    # Footer com dica
    if result.get("type") == "web_search":
        lines.extend(
            [
                "",
                f"💡 Esta NR ainda não está na memória local.",
                f"   Para respostas instantâneas, adicione com: `PYTHONPATH=src python scripts/feed_nr{result['nr'].replace('NR-', '')}.py`",
            ]
        )

    return "\n".join(lines)
