"""Spam report / warns"""
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
REPORTS = []
WARNS = {}

async def out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["report"], prefixes=P))
async def report_cmd(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await out(message, "Reply to a user to report.")
        return
    u = message.reply_to_message.from_user
    REPORTS.append({"chat_id": message.chat.id, "user_id": u.id, "name": u.first_name})
    key = (message.chat.id, u.id)
    WARNS[key] = WARNS.get(key, 0) + 1
    await out(message, f"🚩 Reported {u.mention}\nWarns: **{WARNS[key]}**")

@app.on_message(filters.command(["reports"], prefixes=P))
async def reports_list(client, message: Message):
    if not REPORTS:
        await out(message, "No reports.")
        return
    lines = ["🚩 **Reports**"]
    for i, r in enumerate(REPORTS[-20:], 1):
        lines.append(f"{i}. `{r['user_id']}` {r['name']}")
    await out(message, "\n".join(lines))

@app.on_message(filters.command(["clearreports"], prefixes=P))
async def clear_reports(client, message: Message):
    REPORTS.clear()
    await out(message, "🗑 Reports cleared")

@app.on_message(filters.command(["resetwarns", "clearwarns"], prefixes=P))
async def reset_warns(client, message: Message):
    uid = None
    if message.reply_to_message and message.reply_to_message.from_user:
        uid = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try:
            uid = (await client.get_users(message.command[1])).id
        except Exception:
            pass
    if not uid:
        await out(message, "Reply / user do.")
        return
    WARNS.pop((message.chat.id, uid), None)
    await out(message, f"✅ Warns reset for `{uid}`")
