import random
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
P = config.COMMAND_PREFIX
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["giveaway"], prefixes=P))
async def giveaway_cmd(client, message: Message):
    users, seen = [], set()
    async for m in client.get_chat_history(message.chat.id, limit=80):
        if m.from_user and not m.from_user.is_bot and m.from_user.id not in seen:
            seen.add(m.from_user.id); users.append(m.from_user)
    if len(users) < 2:
        await _out(message, "❌ Enough users nahi"); return
    win = random.choice(users)
    await _out(message, f"🎁 <b>WINNER</b>\n👤 {win.mention}\n🆔 <code>{win.id}</code>\nPool: {len(users)}")
