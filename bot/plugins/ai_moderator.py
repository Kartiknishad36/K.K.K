"""
🛡️ AI Moderator — gaali/link + warns
.antion / .antioff
"""
import re
from collections import defaultdict
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from bot.client import app
import config

P = config.COMMAND_PREFIX
ANTI_ON = set()
WARNS = defaultdict(int)
MAX_WARN = 3
BAD_WORDS = ["mc", "bc", "bkl", "madarchod", "behenchod", "chutiya", "bsdk", "gandu"]
LINK_RE = re.compile(r"(https?://|t\.me/|telegram\.me/|www\.)", re.I)

async def _out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["antion"], prefixes=P))
async def anti_on(client, message: Message):
    ANTI_ON.add(message.chat.id)
    await _out(message, f"🛡️ <b>Moderator ON</b>\nMax warns: {MAX_WARN}\nOff: <code>{P}antioff</code>")

@app.on_message(filters.command(["antioff"], prefixes=P))
async def anti_off(client, message: Message):
    ANTI_ON.discard(message.chat.id)
    await _out(message, "🛡️ Moderator <b>OFF</b>")

@app.on_message(filters.group & filters.incoming & ~filters.me & filters.text, group=33)
async def moderator(client, message: Message):
    if message.chat.id not in ANTI_ON or not message.from_user:
        return
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            return
    except Exception:
        pass
    text = (message.text or "").lower()
    key = (message.chat.id, message.from_user.id)
    if any(w in text for w in BAD_WORDS):
        try:
            await message.delete()
        except Exception:
            pass
        WARNS[key] += 1
        w = WARNS[key]
        name = message.from_user.mention
        if w >= MAX_WARN:
            try:
                await client.restrict_chat_member(message.chat.id, message.from_user.id, permissions=None)
            except Exception:
                pass
            await client.send_message(message.chat.id, f"🚫 {name} max warns — restricted")
            return
        await client.send_message(message.chat.id, f"⚠️ {name} gaali mat do! Warn <b>{w}/{MAX_WARN}</b>")
        return
    if LINK_RE.search(text):
        try:
            await message.delete()
            await client.send_message(message.chat.id, f"🔗 {message.from_user.mention} links nahi!")
        except Exception:
            pass
