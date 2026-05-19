# Run & Test Commands

```bash
# Run the Telegram bot
cd C:\Users\Dell\expense-bot
python main.py

# Test the expense parser
python -c "from bot.parser.expense_parser import parse_expense; r=parse_expense('lunch 500'); print(r)"

# Test database
python -c "from bot.database.db import *; init_db(); print('ok')"

# Install whisper (optional, for voice):
pip install openai-whisper
```
