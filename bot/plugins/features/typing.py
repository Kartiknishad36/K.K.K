import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from bot.client import app
import config
P = config.COMMAND_PREFIX
_TYPING24 = False
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["typing"], prefixes=P))
async def typing_cmd(client, message: Message):
    sec = 5
    if len(message.command) > 1 and message.command[1].isdigit():
        sec = min(int(message.command[1]), 30)
    await _out(message, f"⌨️ Typing {sec}s...")
    end = asyncio.get_event_loop().time() + sec
    while asyncio.get_event_loop().time() < end:
        try: await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        except Exception: break
        await asyncio.sleep(4)
@app.on_message(filters.command(["typing24"], prefixes=P))
async def typing24_cmd(client, message: Message):
    global _TYPING24
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    if arg in ("on", "1"): _TYPING24 = True
    elif arg in ("off", "0"): _TYPING24 = False
    else: _TYPING24 = not _TYPING24
    await _out(message, f"⌨️ Typing24: {'ON' if _TYPING24 else 'OFF'}")
    if _TYPING24:
        async def _loop():
            while _TYPING24:
                try: await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                except Exception: break
                await asyncio.sleep(4)
        asyncio.create_task(_loop())
