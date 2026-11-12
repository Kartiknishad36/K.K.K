"""
Webhook / External API Integration
"""

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
import config
from bot.database import db


@Client.on_message(filters.command("webhook", prefixes=config.COMMAND_PREFIX) & filters.me)
async def send_webhook(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit_text(
            f"**Webhook Helper**\n\n"
            f"`{config.COMMAND_PREFIX}webhook <url> <payload>`\n"
            f"`{config.COMMAND_PREFIX}webhook <url>` (reply to message)\n\n"
            f"Example:\n"
            f"`{config.COMMAND_PREFIX}webhook https://discord.com/api/webhooks/... Hello`"
        )
        return

    url = message.command[1]

    if message.reply_to_message:
        payload = message.reply_to_message.text or message.reply_to_message.caption or ""
    else:
        payload = " ".join(message.command[2:]) if len(message.command) > 2 else "Ping from Telegram UserBot"

    if not url.startswith("http"):
        await message.edit_text("❌ URL must start with http:// or https://")
        return

    status = await message.edit_text("📡 Sending webhook...")

    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Content-Type": "application/json"}
            data = {"content": payload, "text": payload, "message": payload}

            async with session.post(url, json=data, headers=headers, timeout=15) as resp:
                text = await resp.text()
                await status.edit_text(
                    f"✅ **Webhook Sent**\n\n"
                    f"**Status:** `{resp.status}`\n"
                    f"**Response:** `{text[:300]}{'...' if len(text) > 300 else ''}`"
                )
    except Exception as e:
        await status.edit_text(f"❌ Webhook failed: `{e}`")


@Client.on_message(filters.command("fetch", prefixes=config.COMMAND_PREFIX) & filters.me)
async def fetch_url(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit_text(f"Usage: `{config.COMMAND_PREFIX}fetch <url>`")
        return

    url = message.command[1]
    if not url.startswith("http"):
        url = "https://" + url

    status = await message.edit_text("🌐 Fetching...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=15) as resp:
                content_type = resp.headers.get("Content-Type", "")
                text = await resp.text()
                preview = text[:800] + ("..." if len(text) > 800 else "")

                await status.edit_text(
                    f"**🌐 Fetch Result**\n\n"
                    f"**URL:** `{url}`\n"
                    f"**Status:** `{resp.status}`\n"
                    f"**Type:** `{content_type}`\n\n"
                    f"```\n{preview}\n```"
                )
    except Exception as e:
        await status.edit_text(f"❌ Fetch failed: `{e}`")


@Client.on_message(filters.command("shorten", prefixes=config.COMMAND_PREFIX) & filters.me)
async def shorten_url(client: Client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.edit_text(f"Usage: `{config.COMMAND_PREFIX}shorten <url>`")
        return

    if message.reply_to_message:
        url = message.reply_to_message.text or message.reply_to_message.caption or ""
    else:
        url = message.command[1]

    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url

    status = await message.edit_text("🔗 Shortening...")

    try:
        async with aiohttp.ClientSession() as session:
            api = f"https://is.gd/create.php?format=simple&url={url}"
            async with session.get(api, timeout=10) as resp:
                short = await resp.text()
                if short.startswith("http"):
                    await status.edit_text(f"🔗 **Short URL:**\n{short}")
                else:
                    await status.edit_text(f"❌ Error: {short}")
    except Exception as e:
        await status.edit_text(f"❌ Failed: `{e}`")


@Client.on_message(filters.command("sethook", prefixes=config.COMMAND_PREFIX) & filters.me)
async def set_webhook_note(client: Client, message: Message):
    if len(message.command) < 3:
        await message.edit_text(
            f"Usage: `{config.COMMAND_PREFIX}sethook <name> <url>`\n"
            f"Then use `{config.COMMAND_PREFIX}webhook <name> <payload>`"
        )
        return

    name = message.command[1].lower()
    url = message.command[2]

    await db.save_note(message.chat.id, f"hook_{name}", url)
    await message.edit_text(f"✅ Webhook **`{name}`** saved!\nURL: `{url}`")
