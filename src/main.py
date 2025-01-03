from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import os
from dotenv import load_dotenv

load_dotenv()

#from handlers.start_handler import start
from handlers.talk_handler import talk
from handlers.start_handler import start

def main():
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Handler to start the bot
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    # Handler to talk with the bot
    talk_handler = MessageHandler(filters.ALL & ~filters.COMMAND, talk)
    application.add_handler(talk_handler)

    application.run_polling()

if __name__ == "__main__":
    main()
