#!/usr/bin/env python3
"""
Baixa o conteúdo de uma NR (Norma Regulamentadora) do site do Ministério do Trabalho.
Uso: python scripts/fetch_nr_govt.py <nr_number>
     python scripts/fetch_nr_govt.py --nr 35 --output nr35.txt
"""

import argparse
import asyncio
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

try:
    import aiohttp
except ImportError:
    print("Erro: aiohttp não instalado. Instale com: pip install aiohttp")
    sys.exit(1)


BASE_URL = "https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/inspecao-do-trabalho/seguranca-e-saude-no-trabalho/ctpp-nrs/normas-regulamentadoras-nrs"
SEARCH_URL = f"{BASE_URL}?searchudo=Norma+Regulamentadora"


async def fetch_page(session: aiohttp.ClientSession, url: str) -> str:
    """Faz request HTTP e retorna conteúdo HTML."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status == 200:
                return await response.text()
            else:
                return None
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}")
        return None


def clean_html_content(html: str) -> str:
    """Remove tags HTML e formata o conteúdo legível."""
    # Remove scripts e estilos
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)

    # Remove comentários HTML
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)

    # Substitui tags por quebras de linha
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</p>", "\n\n", html)
    html = re.sub(r"</h[1-6]>", "\n\n", html)
    html = re.sub(r"</div>", "\n", html)
    html = re.sub(r"</li>", "\n", html)
    html = re.sub(r"</tr>", "\n", html)

    # Remove todas as outras tags HTML
    html = re.sub(r"<[^>]+>", "", html)

    # Decodifica entidades HTML
    html = html.replace("&nbsp;", " ")
    html = html.replace("&amp;", "&")
    html = html.replace("&lt;", "<")
    html = html.replace("&gt;", ">")
    html = html.replace("&quot;", '"')
    html = html.replace("&#39;", "'")

    # Limpa formatação excessiva
    html = re.sub(r"\n{3,}", "\n\n", html)
    html = html.strip()

    return html


async def search_nr(session: aiohttp.ClientSession, nr_number: int) -> str:
    """Busca NR no site do Ministério do Trabalho."""
    search_url = f"{BASE_URL}?searchudo=NR+{nr_number}"

    print(f"Buscando NR-{nr_number}...")
    html = await fetch_page(session, search_url)

    if html:
        content = clean_html_content(html)
        # Filtra conteúdo relevante
        lines = [line for line in content.split("\n") if line.strip() and len(line) > 20]
        return "\n".join(lines[:100])  # Primeiras 100 linhas relevantes

    return None


async def get_nr_direct_url(nr_number: int) -> str:
    """Constrói URL direta para NR."""
    # NRs têm URLs diferentes no portal
    # Alguns usam nr-X, outros usam o número diretamente
    return f"{BASE_URL}/nr-{nr_number}"


async def fetch_nr(nr_number: int, output_file: str = None) -> str:
    """Baixa conteúdo de uma NR específica."""
    async with aiohttp.ClientSession() as session:
        # Tenta URL direta primeiro
        direct_url = await get_nr_direct_url(nr_number)
        print(f"URL: {direct_url}")

        html = await fetch_page(session, direct_url)

        if html:
            content = clean_html_content(html)

            # Filtra conteúdo relevante sobre NR
            lines = []
            for line in content.split("\n"):
                line = line.strip()
                if (
                    line
                    and len(line) > 30
                    and ("NR" in line or "norma" in line.lower() or "segurança" in line.lower())
                ):
                    lines.append(line)

            result = "\n\n".join(lines[:150])  # Limita a 150 linhas

            if output_file:
                Path(output_file).write_text(result)
                print(f"Conteúdo salvo em: {output_file}")

            return result

        # Fallback: busca genérica
        print(f"URL direta não encontrada. Tentando busca...")
        return await search_nr(session, nr_number)


def main():
    parser = argparse.ArgumentParser(
        description="Baixa conteúdo de NRs do site do Ministério do Trabalho"
    )
    parser.add_argument("nr", type=int, help="Número da NR (ex: 1, 5, 6, 10, 35)")
    parser.add_argument("--output", "-o", type=str, help="Arquivo de saída (opcional)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mostra URL e detalhes")

    args = parser.parse_args()

    if args.verbose:
        print(f"Baixando NR-{args.nr}...")

    content = asyncio.run(fetch_nr(args.nr, args.output))

    if content:
        print(f"\nConteúdo da NR-{args.nr} ({len(content)} caracteres):")
        print("-" * 50)
        # Mostra preview
        preview = content[:500] + "..." if len(content) > 500 else content
        print(preview)
        print("-" * 50)
        return 0
    else:
        print(f"Não foi possível encontrar NR-{args.nr}")
        print("\nDicas:")
        print("1. Verifique o número da NR")
        print("2. Verifique sua conexão com a internet")
        print("3. O site pode estar temporariamente indisponível")
        return 1


if __name__ == "__main__":
    sys.exit(main())
