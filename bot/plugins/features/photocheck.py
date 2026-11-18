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
@app.on_message(filters.command(["photocheck", "imginfo"], prefixes=P))
async def photocheck_cmd(client, message: Message):
    r = message.reply_to_message
    if not r or not r.photo:
        await _out(message, f"Reply photo + <code>{P}photocheck</code>"); return
    p = r.photo
    lines = [f"🖼 <b>Photo</b>", f"W×H: {p.width}×{p.height}", f"Size: {p.file_size}"]
    path = None
    try:
        path = await r.download()
        from PIL import Image
        img = Image.open(path)
        lines += [f"Format: {img.format}", f"Mode: {img.mode}"]
    except Exception as e:
        lines.append(str(e))
    finally:
        if path:
            try: os.remove(path)
            except Exception: pass
    await _out(message, "\n".join(lines))
