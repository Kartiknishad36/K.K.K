"""
Session Manager - Multiple accounts support
Allows switching between different Telegram sessions.
"""

import os
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message
import config
from bot.client import logger

SESSIONS_DIR = Path("data/sessions")
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def list_sessions() -> list:
    """Return list of available session names."""
    sessions = []
    for f in SESSIONS_DIR.glob("*.session"):
        sessions.append(f.stem)
    # Also check main session
    main_session = Path("data") / f"{config.SESSION_NAME}.session"
    if main_session.exists() and config.SESSION_NAME not in sessions:
        sessions.insert(0, config.SESSION_NAME)
    return sessions


@Client.on_message(filters.command("sessions", prefixes=config.COMMAND_PREFIX) & filters.me)
async def sessions_list(client: Client, message: Message):
    sessions = list_sessions()
    current = config.SESSION_NAME

    if not sessions:
        await message.edit_text("No sessions found.")
        return

    text = "**🔐 Available Sessions:**\n\n"
    for s in sessions:
        mark = "✅" if s == current else "•"
        text += f"{mark} `{s}`\n"

    text += (
        f"\n**Current:** `{current}`\n\n"
        f"`{config.COMMAND_PREFIX}session <name>` - Switch (restart required)\n"
        f"`{config.COMMAND_PREFIX}newsession <name>` - Create new session\n"
        f"`{config.COMMAND_PREFIX}delsession <name>` - Delete session"
    )
    await message.edit_text(text)


@Client.on_message(filters.command("session", prefixes=config.COMMAND_PREFIX) & filters.me)
async def switch_session(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit_text(
            f"Usage: `{config.COMMAND_PREFIX}session <session_name>`\n"
            f"Use `{config.COMMAND_PREFIX}sessions` to list available."
        )
        return

    name = message.command[1].strip()
    sessions = list_sessions()

    if name not in sessions:
        await message.edit_text(
            f"❌ Session `{name}` not found.\n"
            f"Available: {', '.join(f'`{s}`' for s in sessions) or 'None'}"
        )
        return

    # Update .env file
    env_path = Path(".env")
    if env_path.exists():
        content = env_path.read_text()
        lines = []
        found = False
        for line in content.splitlines():
            if line.startswith("SESSION_NAME="):
                lines.append(f"SESSION_NAME={name}")
                found = True
            else:
                lines.append(line)
        if not found:
            lines.append(f"SESSION_NAME={name}")
        env_path.write_text("\n".join(lines) + "\n")

    await message.edit_text(
        f"✅ Session switched to **`{name}`**\n\n"
        f"⚠️ **Restart the userbot** for changes to take effect.\n"
        f"`Ctrl+C` then `python main.py`"
    )


@Client.on_message(filters.command("newsession", prefixes=config.COMMAND_PREFIX) & filters.me)
async def new_session(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit_text(
            f"Usage: `{config.COMMAND_PREFIX}newsession <name>`\n\n"
            f"This will create a new session file.\n"
            f"You need to login with phone + OTP for the new account."
        )
        return

    name = message.command[1].strip().replace(" ", "_")
    session_path = SESSIONS_DIR / f"{name}.session"

    if session_path.exists():
        await message.edit_text(f"❌ Session `{name}` already exists.")
        return

    await message.edit_text(
        f"🔐 Creating new session **`{name}`**...\n\n"
        f"1. Stop current bot (`Ctrl+C`)\n"
        f"2. Run the login command shown in docs\n"
        f"3. Login with phone + OTP\n"
        f"4. Then use `{config.COMMAND_PREFIX}session {name}` and restart."
    )


@Client.on_message(filters.command("delsession", prefixes=config.COMMAND_PREFIX) & filters.me)
async def delete_session(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit_text(f"Usage: `{config.COMMAND_PREFIX}delsession <name>`")
        return

    name = message.command[1].strip()

    if name == config.SESSION_NAME:
        await message.edit_text("❌ Cannot delete the currently active session.")
        return

    session_file = SESSIONS_DIR / f"{name}.session"
    journal = SESSIONS_DIR / f"{name}.session-journal"

    deleted = False
    if session_file.exists():
        session_file.unlink()
        deleted = True
    if journal.exists():
        journal.unlink()

    main_session = Path("data") / f"{name}.session"
    if main_session.exists() and name != config.SESSION_NAME:
        main_session.unlink()
        deleted = True

    if deleted:
        await message.edit_text(f"🗑️ Session `{name}` deleted.")
    else:
        await message.edit_text(f"❌ Session `{name}` not found.")
