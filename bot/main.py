from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler
from bot.handlers import start, talk
import os

def main():
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    talk_handler = MessageHandler(filters=None, callback=talk)
    application.add_handler(talk_handler)
    
    application.run_polling()


    