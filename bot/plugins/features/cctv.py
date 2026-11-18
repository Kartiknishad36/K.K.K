from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
P = config.COMMAND_PREFIX
MSG_CACHE = {}
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.group & filters.incoming & ~filters.me, group=56)
async def cctv_cache(client, message: Message):
    if not message.from_user: return
    MSG_CACHE[message.id] = {"name": message.from_user.first_name, "text": (message.text or message.caption or "")[:300]}
    if len(MSG_CACHE) > 500:
        for k in list(MSG_CACHE.keys())[:100]: MSG_CACHE.pop(k, None)
@app.on_message(filters.command(["cctv", "delwatch"], prefixes=P))
async def cctv_cmd(client, message: Message):
    items = list(MSG_CACHE.values())[-8:]
    if not items:
        await _out(message, "📹 Cache empty"); return
    lines = ["📹 <b>Recent</b>"] + [f"• {it['name']}: {it['text'][:80] or '[media]'}" for it in items]
    await _out(message, "\n".join(lines))
