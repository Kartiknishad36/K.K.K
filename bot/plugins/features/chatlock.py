from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
P = config.COMMAND_PREFIX
LOCKED = set()
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["chatlock"], prefixes=P))
async def chatlock_cmd(client, message: Message):
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    cid = message.chat.id
    if arg in ("on", "1"): LOCKED.add(cid)
    elif arg in ("off", "0", "unlock"): LOCKED.discard(cid)
    else:
        if cid in LOCKED: LOCKED.discard(cid)
        else: LOCKED.add(cid)
    await _out(message, f"🔒 Flag: {'ON' if cid in LOCKED else 'OFF'}")
