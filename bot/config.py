import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CURRENCY = os.getenv("CURRENCY", "PKR")
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
PREFERRED_LANGUAGE = os.getenv("PREFERRED_LANGUAGE", "auto")

# PostgreSQL connection string
# Railway auto-injects DATABASE_URL when you add the PostgreSQL plugin
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Fallback to SQLite if no DATABASE_URL (local dev fallback)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
SQLITE_PATH = os.path.join(DATA_DIR, "expenses.db")
