import os
import tempfile
from telegram import Update
from telegram.ext import ContextTypes
from ..parser.expense_parser import parse_expense
from ..database import db
from ..config import CURRENCY


CATEGORY_EMOJIS = {
    "Food": "🍽️",
    "Transport": "🚗",
    "Groceries": "🛒",
    "Shopping": "🛍️",
    "Bills & Utilities": "📄",
    "Healthcare": "💊",
    "Entertainment": "🎬",
    "Personal Care": "💇",
    "Gifts & Charity": "🎁",
    "Education": "📚",
    "Other": "📝",
}


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    voice = update.message.voice

    status_msg = await update.message.reply_text("🎤 Processing your voice message...")

    try:
        import whisper
    except ImportError:
        await status_msg.edit_text(
            "❌ Whisper is not installed. Voice transcription is unavailable.\n"
            "Please send text instead, or install with:\n"
            "`pip install openai-whisper`",
            parse_mode="Markdown",
        )
        return

    try:
        file = await voice.get_file()
        ogg_path = os.path.join(tempfile.gettempdir(), f"voice_{user_id}_{voice.file_id}.ogg")

        await file.download_to_drive(ogg_path)

        model = whisper.load_model("base")
        result = model.transcribe(ogg_path, language=None)

        os.remove(ogg_path)

        transcribed = result["text"].strip()
        detected_lang = result.get("language", "en")

        if not transcribed:
            await status_msg.edit_text("❌ Couldn't understand the audio. Please try again.")
            return

        await status_msg.edit_text(f"📝 *Transcribed:* _{transcribed}_\n\nProcessing...", parse_mode="Markdown")

        parsed = parse_expense(transcribed)

        if parsed["amount"] is None:
            await status_msg.edit_text(
                f"📝 Heard: _{transcribed}_\n\n"
                "❌ Couldn't find an amount. Try being more specific.",
                parse_mode="Markdown",
            )
            return

        parsed["language"] = detected_lang
        expense_id = db.add_expense(
            user_id=user_id,
            amount=parsed["amount"],
            category=parsed["category"],
            description=parsed["description"],
            currency=CURRENCY,
            lang=parsed["language"],
        )

        emoji = CATEGORY_EMOJIS.get(parsed["category"], "📝")
        today_total = db.get_today_total(user_id)

        await status_msg.edit_text(
            f"✅ *Recorded!*\n"
            f"{emoji} {parsed['category']}: *{CURRENCY} {parsed['amount']:,.0f}*\n"
            f"📝 {parsed['description']}\n\n"
            f"📋 Today's total: *{CURRENCY} {today_total:,.0f}*",
            parse_mode="Markdown",
        )

    except Exception as e:
        await status_msg.edit_text(f"❌ Error processing voice: {str(e)}")
