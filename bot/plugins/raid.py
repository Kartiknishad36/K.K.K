"""Reply raid controls"""
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
RAID_RUN = {}

async def out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["replyraid", "raid"], prefixes=P))
async def raid_cmd(client, message: Message):
    if not message.reply_to_message:
        await out(message, f"Reply to user + `{P}replyraid <count> <text>`")
        return
    count = 999999999
    text = "Raid"
    args = message.command[1:]
    if args and args[0].isdigit():
        count = min(int(args[0]), 30)
        text = " ".join(args[1:]) or text
    elif args:
        text = " ".join(args)
    chat_id = message.chat.id
    target = message.reply_to_message
    RAID_RUN[chat_id] = True
    status = await out(message, f"⚔ Raid x{count}...")
    n = 0
    for _ in range(count):
        if not RAID_RUN.get(chat_id):
            break
        try:
            await target.reply_text(text)
            n += 1
        except Exception:
            break
        await asyncio.sleep(0.8)
    RAID_RUN[chat_id] = False
    await status.edit_text(f"⚔ Done `{n}`")

@app.on_message(filters.command(["raidstop", "stopraid"], prefixes=P))
async def raid_stop(client, message: Message):
    RAID_RUN[message.chat.id] = False
    await out(message, "🛑 Raid stopped")
