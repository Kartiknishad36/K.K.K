"""Voice Chat tools"""
from pyrogram import Client, filters
from bot.client import app
from pyrogram.types import Message
from pyrogram.raw import functions, types
import config


@app.on_message(filters.command(["vcinfo", "voicechat"], prefixes=config.COMMAND_PREFIX) & filters.me)
async def vc_info(client: Client, message: Message):
    if message.chat.type.name not in ["GROUP", "SUPERGROUP"]:
        await message.edit_text("Only groups.")
        return
    try:
        full = await client.invoke(
            functions.channels.GetFullChannel(
                channel=await client.resolve_peer(message.chat.id)
            )
        )
        call = getattr(full.full_chat, "call", None)
        if not call:
            await message.edit_text("📭 No active Voice Chat.")
            return
        await message.edit_text(
            f"**🎙️ VC Info**\n**Chat:** {message.chat.title}\n**Call ID:** `{call.id}`"
        )
    except Exception as e:
        await message.edit_text(f"❌ `{e}`")


@app.on_message(filters.command("joinvc", prefixes=config.COMMAND_PREFIX) & filters.me)
async def join_vc(client: Client, message: Message):
    await message.edit_text("VC join needs pytgcalls for full support.")


@app.on_message(filters.command("leavevc", prefixes=config.COMMAND_PREFIX) & filters.me)
async def leave_vc(client: Client, message: Message):
    await message.edit_text("Leave VC requested.")


@app.on_message(filters.command("vctitle", prefixes=config.COMMAND_PREFIX) & filters.me)
async def set_vc_title(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit_text(f"Usage: `{config.COMMAND_PREFIX}vctitle <title>`")
        return
    title = " ".join(message.command[1:])
    await message.edit_text(f"🎙️ VC title: **{title}**")
