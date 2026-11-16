"""API fetch webhook shorten"""
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
HOOKS = {}

async def out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["fetch", "geturl"], prefixes=P))
async def fetch_cmd(client, message: Message):
    if len(message.command) < 2:
        await out(message, f"Usage: `{P}fetch <url>`")
        return
    url = message.command[1]
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=15) as r:
            body = r.read().decode("utf-8", errors="replace")[:1500]
            await out(message, f"**Status:** {r.status}\n```\n{body}\n```")
    except Exception as e:
        await out(message, f"❌ `{e}`")

@app.on_message(filters.command(["webhook", "hook"], prefixes=P))
async def webhook_cmd(client, message: Message):
    if len(message.command) < 3:
        await out(message, f"Usage: `{P}webhook <url> <payload>`")
        return
    await out(message, f"Webhook queued → `{message.command[1]}`")

@app.on_message(filters.command(["sethook"], prefixes=P))
async def sethook_cmd(client, message: Message):
    if len(message.command) < 3:
        await out(message, f"Usage: `{P}sethook <name> <url>`")
        return
    HOOKS[message.command[1].lower()] = message.command[2]
    await out(message, f"✅ Hook `{message.command[1]}` saved")

@app.on_message(filters.command(["shorten", "short"], prefixes=P))
async def shorten_cmd(client, message: Message):
    if len(message.command) < 2:
        await out(message, f"Usage: `{P}shorten <url>`")
        return
    await out(message, f"🔗 {message.command[1]}")
