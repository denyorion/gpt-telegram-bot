"""Bot entry point: run with python main.py."""
import logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot.config import BOT_TOKEN
from bot.handlers.commands import cmd_start, cmd_help, cmd_reset
from bot.handlers.text import handle_text
from bot.handlers.images import handle_photo
from bot.handlers.voice import handle_voice

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set in .env")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    logger.info("Bot starting...")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
