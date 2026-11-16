from pyrogram import filters
from bot.client import app
from pyrogram.types import Message, ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus
import config

WELCOME_STATE = {}
WELCOME_TEXT = {}


@app.on_message(filters.command(["setwelcome"], prefixes=config.COMMAND_PREFIX))
async def set_welcome(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text(f"Usage: `{config.COMMAND_PREFIX}setwelcome <msg>`")
        return
    text = message.text.split(None, 1)[1]
    WELCOME_TEXT[message.chat.id] = text
    WELCOME_STATE[message.chat.id] = True
    await message.reply_text("✅ Welcome message set & ON")


@app.on_message(filters.command(["welcome"], prefixes=config.COMMAND_PREFIX))
async def toggle_welcome(client, message: Message):
    chat_id = message.chat.id
    WELCOME_STATE[chat_id] = not WELCOME_STATE.get(chat_id, False)
    await message.reply_text(f"Welcome: {'ON' if WELCOME_STATE[chat_id] else 'OFF'}")


@app.on_chat_member_updated()
async def welcome_member(client, update: ChatMemberUpdated):
    try:
        if not update.new_chat_member or not update.new_chat_member.user:
            return
        if update.new_chat_member.status not in (ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED):
            return
        if update.old_chat_member and update.old_chat_member.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            return
        chat_id = update.chat.id
        if not WELCOME_STATE.get(chat_id, getattr(config, 'ENABLE_WELCOME', True)):
            return
        user = update.new_chat_member.user
        tmpl = WELCOME_TEXT.get(chat_id) or getattr(config, 'WELCOME_DEFAULT', '👋 Welcome {mention} to **{chat}**!')
        text = tmpl.format(
            mention=user.mention,
            name=user.first_name or 'User',
            id=user.id,
            chat=update.chat.title or 'chat',
        )
        await client.send_message(chat_id, text)
    except Exception:
        pass
