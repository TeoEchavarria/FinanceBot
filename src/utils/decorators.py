from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from services.database.user_service import get_user_by_telegram_username

def requires_auth(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        # Obtiene el username de Telegram
        telegram_username = update.message.from_user.username

        # Verifica si el usuario existe en la base de datos
        user = get_user_by_telegram_username(telegram_username)
        if not user:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="No estás autorizado para usar este bot. Contacta al administrador."
            )
            return  # Detiene la ejecución del handler

        # Si el usuario existe, procedemos a ejecutar la función original
        return await func(update, context, *args, **kwargs)

    return wrapper
