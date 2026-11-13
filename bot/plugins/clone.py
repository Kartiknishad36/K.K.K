from pyrogram import Client, filters
from bot.client import app
from pyrogram.types import Message
import config
from bot.database import db

CLONE_MAP = {}


@app.on_message(filters.command("clone", prefixes=config.COMMAND_PREFIX) & filters.me)
async def set_clone(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit_text(
            f"**Message Cloner**\n\n"
            f"`{config.COMMAND_PREFIX}clone <target_chat_id>` - Start cloning this chat to target\n"
            f"`{config.COMMAND_PREFIX}clone off` - Stop cloning from this chat\n"
            f"`{config.COMMAND_PREFIX}clones` - List active clones\n\n"
            f"**Note:** Use carefully. High volume can cause flood waits."
        )
        return

    arg = message.command[1].lower()
    source = message.chat.id

    if arg == "off":
        if source in CLONE_MAP:
            del CLONE_MAP[source]
            await message.edit_text("✅ Cloning **stopped** for this chat.")
        else:
            await message.edit_text("No active clone for this chat.")
        return

    try:
        target = int(arg)
    except ValueError:
        await message.edit_text("Target must be a valid chat ID (number).")
        return

    if source not in CLONE_MAP:
        CLONE_MAP[source] = []

    if target not in CLONE_MAP[source]:
        CLONE_MAP[source].append(target)

    await message.edit_text(
        f"✅ Now cloning messages from this chat to `{target}`\n"
        f"Use `{config.COMMAND_PREFIX}clone off` to stop."
    )


@app.on_message(filters.command("clones", prefixes=config.COMMAND_PREFIX) & filters.me)
async def list_clones(client: Client, message: Message):
    if not CLONE_MAP:
        await message.edit_text("No active clones.")
        return

    text = "**🔄 Active Clones:**\n\n"
    for src, targets in CLONE_MAP.items():
        text += f"`{src}` → {', '.join(f'`{t}`' for t in targets)}\n"
    await message.edit_text(text)


@app.on_message(~filters.me & ~filters.service & ~filters.command([], prefixes=config.COMMAND_PREFIX), group=30)
async def clone_handler(client: Client, message: Message):
    source = message.chat.id
    if source not in CLONE_MAP:
        return

    targets = CLONE_MAP[source]
    for target in targets:
        try:
            await message.copy(target)
        except Exception:
            pass
