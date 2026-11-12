from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime
import config
from bot.database import db
from bot.helpers.tools import humanize_time


@Client.on_message(filters.command("afk", prefixes=config.COMMAND_PREFIX) & filters.me)
async def set_afk(client: Client, message: Message):
    reason = " ".join(message.command[1:]) if len(message.command) > 1 else config.AFK_DEFAULT_REASON
    await db.set_afk(config.OWNER_ID, reason)
    await message.edit_text(f"😴 **AFK Mode Enabled**\n\n**Reason:** {reason}")


@Client.on_message(filters.command(["unafk", "noafk"], prefixes=config.COMMAND_PREFIX) & filters.me)
async def unset_afk(client: Client, message: Message):
    afk_data = await db.get_afk(config.OWNER_ID)
    if not afk_data:
        await message.edit_text("You are not AFK.")
        return

    since = humanize_time(afk_data["since"])
    await db.unset_afk(config.OWNER_ID)
    await message.edit_text(f"✅ **Welcome back!**\nYou were AFK for {since}")


# Auto reply when someone mentions/replies while AFK
@Client.on_message(
    (filters.private | filters.mentioned | filters.reply) & ~filters.me & ~filters.bot,
    group=5
)
async def afk_auto_reply(client: Client, message: Message):
    if not config.ENABLE_AFK:
        return

    afk_data = await db.get_afk(config.OWNER_ID)
    if not afk_data:
        return

    # Don't reply in channels or if already replied recently (simple check)
    if message.chat.type.name == "CHANNEL":
        return

    reason = afk_data.get("reason") or config.AFK_DEFAULT_REASON
    since = humanize_time(afk_data["since"])

    text = (
        f"😴 **I am currently AFK**\n\n"
        f"**Reason:** {reason}\n"
        f"**Since:** {since}"
    )

    try:
        await message.reply_text(text)
    except Exception:
        pass


# Auto remove AFK when owner sends any message
@Client.on_message(filters.me & ~filters.command(["afk"], prefixes=config.COMMAND_PREFIX), group=1)
async def auto_unafk(client: Client, message: Message):
    afk_data = await db.get_afk(config.OWNER_ID)
    if afk_data:
        await db.unset_afk(config.OWNER_ID)
        # Silent remove - no notification
