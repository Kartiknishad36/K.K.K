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
@app.on_message(filters.command(["kang", "steal"], prefixes=P))
async def kang_cmd(client, message: Message):
    r = message.reply_to_message
    if not r or not r.sticker:
        await _out(message, f"Reply sticker + <code>{P}kang</code>"); return
    try:
        await r.copy(message.chat.id)
        await _out(message, "🎨 Sticker copied.")
    except Exception as e:
        await _out(message, f"❌ <code>{e}</code>")
