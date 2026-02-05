"""Telegram Bot - Interface do Moltbot"""
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sys
sys.path.insert(0, '/home/brunoadsba/clawd/moltbot-setup')
from workspace.core import create_agent
from workspace.storage.sqlite_store import SQLiteStore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

agent = create_agent()
store = SQLiteStore()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Moltbot ativo!\n\n"
        "Sou seu assistente pessoal com acesso a:\n"
        "• Busca na web\n"
        "• Memória persistente\n"
        "• Execução de código\n"
        "• Operações de arquivo\n"
        "• Git\n\n"
        "Como posso ajudar?"
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    store.clear_history()
    await update.message.reply_text("✅ Histórico limpo!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tools = agent.tools.list_tools()
    await update.message.reply_text(
        f"🟢 Sistema operacional\n\n"
        f"Ferramentas disponíveis: {len(tools)}\n"
        f"• {', '.join(tools)}"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Mensagem recebida: {user_message}")
    
    await update.message.chat.send_action("typing")
    
    try:
        history = store.get_history(limit=10)
        response = await agent.run(user_message, history)
        
        store.add_message("user", user_message)
        store.add_message("assistant", response)
        store.log_metric("message_processed", {"length": len(user_message)})
        
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Erro: {str(e)}")

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN não configurado!")
    
    logger.info("Iniciando Moltbot...")
    
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot rodando!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
