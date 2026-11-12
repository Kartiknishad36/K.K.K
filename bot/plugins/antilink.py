"""Anti-Link + Anti-Bot"""
import re
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus
import config
from bot.database import db

_LINK_RE = re.compile(r"(?i)(https?://|www\.|t\.me/|telegram\.me/|tg://)\S+")

@Client.on_message(filters.command("antilink", prefixes=config.COMMAND_PREFIX) & filters.me)
async def antilink_toggle(client: Client, message: Message):
    if message.chat.type.name not in ["GROUP", "SUPERGROUP"]:
        await message.edit_text("Sirf groups me."); return
    chat_id = message.chat.id
    if len(message.command) < 2:
        on = await db.get_chat_flag(chat_id, "antilink", False)
        await message.edit_text(f"🔗 AntiLink: **{'ON' if on else 'OFF'}**\n`{config.COMMAND_PREFIX}antilink on|off|status`"); return
    arg = message.command[1].lower()
    if arg in ("on", "1", "enable"):
        await db.set_chat_flag(chat_id, "antilink", True)
        await message.edit_text("✅ AntiLink **ON**")
    elif arg in ("off", "0", "disable"):
        await db.set_chat_flag(chat_id, "antilink", False)
        await message.edit_text("❌ AntiLink **OFF**")
    else:
        on = await db.get_chat_flag(chat_id, "antilink", False)
        await message.edit_text(f"AntiLink: **{'ON' if on else 'OFF'}**")

@Client.on_message(filters.command("antibot", prefixes=config.COMMAND_PREFIX) & filters.me)
async def antibot_toggle(client: Client, message: Message):
    if message.chat.type.name not in ["GROUP", "SUPERGROUP"]:
        await message.edit_text("Sirf groups me."); return
    chat_id = message.chat.id
    if len(message.command) < 2:
        on = await db.get_chat_flag(chat_id, "antibot", False)
        await message.edit_text(f"🤖 AntiBot: **{'ON' if on else 'OFF'}**\n`{config.COMMAND_PREFIX}antibot on|off`"); return
    arg = message.command[1].lower()
    if arg in ("on", "1", "enable"):
        await db.set_chat_flag(chat_id, "antibot", True)
        await message.edit_text("✅ AntiBot **ON**")
    elif arg in ("off", "0", "disable"):
        await db.set_chat_flag(chat_id, "antibot", False)
        await message.edit_text("❌ AntiBot **OFF**")
    else:
        await message.edit_text(f"Usage: `{config.COMMAND_PREFIX}antibot on|off`")

@Client.on_message(filters.group & filters.incoming & ~filters.me & ~filters.service, group=6)
async def antilink_watch(client: Client, message: Message):
    if not message.from_user or message.from_user.id == config.OWNER_ID: return
    if not await db.get_chat_flag(message.chat.id, "antilink", False): return
    text = message.text or message.caption or ""
    has_link = bool(_LINK_RE.search(text))
    for e in list(message.entities or []) + list(message.caption_entities or []):
        if e.type.name in ("URL", "TEXT_LINK"): has_link = True; break
    if not has_link: return
    try:
        await message.delete()
        await client.send_message(message.chat.id, f"🔗 Link deleted — {message.from_user.mention}")
    except Exception: pass

@Client.on_chat_member_updated()
async def antibot_join(client: Client, update: ChatMemberUpdated):
    chat = update.chat
    if not chat or not await db.get_chat_flag(chat.id, "antibot", False): return
    new, old = update.new_chat_member, update.old_chat_member
    if not new or not new.user or not new.user.is_bot: return
    was_out = (not old) or old.status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED)
    now_in = new.status not in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED)
    if not (was_out and now_in): return
    try:
        me = await client.get_me()
        if new.user.id == me.id: return
    except Exception: pass
    try:
        await client.ban_chat_member(chat.id, new.user.id)
        await client.unban_chat_member(chat.id, new.user.id)
        await client.send_message(chat.id, f"🤖 Bot {new.user.mention} removed (AntiBot).")
    except Exception:
        try: await client.ban_chat_member(chat.id, new.user.id)
        except Exception: pass
