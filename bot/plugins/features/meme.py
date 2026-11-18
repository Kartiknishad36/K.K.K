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
@app.on_message(filters.command(["meme"], prefixes=P))
async def meme_cmd(client, message: Message):
    r = message.reply_to_message
    if not r or not r.photo:
        await _out(message, f"Reply photo + <code>{P}meme text</code>"); return
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else "LOL"
    path = await r.download()
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.open(path).convert("RGB"); d = ImageDraw.Draw(img)
        try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except Exception: font = ImageFont.load_default()
        d.text((20, 20), text[:60], fill=(255, 255, 0), font=font)
        out = path + "_meme.jpg"; img.save(out, quality=90)
        await message.reply_photo(out, caption="😂 Meme")
        try: os.remove(out)
        except Exception: pass
    except Exception as e:
        await _out(message, f"❌ <code>{e}</code>")
    finally:
        try: os.remove(path)
        except Exception: pass
