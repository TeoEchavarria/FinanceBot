from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

#from handlers.start_handler import start
from handlers.talk_handler import talk
# ... otros imports ...

def main():
    application = ApplicationBuilder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

    # Handler para /start
    # start_handler = CommandHandler("start", start)
    # application.add_handler(start_handler)

    # Handler para texto o voz (sin comando), cualquier mensaje que llegue
    talk_handler = MessageHandler(filters.ALL & ~filters.COMMAND, talk)
    application.add_handler(talk_handler)

    application.run_polling()

if __name__ == "__main__":
    main()
