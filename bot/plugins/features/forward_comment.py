"""📨 Auto Forward | 💬 Comment
.af on|off  .afset <id>  .fwd <id>  .fcomment <text>
"""
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
AF_ON = False
AF_DEST = None

async def _out(m, t):
    try:
        return await m.reply_text(t)
    except Exception:
        try:
            return await m.edit_text(t)
        except Exception:
            return None

@app.on_message(filters.command(["af", "autoforward"], prefixes=P))
async def af_toggle(client, message: Message):
    global AF_ON
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    if arg in ("on", "1"):
        AF_ON = True
    elif arg in ("off", "0"):
        AF_ON = False
    else:
        AF_ON = not AF_ON
    await _out(message, f"📨 AutoForward: {'ON' if AF_ON else 'OFF'}\nDest: <code>{AF_DEST}</code>")

@app.on_message(filters.command(["afset"], prefixes=P))
async def af_set(client, message: Message):
    global AF_DEST
    if len(message.command) < 2:
        await _out(message, f"<code>{P}afset -100xxxx</code>")
        return
    AF_DEST = int(message.command[1])
    await _out(message, f"✅ Dest <code>{AF_DEST}</code>")

@app.on_message(filters.command(["fwd"], prefixes=P))
async def fwd_cmd(client, message: Message):
    if not message.reply_to_message or len(message.command) < 2:
        await _out(message, f"Reply + <code>{P}fwd chat_id</code>")
        return
    try:
        await message.reply_to_message.forward(int(message.command[1]))
        await _out(message, "✅ Forwarded")
    except Exception as e:
        await _out(message, f"❌ <code>{e}</code>")

@app.on_message(filters.incoming & ~filters.me, group=55)
async def af_watcher(client, message: Message):
    if not AF_ON or not AF_DEST:
        return
    try:
        if message.chat and str(getattr(message.chat, "type", "")).endswith("CHANNEL"):
            await message.forward(AF_DEST)
    except Exception:
        pass

@app.on_message(filters.command(["fcomment", "firstc"], prefixes=P))
async def fcomment_cmd(client, message: Message):
    if len(message.command) < 2:
        await _out(message, f"<code>{P}fcomment text</code>")
        return
    text = message.text.split(None, 1)[1]
    try:
        if message.reply_to_message:
            await message.reply_to_message.reply_text(text)
        else:
            await client.send_message(message.chat.id, text)
        await _out(message, "💬 Sent")
    except Exception as e:
        await _out(message, f"❌ <code>{e}</code>")
