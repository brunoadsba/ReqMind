#!/usr/bin/env python3
"""
Web Search Tool - Busca web com Playwright
"""

from playwright.sync_api import sync_playwright
import json
import sys
import os

BROWSERLESS_ENDPOINT = os.getenv("BROWSERLESS_ENDPOINT", "ws://moltbot-browser:3000")

def search_web(query, num_results=5):
    """Realiza busca no Google e extrai resultados"""
    results = []
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(BROWSERLESS_ENDPOINT)
            page = browser.new_page()
            
            # Busca no Google
            search_url = f"https://www.google.com/search?q={query}"
            page.goto(search_url, wait_until="networkidle")
            
            # Extrai resultados
            search_results = page.locator('div.g').all()[:num_results]
            
            for result in search_results:
                try:
                    title = result.locator('h3').inner_text()
                    link = result.locator('a').first.get_attribute('href')
                    snippet = result.locator('div.VwiC3b').inner_text() if result.locator('div.VwiC3b').count() > 0 else ""
                    
                    results.append({
                        "title": title,
                        "url": link,
                        "snippet": snippet
                    })
                except:
                    continue
            
            browser.close()
            
        except Exception as e:
            return {"error": str(e)}
    
    return {"query": query, "results": results}

def fetch_page(url):
    """Extrai conteúdo de uma página"""
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(BROWSERLESS_ENDPOINT)
            page = browser.new_page()
            
            page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Extrai texto principal
            content = page.evaluate('''() => {
                const article = document.querySelector('article') || document.querySelector('main') || document.body;
                return article.innerText;
            }''')
            
            title = page.title()
            
            browser.close()
            
            return {
                "url": url,
                "title": title,
                "content": content[:5000]  # Limita tamanho
            }
            
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python web_search.py <search|fetch> <query|url>")
        sys.exit(1)
    
    command = sys.argv[1]
    arg = sys.argv[2]
    
    if command == "search":
        result = search_web(arg)
    elif command == "fetch":
        result = fetch_page(arg)
    else:
        result = {"error": "Comando inválido"}
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
