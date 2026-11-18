import time
from datetime import datetime, timezone
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
P = config.COMMAND_PREFIX
START_TS = time.time()
def _fmt(sec):
    sec = int(sec); h, r = divmod(sec, 3600); m, s = divmod(r, 60); d, h = divmod(h, 24)
    return f"{d}d {h}h {m}m {s}s" if d else (f"{h}h {m}m {s}s" if h else f"{m}m {s}s")
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["screentime", "online", "uptime"], prefixes=P))
async def screentime_cmd(client, message: Message):
    up = time.time() - START_TS
    me = await client.get_me()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    await _out(message, f"⏱️ <b>Uptime</b>\n👤 {me.first_name}\n🆔 <code>{me.id}</code>\n🟢 {_fmt(up)}\n🕒 {now}")
