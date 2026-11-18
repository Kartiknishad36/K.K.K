"""💾 Backup | 🔒 Chatlock
.backup  .chatlock on|off  .autodelchat minutes
"""
from pathlib import Path
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
LOCKED = set()
AUTODEL_MIN = {}

async def _out(m, t):
    try:
        return await m.reply_text(t)
    except Exception:
        try:
            return await m.edit_text(t)
        except Exception:
            return None

@app.on_message(filters.command(["backup"], prefixes=P))
async def backup_cmd(client, message: Message):
    data = Path(getattr(config, "DATA_DIR", Path("data")))
    files = list(data.glob("*")) if data.exists() else []
    lines = [f"💾 <b>Backup</b>", f"Folder: <code>{data}</code>", f"Files: {len(files)}"]
    for f in files[:20]:
        lines.append(f"• {f.name} ({f.stat().st_size}b)")
    try:
        await client.send_message("me", "\n".join(lines))
        await _out(message, "✅ → Saved Messages")
    except Exception as e:
        await _out(message, f"❌ <code>{e}</code>")

@app.on_message(filters.command(["chatlock"], prefixes=P))
async def chatlock_cmd(client, message: Message):
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    cid = message.chat.id
    if arg in ("on", "1"):
        LOCKED.add(cid)
    elif arg in ("off", "0", "unlock"):
        LOCKED.discard(cid)
    else:
        if cid in LOCKED:
            LOCKED.discard(cid)
        else:
            LOCKED.add(cid)
    await _out(message, f"🔒 Flag: {'ON' if cid in LOCKED else 'OFF'} (local only)")

@app.on_message(filters.command(["autodelchat"], prefixes=P))
async def autodelchat_cmd(client, message: Message):
    if len(message.command) < 2 or not message.command[1].isdigit():
        await _out(message, f"<code>{P}autodelchat 5</code>")
        return
    m = int(message.command[1])
    if m <= 0:
        AUTODEL_MIN.pop(message.chat.id, None)
        await _out(message, "⏱️ OFF")
    else:
        AUTODEL_MIN[message.chat.id] = m
        await _out(message, f"⏱️ Flag {m} min")
