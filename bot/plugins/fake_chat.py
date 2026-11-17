"""
😂 Fake Chat Meme
.fake @user Hello
"""
import os
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX

async def _out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["fake", "fakechat"], prefixes=P))
async def fake_cmd(client, message: Message):
    if len(message.command) < 3:
        await _out(message, f"😂 <code>{P}fake @user Hii kaisa hai</code>\n⚠️ Meme only")
        return
    user = message.command[1]
    text = message.text.split(None, 2)[2]
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (800, 280), color=(18, 18, 24))
        d = ImageDraw.Draw(img)
        try:
            font_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except Exception:
            font_b = font = font_s = ImageFont.load_default()
        d.rounded_rectangle((20, 20, 780, 220), radius=16, fill=(32, 34, 42))
        d.text((40, 40), str(user)[:40], fill=(120, 200, 255), font=font_b)
        y = 90
        line = ""
        for ch in text[:180]:
            line += ch
            if len(line) > 42:
                d.text((40, y), line, fill=(230, 230, 235), font=font)
                y += 32
                line = ""
        if line:
            d.text((40, y), line, fill=(230, 230, 235), font=font)
        d.text((40, 240), "WARNING FAKE / MEME", fill=(255, 70, 70), font=font_s)
        path = "fake_chat.png"
        img.save(path)
        await message.reply_photo(path, caption="😂 <b>Fake Chat Meme</b>")
        try:
            os.remove(path)
        except Exception:
            pass
    except ImportError:
        await _out(message, f"💬 <b>{user}</b>\n{text}\n\n⚠️ FAKE MEME (PIL missing)")
    except Exception as e:
        await _out(message, f"❌ <code>{e}</code>")
