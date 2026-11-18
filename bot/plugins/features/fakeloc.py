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
@app.on_message(filters.command(["fakeloc", "location"], prefixes=P))
async def fakeloc_cmd(client, message: Message):
    if len(message.command) < 3:
        await _out(message, f"<code>{P}fakeloc 28.61 77.20 Delhi</code>"); return
    try: lat, lon = float(message.command[1]), float(message.command[2])
    except ValueError:
        await _out(message, "lat lon numbers"); return
    title = " ".join(message.command[3:]) if len(message.command) > 3 else "Location"
    try:
        await client.send_location(message.chat.id, latitude=lat, longitude=lon)
        await _out(message, f"📍 {title} ({lat},{lon})")
    except Exception as e:
        await _out(message, f"❌ <code>{e}</code>")
