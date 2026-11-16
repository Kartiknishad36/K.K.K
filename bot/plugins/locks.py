"""Chat locks — media/stickers/url/forward"""
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from bot.client import app
import config

P = config.COMMAND_PREFIX
LOCKS = {}
VALID = {"media", "stickers", "gif", "url", "forward", "all"}

async def out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["lock"], prefixes=P))
async def lock_cmd(client, message: Message):
    if len(message.command) < 2:
        await out(message, f"Usage: `{P}lock <media|stickers|gif|url|forward|all>`")
        return
    t = message.command[1].lower()
    if t not in VALID:
        await out(message, f"Valid: {', '.join(VALID)}")
        return
    LOCKS.setdefault(message.chat.id, set()).add(t)
    await out(message, f"🔒 Locked **{t}**")

@app.on_message(filters.command(["unlock"], prefixes=P))
async def unlock_cmd(client, message: Message):
    if len(message.command) < 2:
        await out(message, f"Usage: `{P}unlock <type|all>`")
        return
    t = message.command[1].lower()
    if t == "all":
        LOCKS.pop(message.chat.id, None)
        await out(message, "🔓 All unlocked")
        return
    LOCKS.get(message.chat.id, set()).discard(t)
    await out(message, f"🔓 Unlocked **{t}**")

@app.on_message(filters.command(["locks"], prefixes=P))
async def locks_list(client, message: Message):
    cur = LOCKS.get(message.chat.id, set())
    await out(message, "🔒 " + (", ".join(cur) if cur else "None"))

@app.on_message(filters.group & filters.incoming & ~filters.me, group=32)
async def locks_watcher(client, message: Message):
    locked = LOCKS.get(message.chat.id, set())
    if not locked or not message.from_user:
        return
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            return
    except Exception:
        return
    hit = "all" in locked
    if "media" in locked and message.media:
        hit = True
    if "stickers" in locked and message.sticker:
        hit = True
    if "gif" in locked and message.animation:
        hit = True
    if "url" in locked and message.text and ("http" in message.text or "t.me/" in message.text):
        hit = True
    if "forward" in locked and message.forward_date:
        hit = True
    if hit:
        try:
            await message.delete()
        except Exception:
            pass
