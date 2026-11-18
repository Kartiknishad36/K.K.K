"""🤖 AI Dost | 💼 Business replies
.aidost on|off  .biz on|off  .bizadd key | reply
"""
import json
import random
from pathlib import Path
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from bot.client import app
import config

P = config.COMMAND_PREFIX
AI_ON = False
BIZ_ON = False
DATA = Path(getattr(config, "DATA_DIR", Path("data"))) / "biz_replies.json"
DATA.parent.mkdir(parents=True, exist_ok=True)
AI_LINES = ["Haan bolo 😊", "Acha, phir?", "Hmm interesting…", "Main yahin hu ✨"]

def _load_biz():
    if not DATA.exists():
        return {"price": "Rate: Basic 499 | Pro 999", "hi": "Hello! Kaise help karun?"}
    try:
        return json.loads(DATA.read_text())
    except Exception:
        return {}

def _save_biz(d):
    DATA.write_text(json.dumps(d, indent=2, ensure_ascii=False))

async def _out(m, t):
    try:
        return await m.reply_text(t)
    except Exception:
        try:
            return await m.edit_text(t)
        except Exception:
            return None

@app.on_message(filters.command(["aidost"], prefixes=P))
async def aidost_cmd(client, message: Message):
    global AI_ON
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    if arg in ("on", "1"):
        AI_ON = True
    elif arg in ("off", "0"):
        AI_ON = False
    else:
        AI_ON = not AI_ON
    await _out(message, f"🤖 AI Dost: {'ON' if AI_ON else 'OFF'}")

@app.on_message(filters.command(["biz"], prefixes=P))
async def biz_cmd(client, message: Message):
    global BIZ_ON
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    if arg in ("on", "1"):
        BIZ_ON = True
    elif arg in ("off", "0"):
        BIZ_ON = False
    else:
        BIZ_ON = not BIZ_ON
    await _out(message, f"💼 Business: {'ON' if BIZ_ON else 'OFF'}")

@app.on_message(filters.command(["bizadd"], prefixes=P))
async def bizadd_cmd(client, message: Message):
    if len(message.command) < 2 or "|" not in message.text:
        await _out(message, f"<code>{P}bizadd price | Rate 999</code>")
        return
    raw = message.text.split(None, 1)[1]
    key, val = [x.strip() for x in raw.split("|", 1)]
    d = _load_biz()
    d[key.lower()] = val
    _save_biz(d)
    await _out(message, f"✅ <b>{key}</b> saved")

@app.on_message(filters.private & filters.incoming & ~filters.me & filters.text, group=57)
async def ai_biz_watch(client, message: Message):
    text = (message.text or "").lower()
    if BIZ_ON:
        for k, v in _load_biz().items():
            if k in text:
                try:
                    await message.reply_text(v)
                except Exception:
                    pass
                return
    if AI_ON:
        try:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            await message.reply_text(random.choice(AI_LINES))
        except Exception:
            pass
