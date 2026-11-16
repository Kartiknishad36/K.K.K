"""Zombies — find & clean deleted accounts"""
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from bot.client import app
import config

P = config.COMMAND_PREFIX

async def out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["zombies", "deleted"], prefixes=P))
async def zombies_cmd(client, message: Message):
    if not message.chat or message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await out(message, "❌ Sirf group me.")
        return
    status = await out(message, "🧹 Scanning deleted accounts...")
    deleted = []
    try:
        async for m in client.get_chat_members(message.chat.id):
            u = m.user
            if u and getattr(u, "is_deleted", False):
                deleted.append(u.id)
    except Exception as e:
        await status.edit_text(f"❌ `{e}`")
        return
    if not deleted:
        await status.edit_text("✅ No deleted accounts found.")
        return
    if len(message.command) > 1 and message.command[1].lower() == "clean":
        ok = fail = 0
        for uid in deleted:
            try:
                await client.ban_chat_member(message.chat.id, uid)
                await client.unban_chat_member(message.chat.id, uid)
                ok += 1
            except Exception:
                fail += 1
            await asyncio.sleep(0.4)
        await status.edit_text(f"🧹 Cleaned `{ok}` deleted | fail `{fail}`")
    else:
        await status.edit_text(f"👻 Found **{len(deleted)}** deleted accounts.\nClean: `{P}zombies clean`")
