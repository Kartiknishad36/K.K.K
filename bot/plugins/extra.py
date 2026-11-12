from pyrogram import Client, filters
from pyrogram.types import Message
import config
import asyncio


@Client.on_message(filters.command("stats", prefixes=config.COMMAND_PREFIX) & filters.me)
async def stats_command(client: Client, message: Message):
    me = await client.get_me()
    dialogs = []
    async for dialog in client.get_dialogs():
        dialogs.append(dialog)

    groups = sum(1 for d in dialogs if d.chat.type.name in ["GROUP", "SUPERGROUP"])
    channels = sum(1 for d in dialogs if d.chat.type.name == "CHANNEL")
    privates = sum(1 for d in dialogs if d.chat.type.name == "PRIVATE")
    bots = sum(1 for d in dialogs if d.chat.type.name == "BOT")

    text = (
        f"**📊 UserBot Stats**\n\n"
        f"**Account:** {me.first_name}\n"
        f"**ID:** `{me.id}`\n\n"
        f"**Dialogs:** `{len(dialogs)}`\n"
        f"• Groups: `{groups}`\n"
        f"• Channels: `{channels}`\n"
        f"• Private: `{privates}`\n"
        f"• Bots: `{bots}`"
    )
    await message.edit_text(text)


@Client.on_message(filters.command("broadcast", prefixes=config.COMMAND_PREFIX) & filters.me)
async def broadcast_command(client: Client, message: Message):
    """
    Safe broadcast - only to users who have messaged you (dialogs).
    """
    if len(message.command) < 2 and not message.reply_to_message:
        await message.edit_text(
            f"**Broadcast**\n\n"
            f"`{config.COMMAND_PREFIX}broadcast <message>`\n"
            f"Or reply to a message with `{config.COMMAND_PREFIX}broadcast`\n\n"
            f"⚠️ This will send to all private chats. Use responsibly."
        )
        return

    if message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption or ""
    else:
        text = " ".join(message.command[1:])

    if not text:
        await message.edit_text("No message to broadcast.")
        return

    status = await message.edit_text("📢 Starting broadcast...")

    success = 0
    failed = 0

    async for dialog in client.get_dialogs():
        if dialog.chat.type.name != "PRIVATE":
            continue
        if dialog.chat.id == config.OWNER_ID:
            continue
        try:
            await client.send_message(dialog.chat.id, text)
            success += 1
            await asyncio.sleep(0.5)  # Rate limit protection
        except Exception:
            failed += 1

    await status.edit_text(
        f"✅ **Broadcast Complete**\n\n"
        f"Success: `{success}`\n"
        f"Failed: `{failed}`"
    )


@Client.on_message(filters.command("join", prefixes=config.COMMAND_PREFIX) & filters.me)
async def join_chat(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit_text(f"Usage: `{config.COMMAND_PREFIX}join <invite_link or username>`")
        return

    link = message.command[1]
    try:
        await client.join_chat(link)
        await message.edit_text(f"✅ Joined successfully!")
    except Exception as e:
        await message.edit_text(f"❌ Failed to join: `{e}`")


@Client.on_message(filters.command("leave", prefixes=config.COMMAND_PREFIX) & filters.me)
async def leave_chat(client: Client, message: Message):
    try:
        await client.leave_chat(message.chat.id)
    except Exception as e:
        await message.edit_text(f"❌ Failed: `{e}`")
