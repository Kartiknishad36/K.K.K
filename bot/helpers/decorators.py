from functools import wraps

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatType, ChatMemberStatus

import config


def owner_only(func):
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        uid = message.from_user.id if message.from_user else 0
        if message.outgoing or (config.OWNER_ID and uid == config.OWNER_ID):
            return await func(client, message)
        await message.reply_text("⛔ This command is only for the owner.")
    return wrapper


def admin_only(func):
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        if not message.from_user:
            return
        if message.outgoing or (config.OWNER_ID and message.from_user.id == config.OWNER_ID):
            return await func(client, message)

        if message.chat and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
            try:
                member = await client.get_chat_member(message.chat.id, message.from_user.id)
                if member.status in (
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.OWNER,
                ):
                    return await func(client, message)
            except Exception:
                pass

        await message.reply_text("⛔ You need to be an admin to use this command.")
    return wrapper


def group_only(func):
    @wraps(func)
    async def wrapper(client: Client, message: Message):
        if message.chat and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
            return await func(client, message)
        await message.reply_text("⛔ This command can only be used in groups.")
    return wrapper
