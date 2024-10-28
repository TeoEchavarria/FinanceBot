from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler
from bot.handlers import start, talk, api_key, get_pockets, add_pocket
import os

def main():
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    api_key_handler = CommandHandler("apikey", callback=api_key)
    application.add_handler(api_key_handler)

    pockets_handler = CommandHandler("pockets", callback=get_pockets)
    application.add_handler(pockets_handler)

    get_pockets_handler = CommandHandler("apocket", callback=add_pocket)
    application.add_handler(get_pockets_handler)

    talk_handler = MessageHandler(filters=None, callback=talk)
    application.add_handler(talk_handler)
    
    application.run_polling()


    