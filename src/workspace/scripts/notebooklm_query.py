#!/usr/bin/env python3
"""
NotebookLM Query Script - Enhanced Version
Integração avançada com NotebookLM via Browser Automation
"""

import sys
import os
import json
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

NOTEBOOK_URL = os.getenv("NOTEBOOKLM_URL", "https://notebooklm.google.com")
BROWSERLESS_ENDPOINT = os.getenv("BROWSERLESS_ENDPOINT", "ws://moltbot-browser:3000")

class NotebookLMClient:
    def __init__(self):
        self.browser = None
        self.page = None
        
    def connect(self):
        """Conecta ao navegador via CDP"""
        p = sync_playwright().start()
        try:
            self.browser = p.chromium.connect_over_cdp(BROWSERLESS_ENDPOINT)
            self.page = self.browser.new_page()
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}", file=sys.stderr)
            return False
    
    def navigate_to_notebook(self):
        """Navega para o notebook"""
        try:
            self.page.goto(NOTEBOOK_URL, wait_until="networkidle", timeout=30000)
            time.sleep(2)
            return True
        except PlaywrightTimeout:
            print("Timeout ao carregar NotebookLM", file=sys.stderr)
            return False
    
    def check_login(self):
        """Verifica se está logado"""
        try:
            # Procura por elementos que indicam login
            login_indicators = [
                'button[aria-label*="Google"]',
                'a[href*="accounts.google.com"]',
                'div[role="button"]:has-text("Sign in")'
            ]
            
            for selector in login_indicators:
                if self.page.locator(selector).count() > 0:
                    return False
            return True
        except:
            return False
    
    def wait_for_chat_ready(self):
        """Aguarda o chat estar pronto"""
        try:
            # Seletores comuns para interface de chat
            chat_selectors = [
                'textarea[placeholder*="Ask"]',
                'textarea[aria-label*="chat"]',
                'input[type="text"][placeholder*="question"]',
                'div[contenteditable="true"]'
            ]
            
            for selector in chat_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=10000)
                    return selector
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"Erro ao aguardar chat: {e}", file=sys.stderr)
            return None
    
    def send_query(self, query: str, input_selector: str):
        """Envia a query para o chat"""
        try:
            # Preenche o campo de input
            self.page.fill(input_selector, query)
            time.sleep(0.5)
            
            # Tenta enviar (Enter ou botão)
            self.page.keyboard.press("Enter")
            time.sleep(1)
            
            # Alternativa: procurar botão de envio
            send_buttons = [
                'button[aria-label*="Send"]',
                'button[type="submit"]',
                'button:has-text("Send")'
            ]
            
            for btn in send_buttons:
                if self.page.locator(btn).count() > 0:
                    self.page.click(btn)
                    break
            
            return True
        except Exception as e:
            print(f"Erro ao enviar query: {e}", file=sys.stderr)
            return False
    
    def wait_for_response(self, timeout=60000):
        """Aguarda a resposta do AI"""
        try:
            # Aguarda indicadores de resposta
            response_indicators = [
                'div[role="article"]',
                'div.response',
                'div.message',
                'p:has-text("Based on")'
            ]
            
            start_time = time.time()
            while (time.time() - start_time) * 1000 < timeout:
                for selector in response_indicators:
                    elements = self.page.locator(selector).all()
                    if len(elements) > 0:
                        # Pega o último elemento (resposta mais recente)
                        return elements[-1].inner_text()
                
                time.sleep(1)
            
            return None
        except Exception as e:
            print(f"Erro ao aguardar resposta: {e}", file=sys.stderr)
            return None
    
    def extract_response(self):
        """Extrai a resposta mais recente"""
        try:
            # Múltiplas estratégias de extração
            strategies = [
                lambda: self.page.locator('div[role="article"]').last.inner_text(),
                lambda: self.page.locator('div.ai-response').last.inner_text(),
                lambda: self.page.locator('div.message').last.inner_text(),
                lambda: self.page.evaluate('document.querySelector("main").innerText')
            ]
            
            for strategy in strategies:
                try:
                    text = strategy()
                    if text and len(text) > 10:
                        return text
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"Erro ao extrair resposta: {e}", file=sys.stderr)
            return None
    
    def query(self, question: str):
        """Executa query completa"""
        result = {
            "success": False,
            "query": question,
            "response": None,
            "error": None
        }
        
        try:
            if not self.connect():
                result["error"] = "Falha ao conectar ao navegador"
                return result
            
            if not self.navigate_to_notebook():
                result["error"] = "Falha ao navegar para NotebookLM"
                return result
            
            if not self.check_login():
                result["error"] = "Usuário não está logado. Faça login manualmente."
                return result
            
            input_selector = self.wait_for_chat_ready()
            if not input_selector:
                result["error"] = "Interface de chat não encontrada"
                return result
            
            if not self.send_query(question, input_selector):
                result["error"] = "Falha ao enviar query"
                return result
            
            response = self.wait_for_response()
            if not response:
                response = self.extract_response()
            
            if response:
                result["success"] = True
                result["response"] = response
            else:
                result["error"] = "Nenhuma resposta obtida"
            
            return result
            
        except Exception as e:
            result["error"] = str(e)
            return result
        finally:
            if self.browser:
                self.browser.close()

def main():
    if len(sys.argv) < 2:
        print("Uso: python notebooklm_query.py <sua pergunta>")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    
    client = NotebookLMClient()
    result = client.query(query)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result["success"]:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
