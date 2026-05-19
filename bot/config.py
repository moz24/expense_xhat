import os
import sys

# Debug: print all env vars starting with TELEGRAM
for k, v in sorted(os.environ.items()):
    if "TELEGRAM" in k.upper() or "BOT" in k.upper():
        print(f"DEBUG_ENV: {k}={v[:20] if v else '(empty)'}", flush=True)

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CURRENCY = os.environ.get("CURRENCY", "PKR")
WHISPER_MODEL_SIZE = os.environ.get("WHISPER_MODEL_SIZE", "base")
PREFERRED_LANGUAGE = os.environ.get("PREFERRED_LANGUAGE", "auto")
DATABASE_URL = os.environ.get("DATABASE_URL", "")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
SQLITE_PATH = os.path.join(DATA_DIR, "expenses.db")
