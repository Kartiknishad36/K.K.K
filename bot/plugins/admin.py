from pyrogram import Client, filters
from bot.client import app
from pyrogram.types import Message, ChatPermissions
import config

try:
    from bot.helpers.tools import extract_user_and_reason
except Exception:
    async def extract_user_and_reason(client, message):
        if message.reply_to_message and message.reply_to_message.from_user:
            return message.reply_to_message.from_user, " ".join(message.command[1:]) if len(message.command) > 1 else "No reason"
        if len(message.command) > 1:
            try:
                u = await client.get_users(message.command[1])
                return u, " ".join(message.command[2:]) if len(message.command) > 2 else "No reason"
            except Exception:
                return None, None
        return None, None

try:
    from bot.database import db
except Exception:
    db = None


async def _out(message, text):
    try:
        await message.edit_text(text)
    except Exception:
        try:
            await message.reply_text(text)
        except Exception:
            pass


@app.on_message(filters.command("ban", prefixes=config.COMMAND_PREFIX))
async def ban_user(client: Client, message: Message):
    user, reason = await extract_user_and_reason(client, message)
    if not user:
        return await _out(message, "Reply / username do.")
    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await _out(message, f"🔨 **Banned** {user.mention}\n**Reason:** {reason}")
    except Exception as e:
        await _out(message, f"❌ `{e}`")


@app.on_message(filters.command("unban", prefixes=config.COMMAND_PREFIX))
async def unban_user(client: Client, message: Message):
    user, _ = await extract_user_and_reason(client, message)
    if not user:
        return await _out(message, "Reply / username do.")
    try:
        await client.unban_chat_member(message.chat.id, user.id)
        await _out(message, f"✅ **Unbanned** {user.mention}")
    except Exception as e:
        await _out(message, f"❌ `{e}`")


@app.on_message(filters.command("kick", prefixes=config.COMMAND_PREFIX))
async def kick_user(client: Client, message: Message):
    user, reason = await extract_user_and_reason(client, message)
    if not user:
        return await _out(message, "Reply / username do.")
    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await client.unban_chat_member(message.chat.id, user.id)
        await _out(message, f"👢 **Kicked** {user.mention}\n**Reason:** {reason}")
    except Exception as e:
        await _out(message, f"❌ `{e}`")


@app.on_message(filters.command("mute", prefixes=config.COMMAND_PREFIX))
async def mute_user(client: Client, message: Message):
    user, reason = await extract_user_and_reason(client, message)
    if not user:
        return await _out(message, "Reply / username do.")
    try:
        await client.restrict_chat_member(message.chat.id, user.id, ChatPermissions(can_send_messages=False))
        await _out(message, f"🔇 **Muted** {user.mention}\n**Reason:** {reason}")
    except Exception as e:
        await _out(message, f"❌ `{e}`")


@app.on_message(filters.command("unmute", prefixes=config.COMMAND_PREFIX))
async def unmute_user(client: Client, message: Message):
    user, _ = await extract_user_and_reason(client, message)
    if not user:
        return await _out(message, "Reply / username do.")
    try:
        await client.restrict_chat_member(
            message.chat.id, user.id,
            ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True),
        )
        await _out(message, f"🔊 **Unmuted** {user.mention}")
    except Exception as e:
        await _out(message, f"❌ `{e}`")


@app.on_message(filters.command("promote", prefixes=config.COMMAND_PREFIX))
async def promote_user(client: Client, message: Message):
    user, _ = await extract_user_and_reason(client, message)
    if not user:
        return await _out(message, "Reply / username do.")
    try:
        await client.promote_chat_member(
            message.chat.id, user.id,
            can_manage_chat=True, can_delete_messages=True, can_restrict_members=True,
            can_invite_users=True, can_pin_messages=True,
        )
        await _out(message, f"⬆️ **Promoted** {user.mention}")
    except Exception as e:
        await _out(message, f"❌ `{e}`")


@app.on_message(filters.command("demote", prefixes=config.COMMAND_PREFIX))
async def demote_user(client: Client, message: Message):
    user, _ = await extract_user_and_reason(client, message)
    if not user:
        return await _out(message, "Reply / username do.")
    try:
        await client.promote_chat_member(
            message.chat.id, user.id,
            can_manage_chat=False, can_delete_messages=False, can_restrict_members=False,
            can_invite_users=False, can_pin_messages=False,
        )
        await _out(message, f"⬇️ **Demoted** {user.mention}")
    except Exception as e:
        await _out(message, f"❌ `{e}`")


@app.on_message(filters.command("pin", prefixes=config.COMMAND_PREFIX))
async def pin_message(client: Client, message: Message):
    if not message.reply_to_message:
        return await _out(message, "Reply to a message to pin.")
    try:
        await message.reply_to_message.pin(disable_notification=False)
        await _out(message, "📌 Pinned.")
    except Exception as e:
        await _out(message, f"❌ `{e}`")


@app.on_message(filters.command("unpin", prefixes=config.COMMAND_PREFIX))
async def unpin_message(client: Client, message: Message):
    try:
        if message.reply_to_message:
            await message.reply_to_message.unpin()
        else:
            await client.unpin_chat_message(message.chat.id)
        await _out(message, "📌 Unpinned.")
    except Exception as e:
        await _out(message, f"❌ `{e}`")


@app.on_message(filters.command("purge", prefixes=config.COMMAND_PREFIX))
async def purge_messages(client: Client, message: Message):
    if not message.reply_to_message:
        return await _out(message, "Reply to start message for purge.")
    try:
        start_id = message.reply_to_message.id
        end_id = message.id
        ids = list(range(start_id, end_id))
        for i in range(0, len(ids), 100):
            await client.delete_messages(message.chat.id, ids[i:i+100])
        try:
            await message.delete()
        except Exception:
            pass
    except Exception as e:
        await _out(message, f"❌ Purge failed: `{e}`")


@app.on_message(filters.command("gban", prefixes=config.COMMAND_PREFIX))
async def gban_user(client: Client, message: Message):
    user, reason = await extract_user_and_reason(client, message)
    if not user:
        return await _out(message, "Reply / username do.")
    if user.id == config.OWNER_ID:
        return await _out(message, "Can't gban owner.")
    if db:
        try:
            await db.gban_user(user.id, reason, config.OWNER_ID)
        except Exception:
            pass
    await _out(message, f"🌍 **GBanned** {user.mention}\n**Reason:** {reason}")


@app.on_message(filters.command("ungban", prefixes=config.COMMAND_PREFIX))
async def ungban_user(client: Client, message: Message):
    user, _ = await extract_user_and_reason(client, message)
    if not user:
        return await _out(message, "Reply / username do.")
    if db:
        try:
            await db.ungban_user(user.id)
        except Exception:
            pass
    await _out(message, f"✅ GBan removed for {user.mention}")
