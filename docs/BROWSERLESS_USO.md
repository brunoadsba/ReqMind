# Uso prático do Browserless (porta 3002)

## 1. Subir o Browserless

Com Docker (uma vez por sessão):

```bash
docker run -d -p 3002:3000 --name browserless ghcr.io/browserless/chromium
```

Verificar: abra no navegador `http://localhost:3002` — deve aparecer a interface do Browserless.

## 2. Variável de ambiente

No `.env` já está:

```
BROWSERLESS_ENDPOINT=ws://localhost:3002
```

Para rodar scripts no terminal do Cursor, exporte (ou use um `.env` carregado):

```bash
export BROWSERLESS_ENDPOINT=ws://localhost:3002
```

## 3. Dependência Playwright

No ambiente virtual do projeto:

```bash
source venv/bin/activate
pip install playwright
playwright install chromium
```

## 4. Usar os scripts existentes

**Busca no Google** (retorna JSON com título, URL e snippet):

```bash
cd /home/brunoadsba/assistente
source venv/bin/activate
export PYTHONPATH=src
python src/workspace/scripts/web_search.py search "sua busca aqui"
```

**Extrair conteúdo de uma página:**

```bash
python src/workspace/scripts/web_search.py fetch "https://exemplo.com/artigo"
```

## 5. Script mínimo para testar no Cursor

Use o script `scripts/browserless_exemplo.py` (ver abaixo) para abrir uma URL, esperar o carregamento e extrair título e um trecho de texto. Útil para validar que a conexão com o Browserless está ok.

## 6. Integração no código

Para usar o browser em outro módulo Python:

```python
import os
from playwright.sync_api import sync_playwright

BROWSERLESS = os.getenv("BROWSERLESS_ENDPOINT", "ws://localhost:3002")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(BROWSERLESS)
    page = browser.new_page()
    page.goto("https://exemplo.com")
    print(page.title())
    browser.close()
```

## Troubleshooting

| Problema | Solução |
|----------|---------|
| `Connection refused` na 3002 | Subir o container: `docker run -d -p 3002:3000 --name browserless ghcr.io/browserless/chromium` |
| Google bloqueia / reCAPTCHA | Use `fetch` em outros sites ou busque por API (e.g. SerpAPI) para produção |
| Playwright não acha Chromium | Rodar `playwright install chromium` |
