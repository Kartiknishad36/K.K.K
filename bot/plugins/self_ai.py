"""
🤖 Self AI / Auto Reply
.autoreply / .auto on|off
"""
import asyncio
import random
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from bot.client import app
import config

P = config.COMMAND_PREFIX
AUTO_REPLY = False
AUTO_CHATS = set()

REPLIES = [
    "Bhai bas market me hu, 10 min me aata hu 😊",
    "Haan bhai bol, thoda busy hu, abhi reply karta hu 👍",
    "Arey yaar, phone charge pe tha, bol kya hua? 🔋",
    "Hmm, samajh gaya, thodi der me call karta hu 📞",
    "Abhi thoda kaam pe hu, thodi der baad baat karte hai ✨",
    "Ok done, note kar liya 📝",
    "Haha sahi hai 😂",
    "Theek hai bhai, baad me detail me baat karte hai 🤝",
]

async def _out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["autoreply", "auto"], prefixes=P))
async def toggle_auto(client, message: Message):
    global AUTO_REPLY
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    if arg in ("on", "1", "true", "enable"):
        AUTO_REPLY = True
    elif arg in ("off", "0", "false", "disable"):
        AUTO_REPLY = False
    else:
        AUTO_REPLY = not AUTO_REPLY
    if AUTO_REPLY:
        AUTO_CHATS.add(message.chat.id)
    await _out(
        message,
        f"🤖 <b>Auto Reply:</b> {'ON ✅' if AUTO_REPLY else 'OFF ❌'}\n"
        f"💬 Scope: DM\n"
        f"✏️ Replies: <code>{len(REPLIES)}</code>\n"
        f"Usage: <code>{P}auto on</code> / <code>{P}auto off</code>",
    )

@app.on_message(filters.command(["autoreplyset"], prefixes=P))
async def set_replies(client, message: Message):
    if len(message.command) < 2:
        await _out(message, f"Usage: <code>{P}autoreplyset line1 | line2</code>")
        return
    raw = message.text.split(None, 1)[1]
    parts = [p.strip() for p in raw.split("|") if p.strip()]
    REPLIES.clear()
    REPLIES.extend(parts)
    await _out(message, f"✅ {len(REPLIES)} replies set.")

@app.on_message(filters.private & filters.incoming & ~filters.me & ~filters.bot, group=45)
async def auto_reply_dm(client, message: Message):
    if not AUTO_REPLY or not message.text:
        return
    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        await asyncio.sleep(random.uniform(0.8, 2.2))
        await message.reply_text(random.choice(REPLIES))
    except Exception:
        pass
