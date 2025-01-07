from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import os
from dotenv import load_dotenv

load_dotenv()

#from handlers.start_handler import start
from handlers.talk_handler import talk, payment_decision
from handlers.start_handler import start

# Pocket Handlers
from handlers.create_pocket_handler import create_pocket
from handlers.get_pockets_handler import get_pockets

def main():
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Handler to start the bot
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    # Handler to create a pocket
    create_pocket_handler = CommandHandler("addpocket", create_pocket)
    application.add_handler(create_pocket_handler)

    # Handler to get pockets
    get_pockets_handler = CommandHandler("pockets", get_pockets)
    application.add_handler(get_pockets_handler)

    # Handler to talk with the bot
    talk_handler = MessageHandler(filters.ALL & ~filters.COMMAND, talk)
    application.add_handler(talk_handler)
    application.add_handler(CallbackQueryHandler(payment_decision))

    application.run_polling()

if __name__ == "__main__":
    main()
