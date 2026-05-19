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


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id

    parsed = parse_expense(text)

    if parsed["amount"] is None:
        await update.message.reply_text(
            "❌ Couldn't find an amount.\n\n"
            "Try: `lunch 500` or `200 کا ناشتہ`",
            parse_mode="Markdown",
        )
        return

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

    await update.message.reply_text(
        f"✅ *Recorded!*\n"
        f"{emoji} {parsed['category']}: *{CURRENCY} {parsed['amount']:,.0f}*\n"
        f"📝 {parsed['description']}\n\n"
        f"📋 Today's total: *{CURRENCY} {today_total:,.0f}*",
        parse_mode="Markdown",
    )
