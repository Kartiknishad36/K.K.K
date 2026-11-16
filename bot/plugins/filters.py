"""Keyword filters — auto reply on keyword"""
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app, logger
import config

P = config.COMMAND_PREFIX
FILTERS = {}

async def out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["filter", "addfilter"], prefixes=P))
async def add_filter(client, message: Message):
    if len(message.command) < 3:
        await out(message, f"Usage: `{P}filter <key> <reply text>`")
        return
    key = message.command[1].lower()
    reply = " ".join(message.command[2:])
    FILTERS.setdefault(message.chat.id, {})[key] = reply
    await out(message, f"✅ Filter saved: `{key}`")

@app.on_message(filters.command(["stop", "stopfilter", "delfilter"], prefixes=P))
async def del_filter(client, message: Message):
    if len(message.command) < 2:
        await out(message, f"Usage: `{P}stop <key>`")
        return
    key = message.command[1].lower()
    removed = FILTERS.get(message.chat.id, {}).pop(key, None)
    await out(message, f"🗑 Removed `{key}`" if removed else f"❌ No filter `{key}`")

@app.on_message(filters.command(["filters", "listfilters"], prefixes=P))
async def list_filters(client, message: Message):
    keys = list(FILTERS.get(message.chat.id, {}).keys())
    if not keys:
        await out(message, "No filters in this chat.")
        return
    await out(message, "🔍 **Filters:**\n" + "\n".join(f"• `{k}`" for k in keys))

@app.on_message(filters.text & filters.incoming & ~filters.me, group=20)
async def filter_watcher(client, message: Message):
    text = (message.text or "").lower()
    for key, reply in list(FILTERS.get(message.chat.id, {}).items()):
        if key in text:
            try:
                await message.reply_text(reply)
            except Exception as e:
                logger.error(f"filter: {e}")
            break
