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
@app.on_message(filters.command(["sticker", "tosticker"], prefixes=P))
async def sticker_cmd(client, message: Message):
    r = message.reply_to_message
    if not r or not (r.photo or r.document):
        await _out(message, f"Reply photo + <code>{P}sticker</code>"); return
    path = await r.download()
    try:
        await message.reply_sticker(path)
    except Exception:
        try:
            from PIL import Image
            img = Image.open(path).convert("RGBA"); img.thumbnail((512, 512))
            out = path + ".webp"; img.save(out, "WEBP")
            await message.reply_document(out, caption="🎨 sticker")
            try: os.remove(out)
            except Exception: pass
        except Exception as e:
            await _out(message, f"❌ <code>{e}</code>")
    finally:
        try: os.remove(path)
        except Exception: pass
