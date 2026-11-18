"""
🧹 Purge | 📢 Spam | ⌨️ Fake Typing
.purge [n]  .spam <count> <text>  .typing [sec]  .typing24 on|off
"""
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from bot.client import app
import config

P = config.COMMAND_PREFIX
_TYPING24 = False

async def _out(m, t):
    try:
        return await m.reply_text(t)
    except Exception:
        try:
            return await m.edit_text(t)
        except Exception:
            return None

@app.on_message(filters.command(["purge"], prefixes=P))
async def purge_cmd(client, message: Message):
    n = 50
    if len(message.command) > 1 and message.command[1].isdigit():
        n = min(int(message.command[1]), 200)
    status = await _out(message, f"🧹 Purging last <code>{n}</code>...")
    deleted = 0
    try:
        async for msg in client.get_chat_history(message.chat.id, limit=n):
            try:
                await msg.delete()
                deleted += 1
            except Exception:
                pass
            await asyncio.sleep(0.05)
    except Exception as e:
        await _out(message, f"❌ <code>{e}</code>")
        return
    if status:
        try:
            await status.edit_text(f"✅ Purged ~<code>{deleted}</code>")
        except Exception:
            pass

@app.on_message(filters.command(["spam"], prefixes=P))
async def spam_cmd(client, message: Message):
    if len(message.command) < 3:
        await _out(message, f"Usage: <code>{P}spam 5 Hello</code> (max 20)")
        return
    try:
        count = min(int(message.command[1]), 20)
    except ValueError:
        await _out(message, "Count number do")
        return
    text = message.text.split(None, 2)[2]
    for _ in range(count):
        try:
            await client.send_message(message.chat.id, text)
        except Exception:
            break
        await asyncio.sleep(0.35)
    try:
        await message.delete()
    except Exception:
        pass

@app.on_message(filters.command(["typing"], prefixes=P))
async def typing_cmd(client, message: Message):
    sec = 5
    if len(message.command) > 1 and message.command[1].isdigit():
        sec = min(int(message.command[1]), 30)
    await _out(message, f"⌨️ Typing {sec}s...")
    end = asyncio.get_event_loop().time() + sec
    while asyncio.get_event_loop().time() < end:
        try:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        except Exception:
            break
        await asyncio.sleep(4)

@app.on_message(filters.command(["typing24"], prefixes=P))
async def typing24_cmd(client, message: Message):
    global _TYPING24
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    if arg in ("on", "1"):
        _TYPING24 = True
    elif arg in ("off", "0"):
        _TYPING24 = False
    else:
        _TYPING24 = not _TYPING24
    await _out(message, f"⌨️ Typing24: {'ON' if _TYPING24 else 'OFF'}")
    if _TYPING24:
        asyncio.create_task(_typing_loop(client, message.chat.id))

async def _typing_loop(client, chat_id):
    while _TYPING24:
        try:
            await client.send_chat_action(chat_id, ChatAction.TYPING)
        except Exception:
            break
        await asyncio.sleep(4)
