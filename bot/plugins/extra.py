"""Extra utils — time random echo type"""
import random
import asyncio
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

@app.on_message(filters.command(["time", "now"], prefixes=P))
async def time_cmd(client, message: Message):
    now = datetime.now(timezone.utc)
    await out(message, f"🕐 **UTC:** `{now.strftime('%Y-%m-%d %H:%M:%S')}`\nUnix: `{int(now.timestamp())}`")

@app.on_message(filters.command(["random", "rand"], prefixes=P))
async def random_cmd(client, message: Message):
    if len(message.command) >= 3:
        try:
            a, b = int(message.command[1]), int(message.command[2])
            await out(message, f"🎲 `{random.randint(min(a,b), max(a,b))}`")
            return
        except ValueError:
            pass
    await out(message, f"🎲 `{random.randint(1, 100)}`")

@app.on_message(filters.command(["echo", "say"], prefixes=P))
async def echo_cmd(client, message: Message):
    if len(message.command) < 2:
        await out(message, f"Usage: `{P}echo <text>`")
        return
    await out(message, " ".join(message.command[1:]))

@app.on_message(filters.command(["type", "typewriter"], prefixes=P))
async def type_cmd(client, message: Message):
    if len(message.command) < 2:
        await out(message, f"Usage: `{P}type <text>`")
        return
    text = " ".join(message.command[1:])
    msg = await out(message, "...")
    if not msg:
        return
    cur = ""
    for ch in text:
        cur += ch
        try:
            await msg.edit_text(cur + "▌")
        except Exception:
            break
        await asyncio.sleep(0.05)
    try:
        await msg.edit_text(text)
    except Exception:
        pass
