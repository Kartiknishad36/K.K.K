"""Scheduler — schedule messages"""
import re
from datetime import datetime, timedelta, timezone
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
SCHEDULES = {}
_SID = 0

def parse_time(s):
    s = s.strip().lower()
    m = re.match(r"^(\d+)(s|m|h|d)$", s)
    if m:
        n, u = int(m.group(1)), m.group(2)
        delta = {"s": 1, "m": 60, "h": 3600, "d": 86400}[u]
        return datetime.now(timezone.utc) + timedelta(seconds=n * delta)
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
    except Exception:
        return None

async def out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["schedule", "sch"], prefixes=P))
async def schedule_cmd(client, message: Message):
    global _SID
    if len(message.command) < 3:
        await out(message, f"Usage: `{P}schedule <10m|2h|1d> <msg>`")
        return
    when = parse_time(message.command[1])
    if not when:
        await out(message, "Invalid time format.")
        return
    text = " ".join(message.command[2:])
    _SID += 1
    SCHEDULES[_SID] = {"id": _SID, "chat_id": message.chat.id, "when": when, "message": text, "done": False}
    await out(message, f"⏰ Scheduled **#{_SID}** at `{when.strftime('%Y-%m-%d %H:%M UTC')}`")

@app.on_message(filters.command(["schedules", "listsch"], prefixes=P))
async def list_sch(client, message: Message):
    pending = [s for s in SCHEDULES.values() if not s["done"]]
    if not pending:
        await out(message, "No pending schedules.")
        return
    lines = ["⏰ **Pending**"]
    for s in pending:
        lines.append(f"#{s['id']} → `{s['when'].strftime('%Y-%m-%d %H:%M')}` — {s['message'][:40]}")
    await out(message, "\n".join(lines))

@app.on_message(filters.command(["delschedule", "delsch"], prefixes=P))
async def del_sch(client, message: Message):
    if len(message.command) < 2:
        await out(message, f"Usage: `{P}delschedule <id>`")
        return
    try:
        sid = int(message.command[1].lstrip("#"))
    except ValueError:
        await out(message, "Invalid id")
        return
    if sid in SCHEDULES:
        SCHEDULES[sid]["done"] = True
        await out(message, f"🗑 Schedule #{sid} cancelled")
    else:
        await out(message, "Not found")
