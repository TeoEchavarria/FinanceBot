from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from telegram.ext import ContextTypes
from utils.logger import LoggingUtil
from bot.config import UserConfigDB, PocketDB
import json

logger = LoggingUtil.setup_logger()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    file_path = f"context_{ update.message.from_user.username}.txt"
    open(file_path, "w").close()
    start_message = open("./data/start.md").read()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=start_message)

async def confirmation(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "Correct":
        # Retrieve the last message from user_data
        user_name = context.user_data.get('user_name', None)
        last_message = context.user_data.get('last_message', 'No previous message available.')
        db_pocket = PocketDB()
        db_pocket.add_transaction(user_name, **last_message)
        
        message_response = f"Transaction added to pocket {last_message['pocket_name']}"
        await query.edit_message_text(text=message_response)
    # You can now use this last message in your response
    else:
        from bot.finance_manager import FinanceManager
        finace_data = context.user_data.get('last_user_message', None)
        last_message = FinanceManager.get(*finace_data)


async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from bot.finance_manager import FinanceManager
    db_pocket = PocketDB()
    db = UserConfigDB()
    user_name = update.message.from_user.username
    try:
        config = db.get_user_config(user_name)
        pockets = db_pocket.get_pockets(user_name)
        finace_data = [update.message.text, config["openai_apikey"], [i["name"] for i in pockets]]
        if not config:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please set your API_KEY using /apikey {your_api_key} command.")
        answer = FinanceManager.get(*finace_data)
        answer_text = "Pocket Name: {pocket_name}\nDescription: {description}\nAmount: {amount}\nType: {transaction_type}".format(**answer)
        context.user_data['last_message'] = answer
        context.user_data['last_user_message'] = finace_data
        context.user_data['user_name'] = user_name
    except Exception as e:
        logger.error("Error generating answer for user: %s", e)
        answer = {"text": "I'm sorry I couldn't generate an answer for you. Would you like to ask me something else?"}
    keyboard = [
        [InlineKeyboardButton("Correct", callback_data="Correct"),
         InlineKeyboardButton("Incorrect", callback_data="Incorrect")]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await update.message.reply_text(text=answer_text, reply_markup=reply_markup)
    except Exception as e:
        logger.error("Error sending message: %s", e)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm sorry I couldn't generate an answer for you. Would you like to ask me something else?")


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

async def get_pocket_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.username
    db = PocketDB()
    pocket = update.message.text.replace("/balance ","")
    if pocket == "" or pocket == "/balance":
        balance = db.get_pockets_balance(user_name)
        
    else:
        balance = db.get_pocket_balance(user_name, pocket)
        balance = {pocket: balance}
    try:
        header = "Key                  | Value"
        separator = "---------------------+-----------------"
        # Dynamically create rows for each item
        rows = "\n".join([f"{key:<21}| {value:,.2f}" for key, value in balance.items()])

        # Combine all parts into a table
        table = f"```\n{header}\n{separator}\n{rows}\n```"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=table, parse_mode='MarkdownV2')
    except Exception as e:
        logger.error("Error getting pocket balance: %s", e)
    finally:
        db.close()