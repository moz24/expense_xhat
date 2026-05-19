import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except ImportError:
    pass

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CURRENCY = os.environ.get("CURRENCY", "PKR")
WHISPER_MODEL_SIZE = os.environ.get("WHISPER_MODEL_SIZE", "base")
PREFERRED_LANGUAGE = os.environ.get("PREFERRED_LANGUAGE", "auto")
DATABASE_URL = os.environ.get("DATABASE_URL", "")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
SQLITE_PATH = os.path.join(DATA_DIR, "expenses.db")
