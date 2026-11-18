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
@app.on_message(filters.command(["fcomment", "firstc"], prefixes=P))
async def fcomment_cmd(client, message: Message):
    if len(message.command) < 2:
        await _out(message, f"<code>{P}fcomment text</code>"); return
    text = message.text.split(None, 1)[1]
    try:
        if message.reply_to_message: await message.reply_to_message.reply_text(text)
        else: await client.send_message(message.chat.id, text)
        await _out(message, "💬 Sent")
    except Exception as e:
        await _out(message, f"❌ <code>{e}</code>")
