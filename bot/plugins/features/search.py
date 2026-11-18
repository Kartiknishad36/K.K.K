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
@app.on_message(filters.command(["search", "csearch"], prefixes=P))
async def search_cmd(client, message: Message):
    if len(message.command) < 2:
        await _out(message, f"<code>{P}search keyword</code>"); return
    q = message.text.split(None, 1)[1].lower(); hits = []
    async for m in client.get_chat_history(message.chat.id, limit=300):
        t = m.text or m.caption or ""
        if q in t.lower():
            hits.append(f"• <code>{m.id}</code>: {t[:80]}")
        if len(hits) >= 10: break
    await _out(message, "🔎 No hits" if not hits else "🔎 <b>Results</b>\n" + "\n".join(hits))
