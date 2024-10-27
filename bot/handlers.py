from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.logger import LoggingUtil
import os

logger = LoggingUtil.setup_logger()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    file_path = f"context_{ update.message.from_user.username}.txt"
    open(file_path, "w").close()
    start_message = open("./data/start.md").read()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=start_message)

async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from bot.finance_manager import FinanceManager
    try:
            answer = FinanceManager.get(update.message.text)
    except Exception:
        logger.error("Error generating answer")
        answer = {"text": "I'm sorry I couldn't generate an answer for you. Would you like to ask me something else?"}
    await context.bot.send_message(chat_id=update.effective_chat.id, text = answer["text"])
