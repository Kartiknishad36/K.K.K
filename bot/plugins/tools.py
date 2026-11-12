from pyrogram import Client, filters
from pyrogram.types import Message
import config
from bot.helpers.tools import get_user, humanize_time
from bot.database import db

try:
    from googletrans import Translator
    translator = Translator()
except Exception:
    translator = None


@Client.on_message(filters.command(["info", "whois"], prefixes=config.COMMAND_PREFIX) & filters.me)
async def user_info(client: Client, message: Message):
    user = await get_user(client, message)

    if not user:
        if message.command[0] == "info" and len(message.command) > 1:
            try:
                user = await client.get_users(message.command[1])
            except Exception:
                pass
        if not user:
            user = message.from_user or await client.get_me()

    try:
        full = await client.get_users(user.id)
        chat = None
        try:
            chat = await client.get_chat(user.id)
        except Exception:
            pass

        text = (
            f"**👤 User Info**\n\n"
            f"**Name:** {full.first_name} {full.last_name or ''}\n"
            f"**ID:** `{full.id}`\n"
            f"**Username:** @{full.username if full.username else 'None'}\n"
            f"**Bot:** {'Yes' if full.is_bot else 'No'}\n"
            f"**Premium:** {'Yes' if getattr(full, 'is_premium', False) else 'No'}\n"
            f"**DC:** `{getattr(full, 'dc_id', 'N/A')}`\n"
        )

        if chat and chat.bio:
            text += f"**Bio:** {chat.bio}\n"

        # Check gban
        gban = await db.is_gbanned(full.id)
        if gban:
            text += f"\n⚠️ **Globally Banned**\nReason: {gban['reason']}"

        await message.edit_text(text)
    except Exception as e:
        await message.edit_text(f"❌ Error fetching info: `{e}`")


@Client.on_message(filters.command("tr", prefixes=config.COMMAND_PREFIX) & filters.me)
async def translate_text(client: Client, message: Message):
    if not config.ENABLE_TRANSLATOR or not translator:
        await message.edit_text("Translator is not available.")
        return

    if len(message.command) < 2 and not message.reply_to_message:
        await message.edit_text(
            f"Usage:\n`{config.COMMAND_PREFIX}tr <lang> <text>`\n"
            f"`{config.COMMAND_PREFIX}tr <lang>` (reply to message)\n\n"
            f"Example: `{config.COMMAND_PREFIX}tr hi Hello`"
        )
        return

    lang = message.command[1] if len(message.command) > 1 else "en"

    if message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption or ""
    else:
        text = " ".join(message.command[2:]) if len(message.command) > 2 else ""

    if not text:
        await message.edit_text("No text to translate.")
        return

    try:
        result = translator.translate(text, dest=lang)
        await message.edit_text(
            f"**🌐 Translated** ({result.src} → {lang})\n\n"
            f"{result.text}"
        )
    except Exception as e:
        await message.edit_text(f"❌ Translation failed: `{e}`")


@Client.on_message(filters.command("dl", prefixes=config.COMMAND_PREFIX) & filters.me)
async def download_media(client: Client, message: Message):
    if not message.reply_to_message:
        await message.edit_text("Reply to a media message to download.")
        return

    reply = message.reply_to_message
    if not (reply.photo or reply.video or reply.document or reply.audio or reply.voice or reply.animation):
        await message.edit_text("Replied message has no downloadable media.")
        return

    status = await message.edit_text("📥 Downloading...")

    try:
        path = await reply.download(file_name="data/downloads/")
        await status.edit_text(f"✅ Downloaded!\n`{path}`")
    except Exception as e:
        await status.edit_text(f"❌ Download failed: `{e}`")


@Client.on_message(filters.command(["invite", "link"], prefixes=config.COMMAND_PREFIX) & filters.me)
async def invite_link(client: Client, message: Message):
    try:
        link = await client.export_chat_invite_link(message.chat.id)
        await message.edit_text(f"**Invite Link:**\n{link}")
    except Exception as e:
        await message.edit_text(f"❌ Cannot get invite link: `{e}`")
