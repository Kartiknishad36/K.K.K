from pyrogram import Client, filters
from bot.client import app
from pyrogram.types import Message
import config
from bot.database import db


@app.on_message(filters.command("filter", prefixes=config.COMMAND_PREFIX) & filters.me)
async def add_filter(client: Client, message: Message):
    if len(message.command) < 3 and not message.reply_to_message:
        await message.edit_text(
            f"Usage:\n`{config.COMMAND_PREFIX}filter <keyword> <reply text>`\n"
            f"Or reply: `{config.COMMAND_PREFIX}filter <keyword>`"
        )
        return

    keyword = message.command[1].lower()

    if message.reply_to_message:
        reply = message.reply_to_message.text or message.reply_to_message.caption or ""
        if not reply:
            await message.edit_text("Replied message has no text.")
            return
    else:
        reply = " ".join(message.command[2:])

    await db.save_filter(message.chat.id, keyword, reply)
    await message.edit_text(f"✅ Filter for **`{keyword}`** saved!")


@app.on_message(filters.command("stop", prefixes=config.COMMAND_PREFIX) & filters.me)
async def stop_filter(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit_text(f"Usage: `{config.COMMAND_PREFIX}stop <keyword>`")
        return

    keyword = message.command[1].lower()
    deleted = await db.delete_filter(message.chat.id, keyword)

    if deleted:
        await message.edit_text(f"🗑️ Filter **`{keyword}`** removed.")
    else:
        await message.edit_text(f"❌ Filter **`{keyword}`** not found.")


@app.on_message(filters.command("filters", prefixes=config.COMMAND_PREFIX) & filters.me)
async def list_filters(client: Client, message: Message):
    all_filters = await db.get_all_filters(message.chat.id)

    if not all_filters:
        await message.edit_text("No filters in this chat.")
        return

    text = "**🔍 Active Filters:**\n\n" + "\n".join(f"• `{f['keyword']}`" for f in all_filters)
    await message.edit_text(text)


@app.on_message(filters.text & ~filters.me & ~filters.bot, group=10)
async def trigger_filters(client: Client, message: Message):
    if not message.text:
        return

    all_filters = await db.get_all_filters(message.chat.id)
    text_lower = message.text.lower()

    for f in all_filters:
        if f["keyword"] in text_lower:
            try:
                await message.reply_text(f["reply"])
            except Exception:
                pass
            break
