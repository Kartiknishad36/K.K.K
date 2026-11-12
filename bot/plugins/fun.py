"""Fun ASCII / emoji animations"""
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import config

CAT = ["🐈", "🐈 Walking...", "╱|、\n(˚ˎ 。7  < Meow!"]
FLOWER = ["🌱", "🌿", "🌷", "🌹 FOR YOU!"]
MOON = ["🌑 New Moon...", "🌓 Quarter...", "🌕 Full Moon!"]
HEART = ["❤️", "  ❤️\n❤️  ❤️", "❤️❤️❤️\n❤️ FOR YOU"]

async def smart_edit(m, text, sleep=0.45):
    try:
        await m.edit_text(text); await asyncio.sleep(sleep)
    except FloodWait as e:
        if e.value < 8:
            await asyncio.sleep(e.value)
            try: await m.edit_text(text)
            except Exception: pass
    except Exception: pass

@Client.on_message(filters.command("cat", prefixes=config.COMMAND_PREFIX) & filters.me)
async def cat_cmd(c, m):
    msg = await m.edit_text("🐈")
    for f in CAT: await smart_edit(msg, f"`{f}`", 0.4)

@Client.on_message(filters.command("rose", prefixes=config.COMMAND_PREFIX) & filters.me)
async def rose_cmd(c, m):
    msg = await m.edit_text("🌱")
    for f in FLOWER: await smart_edit(msg, f, 0.5)

@Client.on_message(filters.command(["moon", "chand"], prefixes=config.COMMAND_PREFIX) & filters.me)
async def moon_cmd(c, m):
    msg = await m.edit_text("🌑")
    for f in MOON: await smart_edit(msg, f, 0.5)

@Client.on_message(filters.command(["heart", "heartart"], prefixes=config.COMMAND_PREFIX) & filters.me)
async def heart_cmd(c, m):
    msg = await m.edit_text("❤️")
    for f in HEART: await smart_edit(msg, f"`{f}`", 0.4)

@Client.on_message(filters.command("funhelp", prefixes=config.COMMAND_PREFIX) & filters.me)
async def funhelp_cmd(c, m):
    await m.edit_text(f"🎨 **FUN**\n`{config.COMMAND_PREFIX}cat` `{config.COMMAND_PREFIX}rose` `{config.COMMAND_PREFIX}moon` `{config.COMMAND_PREFIX}heart`")
