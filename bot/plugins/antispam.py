import time
from collections import defaultdict
from pyrogram import Client, filters
from bot.client import app
from pyrogram.types import Message
import config
from bot.database import db

flood_tracker = defaultdict(list)


@app.on_message(filters.group & ~filters.me & ~filters.bot & ~filters.service, group=20)
async def anti_flood(client: Client, message: Message):
    if not config.ENABLE_ANTISPAM:
        return

    if not message.from_user:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    key = (chat_id, user_id)
    now = time.time()

    flood_tracker[key] = [t for t in flood_tracker[key] if now - t < config.ANTISPAM_TIME_WINDOW]
    flood_tracker[key].append(now)

    if len(flood_tracker[key]) >= config.ANTISPAM_MAX_MESSAGES:
        warnings = await db.add_warning(user_id, chat_id)

        try:
            await message.delete()
        except Exception:
            pass

        if warnings >= config.ANTISPAM_WARN_LIMIT:
            try:
                await client.ban_chat_member(chat_id, user_id)
                await client.send_message(
                    chat_id,
                    f"🔨 {message.from_user.mention} has been **banned** for flooding."
                )
                await db.reset_warnings(user_id, chat_id)
            except Exception:
                pass
        else:
            try:
                await client.send_message(
                    chat_id,
                    f"⚠️ {message.from_user.mention}, stop flooding! "
                    f"Warning {warnings}/{config.ANTISPAM_WARN_LIMIT}"
                )
            except Exception:
                pass

        flood_tracker[key].clear()


@app.on_message(filters.command("resetwarns", prefixes=config.COMMAND_PREFIX) & filters.me)
async def reset_warns(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.edit_text("Reply to a user to reset their warnings.")
        return

    user = message.reply_to_message.from_user
    await db.reset_warnings(user.id, message.chat.id)
    await message.edit_text(f"✅ Warnings reset for {user.mention}")
