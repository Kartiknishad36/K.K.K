from pyrogram import Client, filters
from bot.client import app
from pyrogram.types import Message
from datetime import datetime
import config

AFK_DATA = {"on": False, "reason": "", "since": None}


async def _out(message, text):
    try:
        await message.edit_text(text)
    except Exception:
        await message.reply_text(text)


@app.on_message(filters.command("afk", prefixes=config.COMMAND_PREFIX))
async def afk_on(client: Client, message: Message):
    reason = " ".join(message.command[1:]) if len(message.command) > 1 else getattr(config, "AFK_DEFAULT_REASON", "AFK")
    AFK_DATA["on"] = True
    AFK_DATA["reason"] = reason
    AFK_DATA["since"] = datetime.utcnow()
    await _out(message, f"😴 **AFK ON**\nReason: {reason}")


@app.on_message(filters.command(["unafk", "back"], prefixes=config.COMMAND_PREFIX))
async def afk_off(client: Client, message: Message):
    AFK_DATA["on"] = False
    AFK_DATA["reason"] = ""
    await _out(message, "✅ **AFK OFF** — wapas aa gaye.")


@app.on_message(filters.mentioned & filters.incoming & ~filters.me)
async def afk_watcher(client: Client, message: Message):
    if not AFK_DATA["on"]:
        return
    try:
        await message.reply_text(f"😴 Owner AFK hai.\nReason: {AFK_DATA['reason']}")
    except Exception:
        pass
