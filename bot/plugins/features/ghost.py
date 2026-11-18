from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
P = config.COMMAND_PREFIX
GHOST = False
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["ghost"], prefixes=P))
async def ghost_cmd(client, message: Message):
    global GHOST
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    if arg in ("on", "1"): GHOST = True
    elif arg in ("off", "0"): GHOST = False
    else: GHOST = not GHOST
    await _out(message, f"👻 Ghost: {'ON' if GHOST else 'OFF'}")
@app.on_message(filters.command(["ghoststatus"], prefixes=P))
async def ghost_status(client, message: Message):
    await _out(message, f"👻 Ghost: <b>{'ON' if GHOST else 'OFF'}</b>")
