from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import LoggingUtil

# Models 
from models.pocket import Pocket

from services.database.user_service import get_user_by_telegram_username
from services.database.pocket_service import create_pocket_service, get_pockets_by_user

logger = LoggingUtil.setup_logger()

async def create_pocket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_telegram_username = update.message.from_user.username

    # Verificar si el usuario existe en la base de datos
    user = get_user_by_telegram_username(user_telegram_username)
    if not user:
        await update.message.reply_text(
            "No estás autorizado. Contacta al administrador."
        )
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "Uso: /addpocket <nombre_pocket> <balance_inicial_opcional>"
        )
        return

    pocket_name = args[0]
    if pocket_name in [i.name for i in get_pockets_by_user(user['id'])]:
        await update.message.reply_text(
            f"Ya tienes un pocket con el nombre '{pocket_name}'."
        )
        return
    initial_balance = 0.00
    if len(args) > 1:
        try:
            initial_balance = float(args[1])
        except ValueError:
            await update.message.reply_text(
                "El balance inicial debe ser un número. Se usará 0.00 por defecto."
            )

    # Crear la pocket en BD
    try:
        created_pocket = create_pocket_service(
            Pocket(
                user_id=user['id'],  
                name=pocket_name,
                balance=initial_balance
            )
        )
        if created_pocket:
            await update.message.reply_text(
                f"Pocket '{pocket_name}' : {initial_balance}."
            )
        else:
            await update.message.reply_text(
                f"Error al crear el pocket '{pocket_name}'."
            )
    except Exception as e:
        logger.error(f"Error creando pocket: {e}")
        await update.message.reply_text(
            "Hubo un error al crear el pocket. Intenta de nuevo."
        )
