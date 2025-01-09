# src/handlers/talk_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext

# Models
from models.purchase import Purchase

# Utils
from utils.logger import LoggingUtil
from utils.decorators import requires_auth

# Services
from services.voice_to_text import transcribe_voice
from services.database.user_service import get_user_by_telegram_username, update_user
from services.database.pocket_service import (
    get_pockets_by_user, 
    get_pocket_by_user_and_name, 
    update_pocket_balance
)
from services.database.purchase_service import create_purchase
from services.finance_manager.register_service import register_purchase
from services.finance_manager.query_service import process_finance_query

logger = LoggingUtil.setup_logger()

async def payment_decision(update: Update, context: CallbackContext):
    """
    Handles each payment's Correct/Incorrect button.
    The callback_data looks like 'payment_correct_{index}' or 'payment_incorrect_{index}'.
    """
    query = update.callback_query
    await query.answer()

    user_name = context.user_data.get('user_name', None)
    user = get_user_by_telegram_username(user_name)
    
    # Retrieve the list of all pending payments
    payments = context.user_data.get('payments', [])

    # Callback data format: e.g. 'payment_correct_0' or 'payment_incorrect_1'
    data_parts = query.data.split('_')  # ['payment', 'correct'/'incorrect', 'index']
    
    if len(data_parts) != 3:
        logger.error(f"Unexpected callback_data format: {query.data}")
        await query.edit_message_text(text="Something went wrong with the payment decision.")
        return

    _, decision, idx_str = data_parts
    idx = int(idx_str)

    # Safety check: index in range
    if idx < 0 or idx >= len(payments):
        logger.error(f"Payment index out of range: {idx}")
        await query.edit_message_text(text="Something went wrong. Invalid payment index.")
        return
    
    payment = payments[idx]
     # Process the payment in the database
    pocket_name = payment['pocket_name']
    transaction_type = payment['transaction_type']
    amount = payment['amount']
    description = payment['description']
    if decision == "correct":
        pocket = get_pocket_by_user_and_name(user["id"], pocket_name)

        if transaction_type == "positive":
            adjusted_amount = amount
        elif transaction_type == "negative":
            adjusted_amount = -amount
        else:
            raise ValueError(f"Invalid transaction type: {transaction_type}")

        purchase = Purchase(
            user_id=pocket.user_id,
            pocket_id=pocket.id,
            description=description,
            amount=adjusted_amount,
            transaction_type=transaction_type
        )
        create_purchase(purchase)

        pocket.balance += adjusted_amount
        update_pocket_balance(pocket.id, pocket.balance)

        # Edit the message to indicate it was confirmed
        await query.edit_message_text(
            text=(
                f"**Payment #{idx+1} Confirmed**\n"
                f"Description: {pocket_name}-{description}\n"
                f"Amount: {amount}\n"
                "This payment has been **processed**."
            ),
            parse_mode="Markdown"
        )

    elif decision == "incorrect":
        # Simply edit the message to indicate the user rejected it
        await query.edit_message_text(
            text=(
                f"**Payment #{idx+1} Rejected**\n"
                f"Description: {pocket_name}-{description}\n"
                "This payment will **not** be processed."
            ),
            parse_mode="Markdown"
        )

@requires_auth
async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_name = update.message.from_user.username

        try:
            user = get_user_by_telegram_username(user_name)
            pockets = get_pockets_by_user(user["id"])
        except Exception as e:
            logger.error("Error fetching user and pockets: %s", e)
            raise e
        
        # 1. Check if the user sent a voice note or a text message
        if update.message.voice:
            # It's a voice note
            try:
                user_message_text, time = await transcribe_voice(update, context, user["audio_time"])
                if time == -1:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Sorry, you don't have enough time left to send voice messages."
                    )
                    return
            except Exception as e:
                logger.error("Error transcribing voice message: %s", e)
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Sorry, I was unable to transcribe your voice memo. Please try again."
                )
                return
            try: 
                user["audio_time"] -= time
                update_user(user)
            except Exception as e:
                logger.error("Error updating user audio time: %s", e)
                return
        else:
            user_message_text = update.message.text


        finance_data = [
            user_message_text,
            [p.name for p in pockets],
            user["membresia"]
        ]

        if user_message_text.split(" ")[0].lower().replace(",", "").replace(".", "") in ["consulta","consult"]:
            try:
                consult = process_finance_query(*finance_data, user["id"])
            except Exception as e:
                logger.error("Error processing finance query: %s", e)
                raise e
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text= consult
            )
            return
        else:
            try:
                payments = register_purchase(*finance_data)
            except Exception as e:
                logger.error("Error processing register purchase: %s", e)
                raise e

        try:
            if not payments:
                # If no payments were extracted, just respond accordingly
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="I couldn't find any payment details in your message."
                )
                return

            # 5. Store the entire list of payments in context.user_data for the callbacks
            context.user_data['payments'] = payments
            context.user_data['user_name'] = user_name

            # 6. For each payment, send a separate message with Confirm/Reject buttons
            for idx, payment in enumerate(payments):
                answer_text = (
                    f"**Payment #{idx+1}**\n"
                    f"Pocket Name: {payment['pocket_name']}\n"
                    f"Description: {payment['description']}\n"
                    f"Amount: {payment['amount']}\n"
                    f"Type: {payment['transaction_type']}"
                )

                # Inline keyboard for each payment
                keyboard = [
                    [
                        InlineKeyboardButton("Correct", callback_data=f"payment_correct_{idx}"),
                        InlineKeyboardButton("Incorrect", callback_data=f"payment_incorrect_{idx}")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=answer_text,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.error("Error sending payment decisions: %s", e)
            raise e
        
    except Exception as e:
        logger.error("Error generating answer for user (%s): %s", user_name, e)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="I'm sorry, I couldn't generate an answer for you. Would you like to ask me something else?"
        )
