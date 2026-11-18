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
async def _tts(message, text, lang="hi", slow=False):
    path = "vf_out.mp3"; status = await _out(message, "🎙️ ...")
    try:
        from gtts import gTTS
        gTTS(text=text, lang=lang, slow=slow).save(path)
        await message.reply_voice(path, caption=f"🎙️ {lang}")
        if status:
            try: await status.delete()
            except Exception: pass
    except Exception as e:
        if status:
            try: await status.edit_text(f"❌ <code>{e}</code>")
            except Exception: pass
    finally:
        try: os.remove(path)
        except Exception: pass
@app.on_message(filters.command(["vf", "voicefx"], prefixes=P))
async def vf_cmd(client, message: Message):
    if len(message.command) < 2:
        await _out(message, f"<code>{P}vf Hello</code>"); return
    if message.command[1].lower() in ("en", "hi", "es", "fr") and len(message.command) >= 3:
        lang = message.command[1].lower(); text = message.text.split(None, 2)[2]
    else:
        lang, text = "hi", message.text.split(None, 1)[1]
    await _tts(message, text, lang=lang)
@app.on_message(filters.command(["vrobot"], prefixes=P))
async def vrobot_cmd(client, message: Message):
    if len(message.command) < 2:
        await _out(message, f"<code>{P}vrobot text</code>"); return
    await _tts(message, message.text.split(None, 1)[1], lang="en", slow=True)
