from pyrogram import Client, filters
from pyrogram.types import Message
import config
from bot.database import db

# Simple PM permit system


@Client.on_message(filters.command("approve", prefixes=config.COMMAND_PREFIX) & filters.me)
async def approve_user(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            user = await client.get_users(message.command[1])
        except Exception:
            await message.edit_text("User not found.")
            return
    else:
        await message.edit_text("Reply to a user or give username/ID.")
        return

    await db.approve_user(user.id, config.OWNER_ID)
    await message.edit_text(f"✅ Approved {user.mention}")


@Client.on_message(filters.command("disapprove", prefixes=config.COMMAND_PREFIX) & filters.me)
async def disapprove_user(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            user = await client.get_users(message.command[1])
        except Exception:
            await message.edit_text("User not found.")
            return
    else:
        await message.edit_text("Reply to a user or give username/ID.")
        return

    success = await db.disapprove_user(user.id)
    if success:
        await message.edit_text(f"❌ Disapproved {user.mention}")
    else:
        await message.edit_text("User was not in approved list.")


@Client.on_message(filters.private & ~filters.me & ~filters.bot, group=8)
async def pm_permit_handler(client: Client, message: Message):
    if not message.from_user:
        return

    user_id = message.from_user.id

    # Owner and approved users pass
    if user_id == config.OWNER_ID:
        return
    if await db.is_approved(user_id):
        return

    # Simple warning
    try:
        await message.reply_text(
            "⚠️ **PM Permit**\n\n"
            "You are not approved to message me.\n"
            "Please wait for approval or contact me through other means."
        )
    except Exception:
        pass
