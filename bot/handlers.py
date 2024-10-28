from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.logger import LoggingUtil
from bot.config import UserConfigDB, PocketDB
import os

logger = LoggingUtil.setup_logger()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    file_path = f"context_{ update.message.from_user.username}.txt"
    open(file_path, "w").close()
    start_message = open("./data/start.md").read()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=start_message)

async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from bot.finance_manager import FinanceManager
    db = UserConfigDB()
    user_name = update.message.from_user.username
    try:
        config = db.get_user_config(user_name)
        if not config:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please set your API_KEY using /apikey {your_api_key} command.")
        answer = FinanceManager.get(update.message.text, config["openai_apikey"])
        print(answer)
    except Exception as e:
        logger.error("Error generating answer for user: %s", e)
        answer = {"text": "I'm sorry I couldn't generate an answer for you. Would you like to ask me something else?"}
    await context.bot.send_message(chat_id=update.effective_chat.id, text = answer["text"])

async def api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.username
    db = UserConfigDB()
    config = db.get_user_config(user_name)
    if config:
        db.update_user_config(name=user_name, openai_apikey=update.message.text.replace("/apikey ",""))
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Update API Key.")
    else:
        db.add_user_config(name=user_name, openai_apikey=update.message.text.replace("/apikey ",""))
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Added API Key.")
    db.close()

async def get_pockets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.username
    db = PocketDB()
    config = db.get_pockets(user_name)
    logger.info(config)
    if config:
        debts = '\n- '.join([i["name"] for i in config])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your pockets are \n- {debts}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You have no pockets.")
    db.close()

async def add_pocket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.username
    db = PocketDB()
    pocket = update.message.text.replace("/apocket ","").split(" ")
    print(pocket)
    db.add_pocket(user_name, *pocket)
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Added pocket {pocket}")
    except Exception as e:
        logger.error("Error adding pocket: %s", e)
    finally:
        db.close()