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
@app.on_message(filters.command(["movie"], prefixes=P))
async def movie_cmd(client, message: Message):
    if len(message.command) < 2:
        await _out(message, f"<code>{P}movie Pushpa</code>"); return
    name = message.text.split(None, 1)[1].strip(); q = name.replace(" ", "+")
    await _out(message, f"🎬 <b>{name}</b>\n• https://www.imdb.com/find?q={q}\n• https://www.themoviedb.org/search?query={q}\n⚠️ Legal only")
