import re
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message
import config
from bot.database import db
from bot.helpers.tools import time_formatter


def parse_time(time_str: str):
    """Parse relative time like 10m, 2h, 1d or absolute datetime."""
    time_str = time_str.strip().lower()

    # Relative: 30s, 10m, 2h, 1d
    match = re.match(r"^(\d+)(s|m|h|d)$", time_str)
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        delta = {
            "s": timedelta(seconds=value),
            "m": timedelta(minutes=value),
            "h": timedelta(hours=value),
            "d": timedelta(days=value),
        }[unit]
        return datetime.utcnow() + delta

    # Absolute: 2026-11-13 15:30
    try:
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    except ValueError:
        pass

    try:
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass

    return None


@Client.on_message(filters.command("schedule", prefixes=config.COMMAND_PREFIX) & filters.me)
async def schedule_message(client: Client, message: Message):
    if len(message.command) < 3:
        await message.edit_text(
            f"**Usage:**\n"
            f"`{config.COMMAND_PREFIX}schedule <time> <message>`\n\n"
            f"**Examples:**\n"
            f"`{config.COMMAND_PREFIX}schedule 10m Hello after 10 minutes`\n"
            f"`{config.COMMAND_PREFIX}schedule 2h Meeting reminder`\n"
            f"`{config.COMMAND_PREFIX}schedule 2026-11-13 18:00 Happy Birthday!`"
        )
        return

    time_str = message.command[1]
    msg_text = " ".join(message.command[2:])

    run_at = parse_time(time_str)
    if not run_at:
        await message.edit_text(
            "❌ Invalid time format.\nUse `10m`, `2h`, `1d` or `YYYY-MM-DD HH:MM`"
        )
        return

    if run_at <= datetime.utcnow():
        await message.edit_text("❌ Time must be in the future.")
        return

    schedule_id = await db.add_schedule(
        chat_id=message.chat.id,
        user_id=config.OWNER_ID,
        message=msg_text,
        run_at=run_at.isoformat()
    )

    delta = run_at - datetime.utcnow()
    human = time_formatter(int(delta.total_seconds()))

    await message.edit_text(
        f"✅ **Message Scheduled!**\n\n"
        f"**ID:** `{schedule_id}`\n"
        f"**In:** {human}\n"
        f"**At:** `{run_at.strftime('%Y-%m-%d %H:%M')} UTC`\n"
        f"**Message:** {msg_text[:100]}{'...' if len(msg_text) > 100 else ''}"
    )


@Client.on_message(filters.command("schedules", prefixes=config.COMMAND_PREFIX) & filters.me)
async def list_schedules(client: Client, message: Message):
    schedules = await db.list_schedules(config.OWNER_ID)

    if not schedules:
        await message.edit_text("No pending scheduled messages.")
        return

    text = "**⏰ Pending Schedules:**\n\n"
    for s in schedules:
        run_at = datetime.fromisoformat(s["run_at"])
        text += (
            f"**ID:** `{s['id']}`\n"
            f"**At:** `{run_at.strftime('%Y-%m-%d %H:%M')} UTC`\n"
            f"**Msg:** {s['message'][:60]}{'...' if len(s['message']) > 60 else ''}\n\n"
        )

    await message.edit_text(text)


@Client.on_message(filters.command("delschedule", prefixes=config.COMMAND_PREFIX) & filters.me)
async def delete_schedule(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit_text(f"Usage: `{config.COMMAND_PREFIX}delschedule <id>`")
        return

    try:
        schedule_id = int(message.command[1])
    except ValueError:
        await message.edit_text("ID must be a number.")
        return

    deleted = await db.delete_schedule(schedule_id, config.OWNER_ID)
    if deleted:
        await message.edit_text(f"🗑️ Schedule `{schedule_id}` deleted.")
    else:
        await message.edit_text("❌ Schedule not found or already executed.")
