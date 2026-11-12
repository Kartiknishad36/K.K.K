"""
Encrypted Notes + Secret Chat helpers
"""

import base64
from pyrogram import Client, filters
from pyrogram.types import Message
import config
from bot.database import db

SECRET_KEY = str(config.OWNER_ID)[::-1] + "userbot_secret_2026"


def simple_encrypt(text: str) -> str:
    key = SECRET_KEY
    encrypted = []
    for i, char in enumerate(text):
        key_c = key[i % len(key)]
        encrypted.append(chr(ord(char) ^ ord(key_c)))
    return base64.urlsafe_b64encode("".join(encrypted).encode()).decode()


def simple_decrypt(token: str) -> str:
    try:
        encrypted = base64.urlsafe_b64decode(token.encode()).decode()
        key = SECRET_KEY
        decrypted = []
        for i, char in enumerate(encrypted):
            key_c = key[i % len(key)]
            decrypted.append(chr(ord(char) ^ ord(key_c)))
        return "".join(decrypted)
    except Exception:
        return "[Decryption failed]"


@Client.on_message(filters.command("encnote", prefixes=config.COMMAND_PREFIX) & filters.me)
async def save_encrypted_note(client: Client, message: Message):
    if len(message.command) < 3 and not message.reply_to_message:
        await message.edit_text(
            f"Usage:\n`{config.COMMAND_PREFIX}encnote <name> <content>`\n"
            f"Or reply: `{config.COMMAND_PREFIX}encnote <name>`"
        )
        return

    name = message.command[1].lower()

    if message.reply_to_message:
        content = message.reply_to_message.text or message.reply_to_message.caption or ""
    else:
        content = " ".join(message.command[2:])

    if not content:
        await message.edit_text("No content to encrypt.")
        return

    encrypted = simple_encrypt(content)
    await db.save_note(message.chat.id, f"enc_{name}", encrypted)
    await message.edit_text(f"🔒 Encrypted note **`{name}`** saved!")


@Client.on_message(filters.command("decnote", prefixes=config.COMMAND_PREFIX) & filters.me)
async def get_encrypted_note(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit_text(f"Usage: `{config.COMMAND_PREFIX}decnote <name>`")
        return

    name = message.command[1].lower()
    encrypted = await db.get_note(message.chat.id, f"enc_{name}")

    if not encrypted:
        await message.edit_text(f"❌ Encrypted note **`{name}`** not found.")
        return

    decrypted = simple_decrypt(encrypted)
    await message.edit_text(f"🔓 **Decrypted Note `{name}`:**\n\n{decrypted}")


@Client.on_message(filters.command("encnotes", prefixes=config.COMMAND_PREFIX) & filters.me)
async def list_encrypted_notes(client: Client, message: Message):
    notes = await db.list_notes(message.chat.id)
    enc_notes = [n[4:] for n in notes if n.startswith("enc_")]

    if not enc_notes:
        await message.edit_text("No encrypted notes.")
        return

    text = "**🔒 Encrypted Notes:**\n\n" + "\n".join(f"• `{n}`" for n in enc_notes)
    await message.edit_text(text)


@Client.on_message(filters.command("secretchats", prefixes=config.COMMAND_PREFIX) & filters.me)
async def list_secret_chats(client: Client, message: Message):
    try:
        from pyrogram.raw import functions
        result = await client.invoke(functions.messages.GetAllSecretChats())
        chats = getattr(result, "chats", [])

        if not chats:
            await message.edit_text("No active secret chats found.")
            return

        text = "**🕵️ Secret Chats:**\n\n"
        for c in chats:
            text += f"• ID: `{c.id}`\n"
        await message.edit_text(text)
    except Exception as e:
        await message.edit_text(
            f"❌ Could not list secret chats: `{e}`\n\n"
            f"Note: Depends on Pyrogram version & MTProto layer."
        )
