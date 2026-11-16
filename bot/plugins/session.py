"""Session manager info"""
from datetime import datetime, timezone
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX

async def out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["sessions", "session"], prefixes=P))
async def sessions_cmd(client, message: Message):
    me = await client.get_me()
    lines = [
        "╔══ 🔐 SESSION INFO ══╗",
        f"01 Account: {me.first_name}",
        f"02 ID: `{me.id}`",
        f"03 Username: @{me.username}" if me.username else "03 Username: None",
        f"04 Session name: `{config.SESSION_NAME}`",
        f"05 String session: {bool(config.SESSION_STRING)}",
        f"06 API ID set: {bool(config.API_ID)}",
        f"07 API HASH set: {bool(config.API_HASH)}",
        f"08 Prefix: `{P}`",
        f"09 Owner ID: `{config.OWNER_ID}`",
        f"10 Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"11 Premium: {getattr(me, 'is_premium', False)}",
        f"12 DC: {getattr(me, 'dc_id', 'N/A')}",
        "└─ Set SESSION_STRING env for deploy",
    ]
    await out(message, "\n".join(lines))

@app.on_message(filters.command(["newsession"], prefixes=P))
async def newsession_cmd(client, message: Message):
    await out(message, "ℹ️ Generate StringSession offline, set SESSION_STRING on host.")

@app.on_message(filters.command(["delsession"], prefixes=P))
async def delsession_cmd(client, message: Message):
    await out(message, "⚠️ Delete session only on host/env — not from chat.")
