import random
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
P = config.COMMAND_PREFIX
QUIZ = [("Bharat capital?", "delhi"), ("2+2*2?", "6")]
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["quiz"], prefixes=P))
async def quiz_cmd(client, message: Message):
    q, a = random.choice(QUIZ)
    await _out(message, f"❓ <b>Quiz</b>\n{q}\n<code>{a}</code>")
