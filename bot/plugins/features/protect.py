from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
P = config.COMMAND_PREFIX
PROTECT_ON = set()
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["protect"], prefixes=P))
async def protect_cmd(client, message: Message):
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    cid = message.chat.id
    if arg in ("on", "1"): PROTECT_ON.add(cid)
    elif arg in ("off", "0"): PROTECT_ON.discard(cid)
    else:
        if cid in PROTECT_ON: PROTECT_ON.discard(cid)
        else: PROTECT_ON.add(cid)
    await _out(message, f"🛡️ Protect: {'ON' if cid in PROTECT_ON else 'OFF'}")
