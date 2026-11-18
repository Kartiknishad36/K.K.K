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
@app.on_message(filters.command(["fwd"], prefixes=P))
async def fwd_cmd(client, message: Message):
    if not message.reply_to_message or len(message.command) < 2:
        await _out(message, f"Reply + <code>{P}fwd chat_id</code>"); return
    try:
        await message.reply_to_message.forward(int(message.command[1]))
        await _out(message, "✅ Forwarded")
    except Exception as e:
        await _out(message, f"❌ <code>{e}</code>")
