from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from utils.logger import LoggingUtil
from services.database.user_service import get_user_by_telegram_username
from services.database.pocket_service import (
    get_pockets_by_user as get_pockets_by_user_service,
    get_pocket_by_user_and_name,
)
from services.database.purchase_service import get_last_transactions_by_pocket

logger = LoggingUtil.setup_logger()

async def get_pockets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_telegram_username = update.message.from_user.username

    # Verificar si el usuario existe
    user = get_user_by_telegram_username(user_telegram_username)
    if not user:
        await update.message.reply_text(
            "No estás autorizado. Contacta al administrador."
        )
        return

    args = context.args
    pocket_name = args[0] if args else None

    if not pocket_name:
        # 1) No se especificó pocket: mostrar todos los pockets
        pockets = get_pockets_by_user_service(user_id=user["id"])
        if not pockets:
            await update.message.reply_text("No tienes pockets.")
            return
    
        header = "Key                  | Value"
        separator = "---------------------+-----------------"
        # Dynamically create rows for each item
        rows = "\n".join([f"{p.name:<21}| {p.balance:,.2f}" for p in pockets])

        # Combine all parts into a table
        table = f"```\n{header}\n{separator}\n{rows}\n```"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=table, parse_mode='MarkdownV2')
    else:
        # 2) Se especificó un pocket: mostrar info + últimas 5 transacciones
        pocket = get_pocket_by_user_and_name(user_id=user["id"], pocket_name=pocket_name)
        if not pocket:
            await update.message.reply_text(
                f"No existe el pocket '{pocket_name}'."
            )
            return

        # Obtener últimas 5 transacciones
        transactions = get_last_transactions_by_pocket(pocket_id=pocket.id)

        message_lines = [f"<b>Pocket:</b> {pocket.name}",
                         f"<b>Balance:</b> {pocket.balance}\n"]

        message_lines.append("<b>Últimas 5 transacciones:</b>")
        if not transactions:
            message_lines.append("No hay transacciones registradas.")
        else:
            for t in transactions:
                line = f"- {t.description}: {t.amount}"
                message_lines.append(line)

        final_msg = "\n".join(message_lines)

        await update.message.reply_text(
            final_msg,
            parse_mode= ParseMode.HTML
        )
