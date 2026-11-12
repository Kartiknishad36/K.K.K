"""
TagAll Plugin
  .tagall <message>     - Tag all members (in batches)
  .tag <message>        - Tag members one by one (slower, safer)
  .tagadmin <message>   - Tag all admins only
"""

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMembersFilter
import config


RUNNING = set()


@Client.on_message(filters.command("tagall", prefixes=config.COMMAND_PREFIX) & filters.me)
async def tag_all(client: Client, message: Message):
    """Tag all group members in batches of 5."""
    if message.chat.type.name not in ["GROUP", "SUPERGROUP"]:
        await message.edit_text("Ye command sirf groups me kaam karti hai.")
        return

    chat_id = message.chat.id
    if chat_id in RUNNING:
        await message.edit_text("⚠️ TagAll pehle se chal raha hai is group me.")
        return

    text = " ".join(message.command[1:]) if len(message.command) > 1 else "Hello!"
    if message.reply_to_message and not text.strip():
        text = message.reply_to_message.text or message.reply_to_message.caption or "Hello!"

    RUNNING.add(chat_id)
    status = await message.edit_text("🔄 Members collect kar raha hoon...")

    try:
        members = []
        async for member in client.get_chat_members(chat_id):
            user = member.user
            if user and not user.is_bot and not user.is_deleted:
                members.append(user)

        if not members:
            await status.edit_text("Koi member nahi mila.")
            return

        await status.edit_text(f"📢 Tagging **{len(members)}** members...")

        batch_size = 5
        for i in range(0, len(members), batch_size):
            batch = members[i:i + batch_size]
            mentions = " ".join(u.mention for u in batch)
            try:
                await client.send_message(chat_id, f"{mentions}\n\n{text}")
            except Exception:
                pass
            await asyncio.sleep(1.5)

        await status.edit_text(f"✅ **TagAll Complete**\nTagged: `{len(members)}` members")
    except Exception as e:
        await status.edit_text(f"❌ Error: `{e}`")
    finally:
        RUNNING.discard(chat_id)


@Client.on_message(filters.command("tag", prefixes=config.COMMAND_PREFIX) & filters.me)
async def tag_one_by_one(client: Client, message: Message):
    """Tag members one by one (safer, slower)."""
    if message.chat.type.name not in ["GROUP", "SUPERGROUP"]:
        await message.edit_text("Ye command sirf groups me kaam karti hai.")
        return

    chat_id = message.chat.id
    if chat_id in RUNNING:
        await message.edit_text("⚠️ Tag process pehle se chal raha hai is group me.")
        return

    text = " ".join(message.command[1:]) if len(message.command) > 1 else "Hello!"
    if message.reply_to_message and not text.strip():
        text = message.reply_to_message.text or message.reply_to_message.caption or "Hello!"

    RUNNING.add(chat_id)
    status = await message.edit_text("🔄 Members collect kar raha hoon...")

    try:
        members = []
        async for member in client.get_chat_members(chat_id):
            user = member.user
            if user and not user.is_bot and not user.is_deleted:
                members.append(user)

        if not members:
            await status.edit_text("Koi member nahi mila.")
            return

        await status.edit_text(f"📢 One-by-one tagging **{len(members)}** members...")

        count = 0
        for user in members:
            try:
                await client.send_message(chat_id, f"{user.mention}\n\n{text}")
                count += 1
            except Exception:
                pass
            await asyncio.sleep(2.0)

        await status.edit_text(f"✅ **Tag Complete**\nTagged: `{count}` members")
    except Exception as e:
        await status.edit_text(f"❌ Error: `{e}`")
    finally:
        RUNNING.discard(chat_id)


@Client.on_message(filters.command("tagadmin", prefixes=config.COMMAND_PREFIX) & filters.me)
async def tag_admins(client: Client, message: Message):
    """Tag all adm intensest group."""
    if message.chat.type.name not in ["GROUP", "SUPERGROUP"]:
        await message.edit_text("Ye command sirf groups me kaam karti hai.")
        return

    chat_id = message.chat.id
    if chat_id in RUNNING:
        await message.edit_text("⚠️ Tag process pehle se chal raha hai is group me.")
        return

    text = " ".join(message.command[1:]) if len(message.command) > 1 else "Admin attention!"
    if message.reply_to_message and not text.strip():
        text = message.reply_to_message.text or message.reply_to_message.caption or "Admin attention!"

    RUNNING.add(chat_id)
    status = await message.edit_text("🔄 Admins collect kar raha hoon...")

    try:
        admins = []
        async for member in client.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
            user = member.user
            if user and not user.is_bot and not user.is_deleted:
                admins.append(user)

        if not admins:
            await status.edit_text("Koi admin nahi mila.")
            return

        mentions = " ".join(u.mention for u in admins)
        await client.send_message(chat_id, f"**Admins:**\n{mentions}\n\n{text}")

        await status.edit_text(f"✅ **TagAdmin Complete**\nTagged: `{len(admins)}` admins")
    except Exception as e:
        await status.edit_text(f"❌ Error: `{e}`")
    finally:
        RUNNING.discard(chat_id)
