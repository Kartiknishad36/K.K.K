import random
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
P = config.COMMAND_PREFIX
RIDDLES = [("Hamesha aata hai par kabhi nahi?", "Kal"), ("Bina pair chalta?", "Clock")]
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["riddle"], prefixes=P))
async def riddle_cmd(client, message: Message):
    q, a = random.choice(RIDDLES)
    await _out(message, f"🧩 <b>Riddle</b>\n{q}\n<code>{a}</code>")
