from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
P = config.COMMAND_PREFIX
GM_CHATS = set()
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["gm"], prefixes=P))
async def gm_cmd(client, message: Message):
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    cid = message.chat.id
    if arg in ("on", "1"):
        GM_CHATS.add(cid); await _out(message, "🌅 GM flag ON")
    elif arg in ("off", "0"):
        GM_CHATS.discard(cid); await _out(message, "🌅 OFF")
    else:
        await _out(message, f"<code>{P}gm on</code> / <code>{P}gmnow</code>")
@app.on_message(filters.command(["gmnow"], prefixes=P))
async def gmnow_cmd(client, message: Message):
    await client.send_message(message.chat.id, "🌅 Good Morning! Have a great day ✨")
    await _out(message, "✅ Sent")
