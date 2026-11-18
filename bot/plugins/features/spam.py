from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config, asyncio
P = config.COMMAND_PREFIX
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["spam"], prefixes=P))
async def spam_cmd(client, message: Message):
    if len(message.command) < 3:
        await _out(message, f"Usage: <code>{P}spam 9999999 Hello</code>")
        return
    try: count = min(int(message.command[1]), 20)
    except ValueError:
        await _out(message, "❌ Count number"); return
    text = message.text.split(None, 2)[2]
    for _ in range(count):
        try: await client.send_message(message.chat.id, text)
        except Exception: break
        await asyncio.sleep(0.35)
    try: await message.delete()
    except Exception: pass
