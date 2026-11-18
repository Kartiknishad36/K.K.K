import random
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
P = config.COMMAND_PREFIX
DARES = ["Funny voice note bhejo", "Random member ko compliment do"]
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["dare"], prefixes=P))
async def dare_cmd(client, message: Message):
    await _out(message, f"🔥 <b>Dare</b>\n{random.choice(DARES)}")
