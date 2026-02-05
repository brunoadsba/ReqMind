"""Módulo de autenticação e autorização"""
import os
import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# Fallback quando ALLOWED_USERS não está definido no .env
_DEFAULT_ALLOWED_USERS = [6974901522]
_DEFAULT_ADMIN_ID = 6974901522


def _get_allowed_users():
    users_env = os.getenv("ALLOWED_USERS", "")
    if users_env:
        try:
            ids = [int(uid.strip()) for uid in users_env.split(",") if uid.strip()]
            if ids:
                return ids
        except ValueError:
            pass
    return _DEFAULT_ALLOWED_USERS


def _get_admin_id():
    aid = os.getenv("ADMIN_ID", "")
    if aid:
        try:
            return int(aid.strip())
        except ValueError:
            pass
    return _DEFAULT_ADMIN_ID


ALLOWED_USERS = _get_allowed_users()
ADMIN_ID = _get_admin_id()


def require_auth(func):
    """Decorator que requer autenticação"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        user_id = user.id
        allowed = _get_allowed_users()

        if not allowed or user_id not in allowed:
            logger.warning(
                f"❌ Acesso negado: user_id={user_id}, "
                f"username={user.username}, name={user.full_name}"
            )
            await update.message.reply_text(
                "❌ Acesso negado. Este bot é privado.\n"
                f"Seu ID: {user_id}"
            )
            return
        
        logger.info(f"✅ Acesso autorizado: {user_id} ({user.username})")
        return await func(update, context)
    
    return wrapper

def is_admin(user_id: int) -> bool:
    """Verifica se usuário é admin"""
    return ADMIN_ID and user_id == ADMIN_ID
