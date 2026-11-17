"""
📸 Status Saver
.statussaver on|off
.savestatus — reply media → Saved Messages
"""
from datetime import datetime, timezone
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
STATUS_SAVER = False

async def _out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["statussaver", "ssaver"], prefixes=P))
async def saver_toggle(client, message: Message):
    global STATUS_SAVER
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    if arg in ("on", "1", "enable"):
        STATUS_SAVER = True
    elif arg in ("off", "0", "disable"):
        STATUS_SAVER = False
    else:
        STATUS_SAVER = not STATUS_SAVER
    await _out(
        message,
        f"📸 <b>Status Saver:</b> {'ON ✅' if STATUS_SAVER else 'OFF ❌'}\n"
        f"• <code>{P}savestatus</code> reply media → Saved Messages",
    )

@app.on_message(filters.command(["savestatus"], prefixes=P))
async def save_status_cmd(client, message: Message):
    r = message.reply_to_message
    if not r:
        await _out(message, f"Reply + <code>{P}savestatus</code>")
        return
    try:
        if r.media:
            path = await r.download()
            await client.send_document("me", path, caption=f"📸 {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}")
            await _out(message, "✅ Saved Messages")
        elif r.text:
            await client.send_message("me", f"📸 {r.text}")
            await _out(message, "✅ Text saved")
        else:
            await _out(message, "❌ Nothing to save")
    except Exception as e:
        await _out(message, f"❌ <code>{e}</code>")
