from datetime import datetime, timedelta
from typing import Optional, Tuple
from pyrogram import Client
from pyrogram.types import Message, User


async def get_user(client: Client, message: Message) -> Optional[User]:
    """Extract user from reply or mention."""
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user

    if message.entities:
        for entity in message.entities:
            if entity.type.name == "TEXT_MENTION" and entity.user:
                return entity.user
            if entity.type.name == "MENTION":
                username = message.text[entity.offset:entity.offset + entity.length]
                try:
                    return await client.get_users(username)
                except Exception:
                    pass
    return None


async def extract_user_and_reason(client: Client, message: Message) -> Tuple[Optional[User], str]:
    """Extract target user and reason from command."""
    user = None
    reason = "No reason provided"

    # Reply case
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
        args = message.text.split(None, 1)
        if len(args) > 1:
            reason = args[1]
        return user, reason

    # Command with argument
    args = message.text.split(None, 2)
    if len(args) < 2:
        return None, reason

    try:
        user = await client.get_users(args[1])
    except Exception:
        return None, reason

    if len(args) > 2:
        reason = args[2]

    return user, reason


def time_formatter(seconds: int) -> str:
    """Convert seconds to human readable time."""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)


def humanize_time(dt_string: str) -> str:
    """Convert ISO datetime string to human readable relative time."""
    try:
        dt = datetime.fromisoformat(dt_string)
        now = datetime.utcnow()
        diff = now - dt

        seconds = int(diff.total_seconds())
        if seconds < 60:
            return f"{seconds} seconds ago"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes} minutes ago"
        hours = minutes // 60
        if hours < 24:
            return f"{hours} hours ago"
        days = hours // 24
        return f"{days} days ago"
    except Exception:
        return dt_string
