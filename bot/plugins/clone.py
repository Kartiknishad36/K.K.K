"""Message clone / mirror between chats"""
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app, logger
import config

P = config.COMMAND_PREFIX
CLONES = {}

async def out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["clone"], prefixes=P))
async def clone_cmd(client, message: Message):
    if len(message.command) > 1 and message.command[1].lower() == "off":
        CLONES.pop(message.chat.id, None)
        await out(message, "🔄 Clone **OFF**")
        return
    if len(message.command) < 2:
        await out(message, f"Usage:\n`{P}clone <target_chat_id>`\n`{P}clone off`\n`{P}clones`")
        return
    try:
        target = int(message.command[1])
    except ValueError:
        await out(message, "target_chat_id must be number")
        return
    CLONES[message.chat.id] = target
    await out(message, f"🔄 Cloning this chat → `{target}`")

@app.on_message(filters.command(["clones"], prefixes=P))
async def clones_list(client, message: Message):
    if not CLONES:
        await out(message, "No active clones.")
        return
    lines = ["🔄 **Active clones**"] + [f"`{s}` → `{d}`" for s, d in CLONES.items()]
    await out(message, "\n".join(lines))

@app.on_message(filters.incoming & ~filters.me, group=25)
async def clone_watcher(client, message: Message):
    target = CLONES.get(message.chat.id)
    if not target:
        return
    try:
        if message.text:
            await client.send_message(target, message.text)
        else:
            await message.copy(target)
    except Exception as e:
        logger.error(f"clone: {e}")
