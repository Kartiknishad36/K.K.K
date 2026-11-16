"""Anti-link — delete links from non-admins"""
import re
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from bot.client import app, logger
import config

P = config.COMMAND_PREFIX
ANTILINK_ON = set()
LINK_RE = re.compile(r"(https?://|t\.me/|telegram\.me/|www\.)", re.I)

async def out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["antilink"], prefixes=P))
async def antilink_cmd(client, message: Message):
    chat_id = message.chat.id
    if chat_id in ANTILINK_ON:
        ANTILINK_ON.discard(chat_id)
        await out(message, "🔗 Anti-link **OFF**")
    else:
        ANTILINK_ON.add(chat_id)
        await out(message, "🔗 Anti-link **ON**")

@app.on_message(filters.group & filters.text & filters.incoming & ~filters.me, group=30)
async def antilink_watcher(client, message: Message):
    if message.chat.id not in ANTILINK_ON:
        return
    if not message.text or not LINK_RE.search(message.text):
        return
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            return
        await message.delete()
        warn = await client.send_message(message.chat.id, f"⚠️ Links not allowed, {message.from_user.mention}")
        await asyncio.sleep(3)
        await warn.delete()
    except Exception as e:
        logger.error(f"antilink: {e}")
