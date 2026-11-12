""".raid / .spam — limited (max 9999999999999) to reduce ban risk"""
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
import config

MAX_COUNT, DELAY = 9999999999999, 0.8
_RAID, _SPAM = {}, {}

def _parse(message):
    if len(message.command) < 2:
        return None, f"Usage: `{config.COMMAND_PREFIX}raid 10 text` | reply + `{config.COMMAND_PREFIX}raid 10`"
    try: count = int(message.command[1])
    except ValueError: return None, "Count number hona chahiye."
    count = max(1, min(count, MAX_COUNT))
    text = ""
    if len(message.command) > 2: text = message.text.split(None, 2)[2]
    elif message.reply_to_message:
        r = message.reply_to_message
        text = r.text or r.caption or ""
        if r.from_user: text = f"{r.from_user.mention} {text}".strip()
    if not text.strip(): return None, "Text do ya reply karke chalao."
    return count, text

async def _runner(client, chat_id, count, text, tag, store):
    try:
        for i in range(count):
            await client.send_message(chat_id, text)
            if i < count - 1: await asyncio.sleep(DELAY)
    except asyncio.CancelledError:
        try: await client.send_message(chat_id, f"⏹ {tag} stopped.")
        except Exception: pass
        raise
    except Exception as e:
        try: await client.send_message(chat_id, f"⏹ {tag} error: `{e}`")
        except Exception: pass
    finally: store.pop(chat_id, None)

@Client.on_message(filters.command("raid", prefixes=config.COMMAND_PREFIX) & filters.me)
async def raid_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    if len(message.command) >= 2 and message.command[1].lower() in ("off", "stop", "cancel"):
        t = _RAID.pop(chat_id, None)
        if t and not t.done(): t.cancel(); await message.edit_text("⏹ Raid **OFF**.")
        else: await message.edit_text("Koi raid nahi chal rahi.")
        return
    if chat_id in _RAID and not _RAID[chat_id].done():
        await message.edit_text(f"Raid already ON. `{config.COMMAND_PREFIX}raid off`"); return
    count, text = _parse(message)
    if count is None: await message.edit_text(text); return
    try: await message.delete()
    except Exception: pass
    _RAID[chat_id] = asyncio.create_task(_runner(client, chat_id, count, text, "Raid", _RAID))
    await client.send_message(chat_id, f"🔥 Raid x{count} started… (max {MAX_COUNT})")

@Client.on_message(filters.command("spam", prefixes=config.COMMAND_PREFIX) & filters.me)
async def spam_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    if len(message.command) >= 2 and message.command[1].lower() in ("off", "stop", "cancel"):
        t = _SPAM.pop(chat_id, None)
        if t and not t.done(): t.cancel(); await message.edit_text("⏹ Spam **OFF**.")
        else: await message.edit_text("Koi spam nahi chal raha.")
        return
    if message.chat.type == ChatType.CHANNEL:
        await message.edit_text("❌ Channel me spam band."); return
    if chat_id in _SPAM and not _SPAM[chat_id].done():
        await message.edit_text(f"Spam already ON. `{config.COMMAND_PREFIX}spam off`"); return
    count, text = _parse(message)
    if count is None: await message.edit_text(text); return
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        extra = message.text.split(None, 2)[2] if len(message.command) > 2 else ""
        text = f"{u.mention} {extra}".strip()
    try: await message.delete()
    except Exception: pass
    _SPAM[chat_id] = asyncio.create_task(_runner(client, chat_id, count, text, "Spam", _SPAM))
