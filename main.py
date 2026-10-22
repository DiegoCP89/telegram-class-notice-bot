import os
import sys

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Lê o arquivo .env e carrega as variáveis no ambiente
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Fail fast: encerra se o token não estiver configurado
if not TOKEN:
    sys.exit(
        "Error: TELEGRAM_BOT_TOKEN not found. "
        "Copy .env.example to .env and add your bot token."
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responde ao comando /start."""
    await update.message.reply_text("Olá, Fatecano! Em que posso ajudar?")


def main() -> None:
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


if __name__ == "__main__":
    main()