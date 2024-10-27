from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.logger import LoggingUtil
from bot.config import UserConfigDB
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

async def api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.username
    db = UserConfigDB()
    config = db.get_user_config(user_name)
    if config:
        await db.update_user_config(name=user_name, openai_apikey=update.message.text, array_debts=["default"])
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Update API Key.")
    else:
        await db.add_user_config(name=user_name, openai_apikey=update.message.text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Added API Key.")
    db.close()

async def pockets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.username
    db = UserConfigDB()
    config = db.get_user_config(user_name)
    if config:
        await db.update_user_config(name=user_name, openai_apikey=None, array_debts=update.message.text.split(","))
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Update Pockets.")
    else:
        await db.add_user_config(name=user_name, openai_apikey=None, array_debts=update.message.text.split(","))
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Added Pockets.")
    db.close()

async def get_pockets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.username
    db = UserConfigDB()
    config = db.get_user_config(user_name)
    if config:
        pockets = config[2]
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your pockets are {pockets}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You have no pockets.")
    db.close()