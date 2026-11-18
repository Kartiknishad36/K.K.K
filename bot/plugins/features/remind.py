import asyncio, re
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
P = config.COMMAND_PREFIX
TASKS = []
def _parse(token):
    m = re.fullmatch(r"(\d+)([smhd])", token.lower())
    if not m: return None
    n, u = int(m.group(1)), m.group(2)
    return min(n * {"s": 1, "m": 60, "h": 3600, "d": 86400}[u], 7 * 86400)
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["remind"], prefixes=P))
async def remind_cmd(client, message: Message):
    if len(message.command) < 3:
        await _out(message, f"<code>{P}remind 5m text</code>"); return
    delay = _parse(message.command[1])
    if delay is None:
        await _out(message, "Time: 30s / 5m / 2h / 1d"); return
    text = message.text.split(None, 2)[2]; chat_id = message.chat.id
    async def _job():
        await asyncio.sleep(delay)
        try: await client.send_message(chat_id, f"⏰ <b>Remind</b>\n{text}")
        except Exception: pass
    asyncio.create_task(_job()); TASKS.append({"delay": delay, "text": text[:80]})
    await _out(message, f"✅ In <code>{message.command[1]}</code>")
@app.on_message(filters.command(["remindlist"], prefixes=P))
async def remindlist_cmd(client, message: Message):
    if not TASKS:
        await _out(message, "📭 None"); return
    await _out(message, "⏰\n" + "\n".join(f"• {t['delay']}s — {t['text']}" for t in TASKS[-15:]))
