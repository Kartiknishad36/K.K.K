"""Encrypted notes"""
import base64
import hashlib
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
ENC_NOTES = {}

def _xor(data, key):
    k = hashlib.sha256(key.encode()).digest()
    raw = data.encode("utf-8")
    out = bytes(b ^ k[i % len(k)] for i, b in enumerate(raw))
    return base64.urlsafe_b64encode(out).decode()

def _xor_dec(data, key):
    k = hashlib.sha256(key.encode()).digest()
    raw = base64.urlsafe_b64decode(data.encode())
    out = bytes(b ^ k[i % len(k)] for i, b in enumerate(raw))
    return out.decode("utf-8", errors="replace")

async def out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["encnote", "encrypt"], prefixes=P))
async def encnote_cmd(client, message: Message):
    if len(message.command) < 3:
        await out(message, f"Usage: `{P}encnote <name> <text>`")
        return
    name = message.command[1].lower()
    text = " ".join(message.command[2:])
    key = str(config.OWNER_ID or "secret")
    ENC_NOTES[name] = _xor(text, key)
    await out(message, f"🔐 Encrypted note `{name}` saved")

@app.on_message(filters.command(["decnote", "decrypt"], prefixes=P))
async def decnote_cmd(client, message: Message):
    if len(message.command) < 2:
        await out(message, f"Usage: `{P}decnote <name>`")
        return
    name = message.command[1].lower()
    enc = ENC_NOTES.get(name)
    if not enc:
        await out(message, "❌ Not found")
        return
    key = str(config.OWNER_ID or "secret")
    try:
        plain = _xor_dec(enc, key)
        await out(message, f"🔓 **{name}**\n{plain}")
    except Exception as e:
        await out(message, f"❌ `{e}`")

@app.on_message(filters.command(["encnotes"], prefixes=P))
async def encnotes_list(client, message: Message):
    keys = list(ENC_NOTES.keys())
    await out(message, "🔐 " + (", ".join(f"`{k}`" for k in keys) if keys else "empty"))
