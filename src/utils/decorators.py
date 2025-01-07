from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from models.user import User
from services.database.user_service import get_user_by_telegram_username, create_user
from datetime import datetime as time 

def requires_auth(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        # Obtiene el username de Telegram
        telegram_username = update.message.from_user.username

        # Verifica si el usuario existe en la base de datos
        try:
            user = get_user_by_telegram_username(telegram_username)
        except:
            user = create_user(User(
                username=telegram_username,
            ))
        user_created_dt = time.fromisoformat(user["created_at"]).replace(tzinfo=None)
        now_naive = time.now().replace(tzinfo=None)
        if (now_naive - user_created_dt).days > 30:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, your trial period has expired. Please contact the administrator."
            )
            return
        # Si el usuario existe, procedemos a ejecutar la función original
        return await func(update, context, *args, **kwargs)

    return wrapper
