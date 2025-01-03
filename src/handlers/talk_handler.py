# src/handlers/talk_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.ext import CallbackContext

from models.finance_manager import FinanceManager
from models.purchase import Purchase

from utils.logger import LoggingUtil

from services.voice_to_text import transcribe_voice
from services.database_connection import get_supabase_client
from services.database.user_service import get_user_by_telegram_username
from services.database.pocket_service import get_pockets_by_user, get_pocket_by_user_and_name
from services.database.purchase_service import create_purchase

logger = LoggingUtil.setup_logger()

async def confirmation(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "Correct":
        # Retrieve the last message from user_data
        user_name = context.user_data.get('user_name', None)
        last_message = context.user_data.get('last_message', 'No previous message available.')
        client = get_supabase_client()
        user = get_user_by_telegram_username(client, user_name)
        pocket = get_pocket_by_user_and_name(client, user["id"], last_message['pocket_name'])
        transaction_type = last_message.get('transaction_type')
        amount = last_message.get('amount', 0)

        if transaction_type == "positive":
            adjusted_amount = amount
        elif transaction_type == "negative":
            adjusted_amount = -amount
        else:
            raise ValueError(f"Invalid transaction type: {transaction_type}")

        punchase = Purchase(
            user_id=pocket.user_id, 
            pocket_id=pocket.id, 
            description=last_message['description'], 
            amount=adjusted_amount, 
            transaction_type=last_message['transaction_type']
        )
        create_purchase(client, punchase)

        message_response = f"Transaction added to pocket {last_message['pocket_name']}"
        await query.edit_message_text(text=message_response)
    # You can now use this last message in your response
    else:
        await query.edit_message_text(text="Please try again.")


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