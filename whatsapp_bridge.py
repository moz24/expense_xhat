"""
WhatsApp Bridge — optional WhatsApp integration using whatsapp-web.js via Node.

This provides a Flask-based HTTP server that bridges WhatsApp messages
to the same expense parsing engine.

Usage:
  1. Install Node dependencies:
     npm install whatsapp-web.js qrcode-terminal express

  2. Run this script alongside the Telegram bot:
     python whatsapp_bridge.py

  3. Scan the QR code with WhatsApp to link your account.
"""

import os
import json
import subprocess
import sys
from bot.database.db import init_db, add_expense
from bot.parser.expense_parser import parse_expense

NODE_SCRIPT = """
const { Client, LocalAuth } = require('whatsapp-web.js');
const express = require('express');
const app = express();
app.use(express.json());

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: { headless: true, args: ['--no-sandbox'] }
});

client.on('qr', (qr) => {
    console.log('QR_CODE:' + qr);
});

client.on('ready', () => {
    console.log('WHATSAPP_READY');
});

client.on('message', async (msg) => {
    if (msg.from.endsWith('@c.us') && !msg.from.includes('g.us')) {
        const body = msg.body.trim();
        if (body) {
            console.log('EXPENSE:' + JSON.stringify({ from: msg.from, body }));
        }
    }
});

const PORT = process.env.WHATSAPP_PORT || 3099;
app.post('/send', (req, res) => {
    const { to, message } = req.body;
    client.sendMessage(to, message);
    res.json({ ok: true });
});

app.listen(PORT, () => {
    console.log('BRIDGE_READY on port ' + PORT);
});

client.initialize();
"""


def run_whatsapp_bridge():
    script_path = os.path.join(os.path.dirname(__file__), "_wa_bridge.js")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(NODE_SCRIPT)

    proc = subprocess.Popen(
        ["node", script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    import http.client

    WA_PORT = int(os.environ.get("WHATSAPP_PORT", "3099"))

    for line in proc.stdout:
        line = line.strip()
        if line.startswith("QR_CODE:"):
            qr = line.replace("QR_CODE:", "")
            print("\n📱 SCAN THIS QR CODE WITH WHATSAPP:\n")
            print(qr)
            print()
        elif line == "WHATSAPP_READY":
            print("✅ WhatsApp connected!")
        elif line.startswith("EXPENSE:"):
            try:
                data = json.loads(line.replace("EXPENSE:", ""))
                text = data["body"]
                phone = data["from"]
                parsed = parse_expense(text)
                if parsed["amount"] is not None:
                    user_id = int(hash(phone) % (2**31))
                    expense_id = add_expense(
                        user_id=user_id,
                        amount=parsed["amount"],
                        category=parsed["category"],
                        description=parsed["description"],
                        lang=parsed["language"],
                    )
                    reply = (
                        f"✅ Recorded: {parsed['category']} "
                        f"Rs. {parsed['amount']:,}"
                    )
                    conn = http.client.HTTPConnection("localhost", WA_PORT)
                    conn.request("POST", "/send",
                        json.dumps({"to": phone, "message": reply}),
                        {"Content-Type": "application/json"})
                    conn.getresponse()
            except Exception:
                pass

    proc.wait()


if __name__ == "__main__":
    init_db()
    run_whatsapp_bridge()
