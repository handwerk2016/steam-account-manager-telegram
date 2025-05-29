import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from config import ALLOWED_USERS

def restricted(func):
    """Decorator to check user access"""
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ALLOWED_USERS:
            logging.warning(f"Unauthorized access attempt from user {user_id}")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped 