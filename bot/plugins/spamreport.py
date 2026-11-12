"""
Spam Report + Advanced Ban System
"""

from pyrogram import Client, filters
from pyrogram.types import Message
import config
from bot.database import db

REPORTS = {}


@Client.on_message(filters.command("report", prefixes=config.COMMAND_PREFIX) & filters.me)
async def report_spam(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.edit_text("Reply to a spam message to report the user.")
        return

    spammer = message.reply_to_message.from_user
    reporter_id = config.OWNER_ID

    if spammer.id == config.OWNER_ID:
        await message.edit_text("You can't report yourself.")
        return

    if spammer.id not in REPORTS:
        REPORTS[spammer.id] = []

    if reporter_id in REPORTS[spammer.id]:
        await message.edit_text("You already reported this user.")
        return

    REPORTS[spammer.id].append(reporter_id)
    count = len(REPORTS[spammer.id])

    reason = " ".join(message.command[1:]) if len(message.command) > 1 else "Spam report"
    warnings = await db.add_warning(spammer.id, message.chat.id)

    text = (
        f"🚩 **User Reported**\n\n"
        f"**User:** {spammer.mention}\n"
        f"**ID:** `{spammer.id}`\n"
        f"**Reports:** `{count}`\n"
        f"**Warnings:** `{warnings}`\n"
        f"**Reason:** {reason}"
    )

    if count >= 3 or warnings >= config.ANTISPAM_WARN_LIMIT:
        try:
            await client.ban_chat_member(message.chat.id, spammer.id)
            await db.gban_user(spammer.id, f"Auto-ban after {count} reports", config.OWNER_ID)
            text += f"\n\n🔨 **Auto-banned**"
        except Exception as e:
            text += f"\n\n⚠️ Could not ban: `{e}`"

    await message.edit_text(text)


@Client.on_message(filters.command("reports", prefixes=config.COMMAND_PREFIX) & filters.me)
async def list_reports(client: Client, message: Message):
    if not REPORTS:
        await message.edit_text("No active reports.")
        return

    text = "**🚩 Active Spam Reports:**\n\n"
    for uid, reporters in REPORTS.items():
        try:
            user = await client.get_users(uid)
            name = user.first_name
        except Exception:
            name = str(uid)
        text += f"• **{name}** (`{uid}`) — `{len(reporters)}` reports\n"

    await message.edit_text(text)


@Client.on_message(filters.command("clearreports", prefixes=config.COMMAND_PREFIX) & filters.me)
async def clear_reports(client: Client, message: Message):
    user = None
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            user = await client.get_users(message.command[1])
        except Exception:
            pass

    if not user:
        await message.edit_text("Reply to user or give ID/username.")
        return

    if user.id in REPORTS:
        del REPORTS[user.id]
        await db.reset_warnings(user.id, message.chat.id)
        await message.edit_text(f"✅ Reports & warnings cleared for {user.mention}")
    else:
        await message.edit_text("No reports found for this user.")
