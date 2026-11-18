import os
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
@app.on_message(filters.command(["panel", "webpanel"], prefixes=P))
async def panel_cmd(client, message: Message):
    port = os.getenv("PORT", "10000")
    host = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("RAILWAY_PUBLIC_DOMAIN") or "not set"
    await _out(message, f"🌐 <b>Panel</b>\nPORT: <code>{port}</code>\nURL: <code>{host}</code>\nOwner: <code>{getattr(config,'OWNER_ID',0)}</code>")
