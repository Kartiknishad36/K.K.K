"""🎬 Movie (legal search) | 🧲 Filters
.movie name  .filteradd k | v  .filters
"""
import json
from pathlib import Path
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
DATA = Path(getattr(config, "DATA_DIR", Path("data"))) / "chat_filters.json"
DATA.parent.mkdir(parents=True, exist_ok=True)

def _load():
    if not DATA.exists():
        return {}
    try:
        return json.loads(DATA.read_text())
    except Exception:
        return {}

def _save(d):
    DATA.write_text(json.dumps(d, indent=2, ensure_ascii=False))

async def _out(m, t):
    try:
        return await m.reply_text(t)
    except Exception:
        try:
            return await m.edit_text(t)
        except Exception:
            return None

@app.on_message(filters.command(["movie"], prefixes=P))
async def movie_cmd(client, message: Message):
    if len(message.command) < 2:
        await _out(message, f"<code>{P}movie Pushpa</code>")
        return
    name = message.text.split(None, 1)[1]
    q = name.replace(" ", "+")
    await _out(message, f"🎬 <b>{name}</b>\n• https://www.imdb.com/find?q={q}\n• https://www.themoviedb.org/search?query={q}\n⚠️ Legal sources only")

@app.on_message(filters.command(["filteradd"], prefixes=P))
async def filteradd_cmd(client, message: Message):
    if len(message.command) < 2 or "|" not in (message.text or ""):
        await _out(message, f"<code>{P}filteradd hello | Welcome!</code>")
        return
    raw = message.text.split(None, 1)[1]
    k, v = [x.strip() for x in raw.split("|", 1)]
    d = _load()
    d.setdefault(str(message.chat.id), {})[k.lower()] = v
    _save(d)
    await _out(message, f"✅ Filter <b>{k}</b>")

@app.on_message(filters.command(["filters"], prefixes=P))
async def filters_list(client, message: Message):
    d = _load().get(str(message.chat.id), {})
    if not d:
        await _out(message, "📭 No filters")
        return
    lines = ["🧲 <b>Filters</b>"] + [f"• <code>{k}</code> → {v[:40]}" for k, v in d.items()]
    await _out(message, "\n".join(lines))

@app.on_message(filters.group & filters.incoming & ~filters.me & filters.text, group=58)
async def filter_watch(client, message: Message):
    d = _load().get(str(message.chat.id), {})
    if not d:
        return
    text = (message.text or "").lower()
    for k, v in d.items():
        if k in text:
            try:
                await message.reply_text(v)
            except Exception:
                pass
            return
