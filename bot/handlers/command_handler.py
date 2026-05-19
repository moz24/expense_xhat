from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import db
from ..config import CURRENCY


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 *Expense Tracker Bot*\n\n"
        "Just send me your expenses in English or Urdu, and I'll record them!\n\n"
        "📝 *Examples:*\n"
        "• `lunch 500`\n"
        "• `200 کا ناشتہ`\n"
        "• `spent 1500 on petrol`\n"
        "• `دوا 300 کی`\n\n"
        "🎤 You can also send voice messages!\n\n"
        "*/today* — See today's expenses\n"
        "*/week* — This week's summary\n"
        "*/month* — This month's summary\n"
        "*/total* — All-time total",
        parse_mode="Markdown",
    )


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    expenses = db.get_today_expenses(user_id)
    total = db.get_today_total(user_id)

    if not expenses:
        await update.message.reply_text("📭 No expenses recorded today.")
        return

    lines = [f"📋 *Today's Expenses* — Total: *{CURRENCY} {total:,.0f}*\n"]
    for e in expenses:
        lines.append(
            f"• {e['category']}: *{CURRENCY} {e['amount']:,.0f}*"
            f"{' — ' + e['description'] if e['description'] else ''}"
        )

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    summary = db.get_weekly_summary(user_id)

    if not summary:
        await update.message.reply_text("📭 No expenses this week.")
        return

    total = sum(s["total"] for s in summary)
    lines = [f"📊 *This Week* — Total: *{CURRENCY} {total:,.0f}*\n"]
    for s in summary:
        lines.append(f"• {s['category']}: *{CURRENCY} {s['total']:,.0f}* ({s['count']}x)")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    summary = db.get_monthly_summary(user_id)

    if not summary:
        await update.message.reply_text("📭 No expenses this month.")
        return

    total = sum(s["total"] for s in summary)
    lines = [f"📊 *This Month* — Total: *{CURRENCY} {total:,.0f}*\n"]
    for s in summary:
        lines.append(f"• {s['category']}: *{CURRENCY} {s['total']:,.0f}* ({s['count']}x)")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    total_amount, count = db.get_all_time_total(user_id)

    if count == 0:
        await update.message.reply_text("📭 No expenses recorded yet.")
        return

    await update.message.reply_text(
        f"📈 *All-Time Summary*\n\n"
        f"Total expenses: *{CURRENCY} {total_amount:,.0f}*\n"
        f"Total entries: *{count}*",
        parse_mode="Markdown",
    )
