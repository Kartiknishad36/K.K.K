import random
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
P = config.COMMAND_PREFIX
TRUTHS = ["Sabse embarrassing moment?", "Last lie kab boli?", "Crush ka naam?"]
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["truth"], prefixes=P))
async def truth_cmd(client, message: Message):
    await _out(message, f"🎯 <b>Truth</b>\n{random.choice(TRUTHS)}")
