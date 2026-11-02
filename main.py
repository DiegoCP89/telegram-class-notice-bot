import os
import sys

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


def get_token() -> str:
    """Load the bot token from the environment, exiting if it is missing."""
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        sys.exit(
            "Error: TELEGRAM_BOT_TOKEN not found. "
            "Copy .env.example to .env and add your bot token."
        )
    return token


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply to the /start command with a welcome message."""
    if update.message is None:
        return
    await update.message.reply_text("Olá, Fatecano! Em que posso ajudar?")


def main() -> None:
    """Build the bot application and start polling for updates."""
    token = get_token()
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


if __name__ == "__main__":
    main()
