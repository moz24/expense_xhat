#!/usr/bin/env python3
import os
import sys
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.config import BOT_TOKEN
from bot.database.db import init_db
from bot.handlers.command_handler import start, today, week, month, total
from bot.handlers.text_handler import handle_text
from bot.handlers.voice_handler import handle_voice

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("PORT", "8080"))


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format, *args):
        pass


def run_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    logger.info("Health check server listening on port %d", PORT)
    server.serve_forever()


def main():
    print(f"DEBUG: BOT_TOKEN length={len(BOT_TOKEN)}, starts={BOT_TOKEN[:10] if BOT_TOKEN else 'EMPTY'}", flush=True)
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set in Railway Variables!")
        logger.error("Go to Variables tab and add: TELEGRAM_BOT_TOKEN = your_token")
        while True:
            import time
            time.sleep(60)

    try:
        init_db()
        logger.info("Database initialized.")
    except Exception as e:
        logger.error("Database init failed: %s", e)
        raise

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
    t = threading.Thread(target=run_health_server, daemon=True)
    t.start()
    main()
