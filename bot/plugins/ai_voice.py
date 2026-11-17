"""
🎙️ Text → Voice TTS
.voice / .tts <text>
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

@app.on_message(filters.command(["voice", "tts"], prefixes=P))
async def voice_cmd(client, message: Message):
    if len(message.command) < 2:
        await _out(message, f"🎙️ <code>{P}voice Hello bhai</code>")
        return
    text = message.text.split(None, 1)[1]
    status = await _out(message, "🎙️ Voice bana raha hu...")
    path = "voice_tts.mp3"
    try:
        try:
            from gtts import gTTS
            gTTS(text=text, lang="hi", slow=False).save(path)
        except Exception:
            import edge_tts
            await edge_tts.Communicate(text, "hi-IN-SwaraNeural").save(path)
        await message.reply_voice(path, caption="🎙️ <b>AI Voice</b>")
        if status:
            try:
                await status.delete()
            except Exception:
                pass
        try:
            await message.delete()
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
