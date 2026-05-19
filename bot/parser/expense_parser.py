import re

URDU_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

CATEGORY_KEYWORDS = {
    "en": [
        (r"\b(food|dining|lunch|dinner|breakfast|khana|tiffin|pizza|burger|nashta|anda|chai|roti|naan)\b", "Food"),
        (r"\b(petrol|diesel|fuel|cab|uber|taxi|rickshaw|bus|metro|train|parking|toll|auto)\b", "Transport"),
        (r"\b(grocer(?:ies|y)?|vegetables|sabzi|fruit|milk|bread|eggs|meat|chicken|daal|rice|oil|masala)\b", "Groceries"),
        (r"\b(shopping|clothes|shirt|shoes|dress|watch|bag|mobile|phone)\b", "Shopping"),
        (r"\b(electric(?:ity)?|bill|gas|water|internet|wifi|phone|rent|maintenance)\b", "Bills & Utilities"),
        (r"\b(doctor|medicine|hospital|clinic|pharmacy|dawai|checkup|lab|test)\b", "Healthcare"),
        (r"\b(movie|cinema|netflix|entertainment|game|outing|picnic)\b", "Entertainment"),
        (r"\b(gym|salon|barber|haircut|spa|parlour|makeup)\b", "Personal Care"),
        (r"\b(gift|present|donation|charity|zakat)\b", "Gifts & Charity"),
        (r"\b(education|school|college|university|tuition|fee|books|stationery)\b", "Education"),
    ],
    "ur": [
        (r"(کھانہ|کھانا|ناشتہ|لنچ|ڈنر|فوڈ|پیزا|برگر|بریانی|تِفن)", "Food"),
        (r"(پٹرول|ڈیزل|تیل|ٹیکسی|رکشہ|بس|میٹرو|ٹرین|پارکنگ|آٹو|فیول)", "Transport"),
        (r"(سبزی|پھل|دودھ|انڈے|گوشت|چکن|چاول|تیل|مصالحہ|گروسری)", "Groceries"),
        (r"(شاپنگ|کپڑے|جوتے|شرٹ|واچ|بیگ|موبائل|فون)", "Shopping"),
        (r"(بجلی|گیس|پانی|انٹرنیٹ|وائی فائی|فون|کرایہ|بل)", "Bills & Utilities"),
        (r"(ڈاکٹر|دوا|ہسپتال|کلینک|فارمیسی|معائنہ|ٹیسٹ|لیب)", "Healthcare"),
        (r"(فلم|مووی|تفریح|گیم|پکنک|سیر)", "Entertainment"),
        (r"(جیم|سیلون|حجامت|سپا|پارلر|میک اپ)", "Personal Care"),
        (r"(تعلیم|اسکول|کالج|یونیورسٹی|فیس|کتاب|اسٹیشنری)", "Education"),
        (r"(تحفہ|عطیہ|خیرات|زکوٰۃ)", "Gifts & Charity"),
    ],
}

STOP_WORDS = {
    "en": {"the", "a", "an", "on", "for", "in", "of", "to", "at", "with", "and", "is", "was",
           "spent", "paid", "gave", "expense", "amount", "rs", "pkr", "rupees", "ka", "ki", "ke"},
    "ur": {"کا", "کی", "کے", "نے", "کو", "سے", "میں", "پر", "اور", "ہے", "تھا", "تھی",
           "نے", "ہو", "گئے", "گئی", "کیا", "کرو", "دیے", "دیا"},
}


def _normalize_text(text: str) -> str:
    text = text.translate(URDU_DIGITS)
    text = re.sub(r"[،,;:\!\.\?]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _has_urdu(text: str) -> bool:
    return bool(re.search(r"[\u0600-\u06FF\u0750-\u077F]", text))


def _extract_amount(text: str) -> tuple:
    amounts = re.findall(r"(\d+(?:\.\d{1,2})?)", text)
    if not amounts:
        return None, text
    amounts = sorted([(float(a), len(a)) for a in amounts], key=lambda x: (-x[0], -x[1]))
    best = amounts[0][0]
    text = re.sub(r"\b" + re.escape(str(int(best))) + (r"(\.\d+)?" if "." in str(best) else "") + r"\b", "", text, count=1)
    if best == int(best):
        best = int(best)
    return best, text.strip()


def _detect_category(text: str, lang: str) -> str:
    for pattern, category in CATEGORY_KEYWORDS.get(lang, []):
        if re.search(pattern, text, re.IGNORECASE):
            return category
    return "Other"


def _clean_description(text: str, lang: str, amount_placeholder_removed: bool = True) -> str:
    stop_words = STOP_WORDS.get(lang, set())
    words = text.split()
    cleaned = [w for w in words if w.lower() not in stop_words and not re.match(r"^\d+$", w)]
    return " ".join(cleaned).strip() if cleaned else text.strip()


def parse_expense(text: str) -> dict:
    original = text.strip()
    lang = "ur" if _has_urdu(original) else "en"

    text = _normalize_text(original)
    amount, remaining = _extract_amount(text)

    if amount is None:
        return {"amount": None, "category": None, "description": original, "language": lang}

    category = _detect_category(remaining, lang)
    description = _clean_description(remaining, lang)

    if not description or description.isspace():
        description = category if category != "Other" else "Expense"

    return {
        "amount": amount,
        "category": category,
        "description": description[:100],
        "language": lang,
    }
