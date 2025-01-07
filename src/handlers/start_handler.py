from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import LoggingUtil

logger = LoggingUtil.setup_logger()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_path = f"context_{update.message.from_user.username}.txt"
    open(file_path, "w").close()

    try:
        with open("./src/data/start.md", "r") as f:
            start_message = f.read()
    except FileNotFoundError:
        start_message = "¡Bienvenido al bot! (Archivo start.md no encontrado)"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=start_message)