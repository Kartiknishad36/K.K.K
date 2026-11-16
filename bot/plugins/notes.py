from pyrogram import Client, filters
from bot.client import app
from pyrogram.types import Message
import config
from bot.database import db


async def _out(message, text):
    try:
        await message.edit_text(text)
    except Exception:
        await message.reply_text(text)


@app.on_message(filters.command("save", prefixes=config.COMMAND_PREFIX))
async def save_note(client: Client, message: Message):
    if len(message.command) < 3 and not message.reply_to_message:
        await _out(message, f"Usage: `{config.COMMAND_PREFIX}save <name> <content>`")
        return
    name = message.command[1].lower()
    if message.reply_to_message:
        content = message.reply_to_message.text or message.reply_to_message.caption or ""
        if not content:
            await _out(message, "Replied message has no text.")
            return
    else:
        content = " ".join(message.command[2:])
    await db.save_note(message.chat.id, name, content)
    await _out(message, f"✅ Note **`{name}`** saved!")


@app.on_message(filters.command("get", prefixes=config.COMMAND_PREFIX))
async def get_note(client: Client, message: Message):
    if len(message.command) < 2:
        await _out(message, f"Usage: `{config.COMMAND_PREFIX}get <name>`")
        return
    name = message.command[1].lower()
    content = await db.get_note(message.chat.id, name)
    await _out(message, content if content else f"❌ Note **`{name}`** not found.")


@app.on_message(filters.command("clear", prefixes=config.COMMAND_PREFIX))
async def clear_note(client: Client, message: Message):
    if len(message.command) < 2:
        await _out(message, f"Usage: `{config.COMMAND_PREFIX}clear <name>`")
        return
    name = message.command[1].lower()
    deleted = await db.delete_note(message.chat.id, name)
    await _out(message, f"🗑️ Note **`{name}`** deleted." if deleted else f"❌ Note **`{name}`** not found.")


@app.on_message(filters.command("notes", prefixes=config.COMMAND_PREFIX))
async def list_notes(client: Client, message: Message):
    notes = await db.list_notes(message.chat.id)
    if not notes:
        await _out(message, "No notes saved in this chat.")
        return
    text = "**📝 Saved Notes:**\n\n" + "\n".join(f"• `{n}`" for n in notes)
    await _out(message, text)


@app.on_message(filters.regex(r"^#(\w+)"))
async def quick_note(client: Client, message: Message):
    name = message.matches[0].group(1).lower() if message.matches else None
    if not name:
        return
    content = await db.get_note(message.chat.id, name)
    if content:
        await _out(message, content)
