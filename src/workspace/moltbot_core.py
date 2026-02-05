#!/usr/bin/env python3
"""
Moltbot Core - Implementação básica do bot Telegram
Este é um exemplo funcional que pode ser expandido
"""

import os
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# Configuração
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MoltbotCore:
    def __init__(self):
        self.conversation_history = {}
    
    def call_llm(self, user_id: int, message: str) -> str:
        """Chama o LLM (Groq)"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Adiciona mensagem do usuário
        self.conversation_history[user_id].append({
            "role": "user",
            "content": message
        })
        
        # Mantém apenas últimas 10 mensagens
        if len(self.conversation_history[user_id]) > 20:
            self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
        
        # System prompt
        system_prompt = {
            "role": "system",
            "content": """Você é Moltbot, um assistente pessoal avançado com capacidades de agente.

Você pode:
- Pesquisar na web
- Executar código e scripts
- Consultar o NotebookLM do usuário
- Acessar memória de longo prazo
- Automatizar tarefas no navegador

Seja proativo, inteligente e útil. Quando precisar usar ferramentas, explique o que vai fazer."""
        }
        
        messages = [system_prompt] + self.conversation_history[user_id]
        
        try:
            response = requests.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2048
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result["choices"][0]["message"]["content"]
                
                # Adiciona resposta ao histórico
                self.conversation_history[user_id].append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                return assistant_message
            else:
                logger.error(f"Erro na API Groq: {response.status_code} - {response.text}")
                return "Desculpe, tive um problema ao processar sua mensagem."
        
        except Exception as e:
            logger.error(f"Erro ao chamar LLM: {e}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem."

# Instância global
bot_core = MoltbotCore()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler do comando /start"""
    user = update.effective_user
    welcome_message = f"""Olá {user.first_name}! 👋

Sou o Moltbot, seu assistente pessoal avançado.

Posso ajudar você com:
🔍 Pesquisas na web
💻 Execução de código
📚 Consultas ao NotebookLM
🧠 Memória de longo prazo
🤖 Automação de tarefas

Como posso ajudar você hoje?"""
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler do comando /help"""
    help_text = """🤖 Comandos Disponíveis:

/start - Iniciar conversa
/help - Mostrar esta ajuda
/clear - Limpar histórico de conversa
/status - Ver status do sistema

Você também pode simplesmente conversar comigo naturalmente!

Exemplos:
• "Pesquise sobre Docker Compose"
• "Execute o script test.py"
• "Consulte meu NotebookLM sobre o projeto X"
• "Adicione à memória: meu aniversário é dia 15"
"""
    await update.message.reply_text(help_text)

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Limpa o histórico de conversa"""
    user_id = update.effective_user.id
    if user_id in bot_core.conversation_history:
        del bot_core.conversation_history[user_id]
    await update.message.reply_text("✅ Histórico de conversa limpo!")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra status do sistema"""
    status = "🟢 Sistema Operacional\n\n"
    
    # Testa serviços
    services = {
        "ChromaDB": "http://chroma-db:8000/api/v1/heartbeat",
        "Ollama": "http://ollama:11434/api/tags"
    }
    
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                status += f"✅ {service}: OK\n"
            else:
                status += f"⚠️ {service}: Erro {response.status_code}\n"
        except:
            status += f"❌ {service}: Offline\n"
    
    await update.message.reply_text(status)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler de mensagens normais"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    logger.info(f"Mensagem de {user_id}: {user_message}")
    
    # Mostra que está digitando
    await update.message.chat.send_action("typing")
    
    # Processa com LLM
    response = bot_core.call_llm(user_id, user_message)
    
    # Envia resposta
    await update.message.reply_text(response)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler de erros"""
    logger.error(f"Erro: {context.error}")
    if update and update.message:
        await update.message.reply_text("Desculpe, ocorreu um erro. Tente novamente.")

def main():
    """Inicia o bot"""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN não configurado!")
        return
    
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY não configurado!")
        return
    
    logger.info("Iniciando Moltbot...")
    
    # Cria aplicação
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Inicia
    logger.info("Moltbot iniciado! Aguardando mensagens...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
