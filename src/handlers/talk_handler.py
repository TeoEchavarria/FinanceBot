# src/handlers/talk_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.logger import LoggingUtil
from services.voice_to_text import transcribe_voice
from models.finance_manager import FinanceManager
from services.database_connection import get_supabase_client
from services.database.user_service import get_user_by_telegram_username
from services.database.pocket_service import get_pockets_by_user

logger = LoggingUtil.setup_logger()

async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.username

    # 1. Determinar si el usuario envió texto o nota de voz
    if update.message.voice:
        # Es nota de voz
        try:
            user_message_text = await transcribe_voice(update, context)
        except Exception as e:
            logger.error("Error transcribiendo la nota de voz: %s", e)
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="Lo siento, no pude transcribir tu nota de voz. Por favor, intenta de nuevo."
            )
            return
    else:
        # Es mensaje de texto
        user_message_text = update.message.text

    try:
        # 2. Obtener las pockets del usuario
        client = get_supabase_client()
        user = get_user_by_telegram_username(client, user_name)
        pockets = get_pockets_by_user(client, user["id"])
        # 3. Construir la data para FinanceManager
        finance_data = [
            user_message_text,
            [p.name for p in pockets]
        ]

        print(finance_data)
        # 4. Procesar con FinanceManager
        answer = FinanceManager.get(*finance_data)  # Devuelve un dict con Payment

        # 5. Formatear la respuesta
        answer_text = (
            f"Pocket Name: {answer['pocket_name']}\n"
            f"Description: {answer['description']}\n"
            f"Amount: {answer['amount']}\n"
            f"Type: {answer['transaction_type']}"
        )

        # 6. Guardar en context.user_data (por si requieres uso futuro en callback buttons)
        context.user_data['last_message'] = answer
        context.user_data['last_user_message'] = finance_data
        context.user_data['user_name'] = user_name

        # 7. Crear un teclado inline de confirmación
        keyboard = [
            [
                InlineKeyboardButton("Correct", callback_data="Correct"),
                InlineKeyboardButton("Incorrect", callback_data="Incorrect")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # 8. Enviar respuesta
        await update.message.reply_text(text=answer_text, reply_markup=reply_markup)

    except Exception as e:
        logger.error("Error generating answer for user (%s): %s", user_name, e)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="I'm sorry I couldn't generate an answer for you. Would you like to ask me something else?"
        )