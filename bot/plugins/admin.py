from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import UserAdminInvalid, ChatAdminRequired, RightForbidden
import config
from bot.helpers import group_only
from bot.helpers.tools import extract_user_and_reason
from bot.database import db


@Client.on_message(filters.command("ban", prefixes=config.COMMAND_PREFIX) & filters.me)
@group_only
async def ban_user(client: Client, message: Message):
    user, reason = await extract_user_and_reason(client, message)
    if not user:
        await message.edit_text("Reply to a user or provide username/ID.")
        return

    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await message.edit_text(
            f"🔨 **Banned** {user.mention}\n**Reason:** {reason}"
        )
    except (UserAdminInvalid, ChatAdminRequired, RightForbidden) as e:
        await message.edit_text(f"❌ Failed: `{e}`")
    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")


@Client.on_message(filters.command("unban", prefixes=config.COMMAND_PREFIX) & filters.me)
@group_only
async def unban_user(client: Client, message: Message):
    user, _ = await extract_user_and_reason(client, message)
    if not user:
        await message.edit_text("Reply to a user or provide username/ID.")
        return

    try:
        await client.unban_chat_member(message.chat.id, user.id)
        await message.edit_text(f"✅ **Unbanned** {user.mention}")
    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")


@Client.on_message(filters.command("kick", prefixes=config.COMMAND_PREFIX) & filters.me)
@group_only
async def kick_user(client: Client, message: Message):
    user, reason = await extract_user_and_reason(client, message)
    if not user:
        await message.edit_text("Reply to a user or provide username/ID.")
        return

    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await client.unban_chat_member(message.chat.id, user.id)
        await message.edit_text(f"👢 **Kicked** {user.mention}\n**Reason:** {reason}")
    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")


@Client.on_message(filters.command("mute", prefixes=config.COMMAND_PREFIX) & filters.me)
@group_only
async def mute_user(client: Client, message: Message):
    user, reason = await extract_user_and_reason(client, message)
    if not user:
        await message.edit_text("Reply to a user or provide username/ID.")
        return

    try:
        permissions = ChatPermissions(can_send_messages=False)
        await client.restrict_chat_member(message.chat.id, user.id, permissions)
        await message.edit_text(f"🔇 **Muted** {user.mention}\n**Reason:** {reason}")
    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")


@Client.on_message(filters.command("unmute", prefixes=config.COMMAND_PREFIX) & filters.me)
@group_only
async def unmute_user(client: Client, message: Message):
    user, _ = await extract_user_and_reason(client, message)
    if not user:
        await message.edit_text("Reply to a user or provide username/ID.")
        return

    try:
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        )
        await client.restrict_chat_member(message.chat.id, user.id, permissions)
        await message.edit_text(f"🔊 **Unmuted** {user.mention}")
    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")


@Client.on_message(filters.command("promote", prefixes=config.COMMAND_PREFIX) & filters.me)
@group_only
async def promote_user(client: Client, message: Message):
    user, _ = await extract_user_and_reason(client, message)
    if not user:
        await message.edit_text("Reply to a user or provide username/ID.")
        return

    try:
        await client.promote_chat_member(
            message.chat.id,
            user.id,
            can_manage_chat=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_restrict_members=True,
            can_promote_members=False,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True,
        )
        await message.edit_text(f"⬆️ **Promoted** {user.mention}")
    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")


@Client.on_message(filters.command("demote", prefixes=config.COMMAND_PREFIX) & filters.me)
@group_only
async def demote_user(client: Client, message: Message):
    user, _ = await extract_user_and_reason(client, message)
    if not user:
        await message.edit_text("Reply to a user or provide username/ID.")
        return

    try:
        await client.promote_chat_member(
            message.chat.id,
            user.id,
            can_manage_chat=False,
            can_delete_messages=False,
            can_manage_video_chats=False,
            can_restrict_members=False,
            can_promote_members=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False,
        )
        await message.edit_text(f"⬇️ **Demoted** {user.mention}")
    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")


@Client.on_message(filters.command("pin", prefixes=config.COMMAND_PREFIX) & filters.me)
async def pin_message(client: Client, message: Message):
    if not message.reply_to_message:
        await message.edit_text("Reply to a message to pin it.")
        return
    try:
        await message.reply_to_message.pin(disable_notification=False)
        await message.edit_text("📌 Message pinned.")
    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")


@Client.on_message(filters.command("unpin", prefixes=config.COMMAND_PREFIX) & filters.me)
async def unpin_message(client: Client, message: Message):
    try:
        if message.reply_to_message:
            await message.reply_to_message.unpin()
        else:
            await client.unpin_chat_message(message.chat.id)
        await message.edit_text("📌 Message unpinned.")
    except Exception as e:
        await message.edit_text(f"❌ Error: `{e}`")


@Client.on_message(filters.command("purge", prefixes=config.COMMAND_PREFIX) & filters.me)
@group_only
async def purge_messages(client: Client, message: Message):
    if not message.reply_to_message:
        await message.edit_text("Reply to a message from where you want to start purging.")
        return

    try:
        start_id = message.reply_to_message.id
        end_id = message.id
        message_ids = list(range(start_id, end_id))

        # Delete in chunks of 100
        for i in range(0, len(message_ids), 100):
            chunk = message_ids[i:i + 100]
            await client.delete_messages(message.chat.id, chunk)

        await message.delete()
    except Exception as e:
        await message.edit_text(f"❌ Purge failed: `{e}`")


@Client.on_message(filters.command("gban", prefixes=config.COMMAND_PREFIX) & filters.me)
async def gban_user(client: Client, message: Message):
    user, reason = await extract_user_and_reason(client, message)
    if not user:
        await message.edit_text("Reply to a user or provide username/ID.")
        return

    if user.id == config.OWNER_ID:
        await message.edit_text("You can't gban yourself.")
        return

    await db.gban_user(user.id, reason, config.OWNER_ID)
    await message.edit_text(
        f"🌍 **Globally Banned** {user.mention}\n**Reason:** {reason}"
    )


@Client.on_message(filters.command("ungban", prefixes=config.COMMAND_PREFIX) & filters.me)
async def ungban_user(client: Client, message: Message):
    user, _ = await extract_user_and_reason(client, message)
    if not user:
        await message.edit_text("Reply to a user or provide username/ID.")
        return

    success = await db.ungban_user(user.id)
    if success:
        await message.edit_text(f"✅ **Global ban removed** for {user.mention}")
    else:
        await message.edit_text("User was not gbanned.")
