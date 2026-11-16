"""Anti-spam flood control"""
import time
from collections import defaultdict
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from bot.client import app
import config

P = config.COMMAND_PREFIX
ANTISPAM_ON = set()
FLOOD = defaultdict(list)
LIMIT = 6
WINDOW = 5

async def out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["antispam"], prefixes=P))
async def antispam_cmd(client, message: Message):
    chat_id = message.chat.id
    if chat_id in ANTISPAM_ON:
        ANTISPAM_ON.discard(chat_id)
        await out(message, "🛡 Anti-spam **OFF**")
    else:
        ANTISPAM_ON.add(chat_id)
        await out(message, "🛡 Anti-spam **ON**")

@app.on_message(filters.group & filters.incoming & ~filters.me, group=31)
async def antispam_watcher(client, message: Message):
    if message.chat.id not in ANTISPAM_ON or not message.from_user:
        return
    key = (message.chat.id, message.from_user.id)
    now = time.time()
    FLOOD[key] = [t for t in FLOOD[key] if now - t < WINDOW]
    FLOOD[key].append(now)
    if len(FLOOD[key]) < LIMIT:
        return
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            return
        await message.delete()
    except Exception:
        try:
            await message.delete()
        except Exception:
            pass
