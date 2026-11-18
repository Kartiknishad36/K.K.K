"""
⏱️ Screen / Online time report (bot process uptime)
.screentime / .online / .uptime
"""
import time
from datetime import datetime, timezone
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
START_TS = time.time()
CMD_COUNT = 0


async def _out(m, t):
    try:
        return await m.reply_text(t)
    except Exception:
        try:
            return await m.edit_text(t)
        except Exception:
            return None


def _fmt(sec: float) -> str:
    sec = int(sec)
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    d, h = divmod(h, 24)
    if d:
        return f"{d}d {h}h {m}m {s}s"
    if h:
        return f"{h}h {m}m {s}s"
    return f"{m}m {s}s"


@app.on_message(filters.command(["screentime", "online", "uptime"], prefixes=P))
async def screentime_cmd(client, message: Message):
    global CMD_COUNT
    CMD_COUNT += 1
    up = time.time() - START_TS
    me = await client.get_me()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    await _out(
        message,
        f"⏱️ <b>Screen / Bot Time Report</b>\n\n"
        f"👤 Account: <b>{me.first_name}</b>\n"
        f"🆔 <code>{me.id}</code>\n"
        f"🟢 Process uptime: <code>{_fmt(up)}</code>\n"
        f"📊 Commands via this module: <code>{CMD_COUNT}</code>\n"
        f"🕒 Now: <code>{now}</code>\n\n"
        f"Note: Ye bot process uptime hai, Telegram last-seen alag hota hai.",
    )
