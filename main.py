#!/usr/bin/env python3
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.config import BOT_TOKEN
from bot.database.db import init_db
from bot.handlers.command_handler import start, today, week, month, total
from bot.handlers.text_handler import handle_text
from bot.handlers.voice_handler import handle_voice

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set! Copy .env.example to .env and add your token.")
        return

    init_db()
    logger.info("Database initialized.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("week", week))
    app.add_handler(CommandHandler("month", month))
    app.add_handler(CommandHandler("total", total))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    logger.info("Bot started. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
