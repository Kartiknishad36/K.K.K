"""Fun ASCII / animation commands — fixed for bot.client imports"""
import asyncio
import random

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from bot.client import app
import config

P = config.COMMAND_PREFIX


async def _edit_safe(msg, text):
    try:
        await msg.edit_text(text)
    except FloodWait as e:
        await asyncio.sleep(min(int(e.value), 30))
        try:
            await msg.edit_text(text)
        except Exception:
            pass
    except Exception:
        pass


@app.on_message(filters.command(["cat"], prefixes=P) & filters.me)
async def cmd_cat(client, message: Message):
    frames = [
        "🐈",
        "🐈 walking...",
        "╱|、\n( .. )\n |、˜〵\nじしˍ,)ノ",
        "╱|、\n( > < )\n |、˜〵\nじしˍ,)ノ",
        "╱|、\n(˚ˎ 。7\n |、˜〵\nじしˍ,)ノ Meow!",
    ]
    for f in frames:
        await _edit_safe(message, f"<pre>{f}</pre>")
        await asyncio.sleep(0.6)


@app.on_message(filters.command(["rose"], prefixes=P) & filters.me)
async def cmd_rose(client, message: Message):
    frames = ["🌱", "🌿", "🌷", "🌹", "@}}}-,-`-  🌹"]
    for f in frames:
        await _edit_safe(message, f)
        await asyncio.sleep(0.5)


@app.on_message(filters.command(["moon", "chand"], prefixes=P) & filters.me)
async def cmd_moon(client, message: Message):
    frames = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘", "🌑"]
    for f in frames:
        await _edit_safe(message, f)
        await asyncio.sleep(0.4)


@app.on_message(filters.command(["heart", "heartart"], prefixes=P) & filters.me)
async def cmd_heart(client, message: Message):
    await _edit_safe(
        message,
        "<pre>  **  **\n ******\n  ****\n   **</pre>",
    )


@app.on_message(filters.command(["joke"], prefixes=P) & filters.me)
async def cmd_joke(client, message: Message):
    jokes = [
        "Why do programmers prefer dark mode? Light attracts bugs.",
        "There are 10 types of people: those who know binary and those who don't.",
        "A SQL query walks into a bar and asks: Can I JOIN you?",
    ]
    await message.edit_text(f"😂 {random.choice(jokes)}")


@app.on_message(filters.command(["decide"], prefixes=P) & filters.me)
async def cmd_decide(client, message: Message):
    await message.edit_text(f"🎲 **{random.choice(['Yes', 'No', 'Maybe', 'Definitely', 'Never'])}**")


@app.on_message(filters.command(["choose"], prefixes=P) & filters.me)
async def cmd_choose(client, message: Message):
    opts = message.command[1:] if message.command else []
    if len(opts) < 2:
        return await message.edit_text(f"Usage: `{P}choose a b c`")
    await message.edit_text(f"🎯 I choose: **{random.choice(opts)}**")


@app.on_message(filters.command(["funhelp", "arts"], prefixes=P) & filters.me)
async def cmd_funhelp(client, message: Message):
    await message.edit_text(
        f"**Fun commands**\n"
        f"`{P}cat` `{P}rose` `{P}moon` `{P}heart`\n"
        f"`{P}joke` `{P}decide` `{P}choose a b`"
    )
