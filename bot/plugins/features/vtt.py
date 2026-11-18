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
@app.on_message(filters.command(["vtt", "voicetext"], prefixes=P))
async def vtt_cmd(client, message: Message):
    r = message.reply_to_message
    if not r or not (r.voice or r.audio):
        await _out(message, f"Reply voice + <code>{P}vtt</code>"); return
    await _out(message, "🎙️ STT needs external API — media only for now.")
