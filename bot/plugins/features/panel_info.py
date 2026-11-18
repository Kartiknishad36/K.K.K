"""
🌐 Panel / deploy info
.panel  .webpanel
"""
import os
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX


async def _out(m, t):
    try:
        return await m.reply_text(t)
    except Exception:
        try:
            return await m.edit_text(t)
        except Exception:
            return None


@app.on_message(filters.command(["panel", "webpanel"], prefixes=P))
async def panel_cmd(client, message: Message):
    port = os.getenv("PORT", "10000")
    host = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("RAILWAY_PUBLIC_DOMAIN") or ""
    await _out(
        message,
        f"🌐 <b>Panel / Host info</b>\n\n"
        f"• PORT: <code>{port}</code>\n"
        f"• Public URL env: <code>{host or 'not set'}</code>\n"
        f"• Prefix: <code>{P}</code>\n"
        f"• Owner: <code>{getattr(config, 'OWNER_ID', 0)}</code>\n\n"
        f"Deploy: Render / Railway / Koyeb\n"
        f"Health route usually <code>/</code> if Flask keep-alive enabled.\n"
        f"Bot control: Telegram commands (this userbot), not public admin panel.",
    )
