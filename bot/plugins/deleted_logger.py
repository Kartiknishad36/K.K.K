"""
🗑️ Deleted Message Logger (DM cache)
.deleted / .delmsg / .cleardeleted
"""
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
CACHE = {}
MAX = 200

async def _out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.private & filters.incoming & ~filters.me, group=46)
async def save_msg(client, message: Message):
    if not message.from_user:
        return
    text = message.text or message.caption or ""
    if not text and not message.media:
        return
    name = message.from_user.first_name or "User"
    kind = "media" if message.media and not text else "text"
    CACHE[message.id] = f"👤 {name} (`{message.from_user.id}`)\n📎 {kind}\n💬 {text[:300] or '[media]'}"
    if len(CACHE) > MAX:
        for k in list(CACHE.keys())[: len(CACHE) - MAX]:
            CACHE.pop(k, None)

@app.on_message(filters.command(["deleted", "delmsg"], prefixes=P))
async def show_deleted(client, message: Message):
    if not CACHE:
        await _out(message, "📭 Cache empty")
        return
    items = list(CACHE.values())[-10:]
    await _out(message, "🗑️ <b>Last DM snapshots</b>\n\n" + "\n\n———\n\n".join(items))

@app.on_message(filters.command(["cleardeleted", "cleardel"], prefixes=P))
async def clear_deleted(client, message: Message):
    CACHE.clear()
    await _out(message, "🧹 Cache clear")
