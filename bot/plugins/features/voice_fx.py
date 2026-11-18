"""
🎙️ Voice FX / simple voice changer (TTS voices)
.vf <text>           — Hindi TTS
.vf en <text>        — English
.vrobot <text>       — slow/robot-ish
"""
import os
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX


async def _out(m, t):
    try:
        return await m.reply_text(t)
    except Exception:
        try:
            return await m.edit_text(t)
        except Exception:
            return None


async def _tts_send(message, text: str, lang: str = "hi", slow: bool = False):
    path = "vf_out.mp3"
    status = await _out(message, "🎙️ Voice bana raha hu...")
    try:
        from gtts import gTTS

        gTTS(text=text, lang=lang, slow=slow).save(path)
        await message.reply_voice(path, caption=f"🎙️ lang=<code>{lang}</code> slow={slow}")
        if status:
            try:
                await status.delete()
            except Exception:
                pass
    except Exception as e:
        if status:
            try:
                await status.edit_text(f"❌ <code>{e}</code>")
            except Exception:
                pass
    finally:
        try:
            os.remove(path)
        except Exception:
            pass


@app.on_message(filters.command(["vf", "voicefx"], prefixes=P))
async def vf_cmd(client, message: Message):
    if len(message.command) < 2:
        await _out(
            message,
            f"🎙️ <b>Voice FX</b>\n"
            f"<code>{P}vf Hello bhai</code>\n"
            f"<code>{P}vf en Hello friend</code>\n"
            f"<code>{P}vrobot text</code>",
        )
        return
    # .vf en text...
    if message.command[1].lower() in ("en", "hi", "es", "fr", "de") and len(message.command) >= 3:
        lang = message.command[1].lower()
        text = message.text.split(None, 2)[2]
    else:
        lang = "hi"
        text = message.text.split(None, 1)[1]
    await _tts_send(message, text, lang=lang, slow=False)


@app.on_message(filters.command(["vrobot"], prefixes=P))
async def vrobot_cmd(client, message: Message):
    if len(message.command) < 2:
        await _out(message, f"<code>{P}vrobot Hello I am robot</code>")
        return
    text = message.text.split(None, 1)[1]
    await _tts_send(message, text, lang="en", slow=True)
