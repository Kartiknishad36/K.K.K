"""🎁 Giveaway | 🎂 Birthday
.giveaway  .bdayadd Name YYYY-MM-DD  .bdays
"""
import json
import random
from datetime import datetime, date
from pathlib import Path
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
DATA = Path(getattr(config, "DATA_DIR", Path("data"))) / "birthdays.json"
DATA.parent.mkdir(parents=True, exist_ok=True)

def _load():
    if not DATA.exists():
        return []
    try:
        return json.loads(DATA.read_text())
    except Exception:
        return []

def _save(rows):
    DATA.write_text(json.dumps(rows, indent=2))

async def _out(m, t):
    try:
        return await m.reply_text(t)
    except Exception:
        try:
            return await m.edit_text(t)
        except Exception:
            return None

@app.on_message(filters.command(["giveaway"], prefixes=P))
async def giveaway_cmd(client, message: Message):
    users, seen = [], set()
    async for m in client.get_chat_history(message.chat.id, limit=80):
        if m.from_user and not m.from_user.is_bot and m.from_user.id not in seen:
            seen.add(m.from_user.id)
            users.append(m.from_user)
    if len(users) < 2:
        await _out(message, "❌ Enough users nahi")
        return
    win = random.choice(users)
    await _out(message, f"🎁 <b>WINNER</b>\n👤 {win.mention}\n🆔 <code>{win.id}</code>\nPool: {len(users)}")

@app.on_message(filters.command(["bdayadd"], prefixes=P))
async def bday_add(client, message: Message):
    if len(message.command) < 3:
        await _out(message, f"<code>{P}bdayadd Name 2000-01-31</code>")
        return
    name, day = message.command[1], message.command[2]
    try:
        datetime.strptime(day, "%Y-%m-%d")
    except ValueError:
        await _out(message, "YYYY-MM-DD")
        return
    rows = _load()
    rows.append({"name": name, "date": day})
    _save(rows)
    await _out(message, f"🎂 Saved {name}")

@app.on_message(filters.command(["bdays"], prefixes=P))
async def bdays_cmd(client, message: Message):
    rows = _load()
    if not rows:
        await _out(message, "📭 No birthdays")
        return
    today = date.today()
    lines = ["🎂 <b>Birthdays</b>"]
    for r in rows[:40]:
        try:
            d = datetime.strptime(r["date"], "%Y-%m-%d").date()
            nxt = d.replace(year=today.year)
            if nxt < today:
                nxt = nxt.replace(year=today.year + 1)
            delta = (nxt - today).days
            lines.append(f"• {r['name']} — {r['date'][5:]} ({'TODAY' if delta==0 else str(delta)+'d'})")
        except Exception:
            lines.append(f"• {r}")
    await _out(message, "\n".join(lines))
