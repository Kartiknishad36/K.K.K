import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import config
from bot.database import db


@Client.on_message(filters.command("autodel", prefixes=config.COMMAND_PREFIX) & filters.me)
async def set_autodelete(client: Client, message: Message):
    if len(message.command) < 2:
        data = await db.get_autodelete(message.chat.id)
        if data and data["enabled"]:
            await message.edit_text(
                f"🗑️ AutoDelete is **ON**\nDelay: `{data['delay']}` seconds"
            )
        else:
            await message.edit_text(
                f"AutoDelete is **OFF**\n\n"
                f"Usage: `{config.COMMAND_PREFIX}autodel <seconds>`\n"
                f"Example: `{config.COMMAND_PREFIX}autodel 300` (5 minutes)\n"
                f"`{config.COMMAND_PREFIX}autodel off` to disable"
            )
        return

    arg = message.command[1].lower()

    if arg in ["off", "0", "disable", "false"]:
        await db.set_autodelete(message.chat.id, enabled=False)
        await message.edit_text("✅ AutoDelete **disabled**.")
        return

    try:
        delay = int(arg)
        if delay < 10:
            await message.edit_text("Minimum delay is 10 seconds.")
            return
        if delay > 86400 * 7:  # 7 days max
            await message.edit_text("Maximum delay is 7 days.")
            return
    except ValueError:
        await message.edit_text("Please provide a valid number of seconds.")
        return

    await db.set_autodelete(message.chat.id, enabled=True, delay=delay)
    await message.edit_text(f"✅ AutoDelete **enabled**\nMessages will be deleted after `{delay}` seconds.")


# Handler that schedules deletion
@Client.on_message(filters.group & ~filters.service, group=15)
async def autodelete_handler(client: Client, message: Message):
    if not config.ENABLE_AUTODELETE:
        return

    data = await db.get_autodelete(message.chat.id)
    if not data or not data["enabled"]:
        return

    delay = data["delay"]

    async def delete_later():
        await asyncio.sleep(delay)
        try:
            await message.delete()
        except Exception:
            pass

    asyncio.create_task(delete_later())
