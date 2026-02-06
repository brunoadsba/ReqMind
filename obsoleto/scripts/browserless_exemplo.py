#!/usr/bin/env python3
"""
Exemplo prático (LEGADO): conectar ao Browserless (localhost:3002) e extrair dados de uma página.
Movido para o diretório obsoleto para não poluir o foco do bot Telegram.

Uso:
    python scripts/browserless_exemplo.py [URL]
"""

import os
import sys

from playwright.sync_api import sync_playwright

BROWSERLESS = os.getenv("BROWSERLESS_ENDPOINT", "ws://localhost:3002")
URL = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"


def main():
    print(f"Conectando em {BROWSERLESS}...")
    print(f"Abrindo: {URL}\n")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(BROWSERLESS)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=15000)

        title = page.title()
        # Primeiro parágrafo ou body
        snippet = page.evaluate(
            """() => {
            const p = document.querySelector('p');
            return p ? p.innerText.slice(0, 300) : document.body.innerText.slice(0, 300);
        }"""
        )

        browser.close()

    print(f"Título: {title}")
    print(f"Trecho: {snippet}...")


if __name__ == "__main__":
    main()

