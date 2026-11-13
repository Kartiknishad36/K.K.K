from pyrogram import Client, filters
from bot.client import app
from pyrogram.types import Message, ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus
import config
from bot.database import db


@app.on_message(filters.command("setwelcome", prefixes=config.COMMAND_PREFIX) & filters.me)
async def set_welcome(client: Client, message: Message):
    text = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    if not text and message.reply_to_message:
        text = message.reply_to_message.text or ""
    if not text:
        await message.edit_text(
            f"Usage: `{config.COMMAND_PREFIX}setwelcome Welcome {{mention}} to {{chat}}!`\n"
            f"Vars: {{mention}} {{name}} {{id}} {{chat}}"
        )
        return
    await db.set_welcome(message.chat.id, text, enabled=True)
    await message.edit_text("✅ Welcome message set.")


@app.on_message(filters.command("welcome", prefixes=config.COMMAND_PREFIX) & filters.me)
async def toggle_welcome(client: Client, message: Message):
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    data = await db.get_welcome(message.chat.id)
    if arg in ("on", "off"):
        enabled = arg == "on"
        if data:
            await db.toggle_welcome(message.chat.id, enabled)
        else:
            await db.set_welcome(message.chat.id, config.WELCOME_DEFAULT, enabled=enabled)
        await message.edit_text(f"Welcome **{'ON' if enabled else 'OFF'}**")
        return
    if data:
        state = "ON" if data.get("enabled") else "OFF"
        await message.edit_text(f"Welcome is **{state}**\n`{data.get('message')}`")
    else:
        await message.edit_text("No welcome set. Use setwelcome.")


@app.on_chat_member_updated()
async def welcome_handler(client: Client, update: ChatMemberUpdated):
    if not config.ENABLE_WELCOME:
        return
    if not update.new_chat_member or not update.new_chat_member.user:
        return
    user = update.new_chat_member.user
    if user.is_bot:
        return
    old = update.old_chat_member.status if update.old_chat_member else None
    new = update.new_chat_member.status
    if new not in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR):
        return
    if old not in (None, ChatMemberStatus.LEFT, ChatMemberStatus.BANNED):
        return
    data = await db.get_welcome(update.chat.id)
    if not data or not data.get("enabled"):
        return
    tpl = data.get("message") or config.WELCOME_DEFAULT
    name = user.first_name or "User"
    mention = f"[{name}](tg://user?id={user.id})"
    text = (
        tpl.replace("{mention}", mention)
        .replace("{name}", name)
        .replace("{id}", str(user.id))
        .replace("{chat}", update.chat.title or "Group")
    )
    try:
        await client.send_message(update.chat.id, text)
    except Exception:
        pass
