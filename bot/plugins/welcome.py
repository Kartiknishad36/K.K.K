from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus
import config
from bot.database import db


@Client.on_message(filters.command("setwelcome", prefixes=config.COMMAND_PREFIX) & filters.me)
async def set_welcome(client: Client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.edit_text(
            f"Usage: `{config.COMMAND_PREFIX}setwelcome <message>`\n\n"
            "Variables you can use:\n"
            "• `{mention}` - Mentions the user\n"
            "• `{name}` - User's first name\n"
            "• `{id}` - User ID\n"
            "• `{chat}` - Chat title"
        )
        return

    if message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption or ""
    else:
        text = message.text.split(None, 1)[1]

    await db.set_welcome(message.chat.id, text, enabled=True)
    await message.edit_text("✅ Welcome message set successfully!")


@Client.on_message(filters.command("welcome", prefixes=config.COMMAND_PREFIX) & filters.me)
async def toggle_welcome(client: Client, message: Message):
    data = await db.get_welcome(message.chat.id)

    if not data:
        # Set default
        await db.set_welcome(message.chat.id, config.WELCOME_DEFAULT, enabled=True)
        await message.edit_text("✅ Welcome enabled with default message.")
        return

    new_state = not bool(data["enabled"])
    await db.toggle_welcome(message.chat.id, new_state)
    status = "enabled" if new_state else "disabled"
    await message.edit_text(f"✅ Welcome messages **{status}**.")


@Client.on_chat_member_updated()
async def welcome_new_member(client: Client, update: ChatMemberUpdated):
    if not config.ENABLE_WELCOME:
        return

    # Only care about new joins
    old = update.old_chat_member
    new = update.new_chat_member

    if not new or not new.user:
        return

    # User joined
    if (old is None or old.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED]) and \
       new.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED]:

        chat_id = update.chat.id
        data = await db.get_welcome(chat_id)

        if not data or not data["enabled"]:
            return

        user = new.user
        msg = data["message"] or config.WELCOME_DEFAULT

        # Replace variables
        msg = msg.replace("{mention}", user.mention)
        msg = msg.replace("{name}", user.first_name or "User")
        msg = msg.replace("{id}", str(user.id))
        msg = msg.replace("{chat}", update.chat.title or "the group")

        try:
            await client.send_message(chat_id, msg)
        except Exception:
            pass
