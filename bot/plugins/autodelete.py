"""Auto-delete messages after N seconds"""
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app, logger
import config

P = config.COMMAND_PREFIX
AUTODEL = {}

async def out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["autodel", "autodelete"], prefixes=P))
async def autodel_cmd(client, message: Message):
    if len(message.command) < 2:
        cur = AUTODEL.get(message.chat.id)
        await out(message, f"Current: `{cur or 'OFF'}`\nUsage: `{P}autodel <seconds|off>`")
        return
    arg = message.command[1].lower()
    if arg in ("off", "0", "disable"):
        AUTODEL.pop(message.chat.id, None)
        await out(message, "🗑 Auto-delete **OFF**")
        return
    try:
        sec = int(arg)
        if sec < 1 or sec > 86400:
            raise ValueError
    except ValueError:
        await out(message, "Seconds must be 1–86400")
        return
    AUTODEL[message.chat.id] = sec
    await out(message, f"✅ Auto-delete **{sec}s**")

@app.on_message(filters.group & filters.incoming, group=50)
async def autodel_watcher(client, message: Message):
    sec = AUTODEL.get(message.chat.id)
    if not sec:
        return
    try:
        await asyncio.sleep(sec)
        await message.delete()
    except Exception:
        pass
