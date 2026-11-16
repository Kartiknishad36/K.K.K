"""Hash utilities"""
import hashlib
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX

async def out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["sha", "hash", "md5", "sha256"], prefixes=P))
async def hash_cmd(client, message: Message):
    if len(message.command) < 2:
        await out(message, f"Usage: `{P}sha <text>`")
        return
    text = " ".join(message.command[1:])
    data = text.encode()
    lines = [
        "🔐 **HASH**",
        f"**Input:** `{text[:100]}`",
        f"**MD5:** `{hashlib.md5(data).hexdigest()}`",
        f"**SHA1:** `{hashlib.sha1(data).hexdigest()}`",
        f"**SHA256:** `{hashlib.sha256(data).hexdigest()}`",
        f"**SHA512:** `{hashlib.sha512(data).hexdigest()[:64]}...`",
    ]
    await out(message, "\n".join(lines))
