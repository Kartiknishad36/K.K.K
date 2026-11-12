from functools import wraps
from pyrogram import Client
from pyrogram.types import Message
import config


def owner_only(func):
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        if message.from_user and message.from_user.id == config.OWNER_ID:
            return await func(client, message)
        await message.reply_text("⛔ This command is only for the owner.")
    return wrapper


def admin_only(func):
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        if not message.from_user:
            return
        # Owner always allowed
        if message.from_user.id == config.OWNER_ID:
            return await func(client, message)

        if message.chat.type in ["group", "supergroup"]:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in ["administrator", "creator"]:
                return await func(client, message)

        await message.reply_text("⛔ You need to be an admin to use this command.")
    return wrapper


def group_only(func):
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        if message.chat.type in ["group", "supergroup"]:
            return await func(client, message)
        await message.reply_text("⛔ This command can only be used in groups.")
    return wrapper
