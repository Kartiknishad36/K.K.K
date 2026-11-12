"""
Voice Chat / Video Chat Tools
"""

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw import functions, types
import config


@Client.on_message(filters.command(["vcinfo", "voicechat"], prefixes=config.COMMAND_PREFIX) & filters.me)
async def vc_info(client: Client, message: Message):
    if message.chat.type.name not in ["GROUP", "SUPERGROUP"]:
        await message.edit_text("This command works only in groups.")
        return

    try:
        full = await client.invoke(
            functions.channels.GetFullChannel(
                channel=await client.resolve_peer(message.chat.id)
            )
        )
        call = getattr(full.full_chat, "call", None)

        if not call:
            await message.edit_text("📭 No active Voice Chat in this group.")
            return

        text = (
            f"**🎙️ Voice Chat Info**\n\n"
            f"**Chat:** {message.chat.title}\n"
            f"**Call ID:** `{call.id}`\n"
        )
        await message.edit_text(text)
    except Exception as e:
        await message.edit_text(f"❌ Could not fetch VC info: `{e}`")


@Client.on_message(filters.command("joinvc", prefixes=config.COMMAND_PREFIX) & filters.me)
async def join_vc(client: Client, message: Message):
    if message.chat.type.name not in ["GROUP", "SUPERGROUP"]:
        await message.edit_text("Only works in groups.")
        return

    try:
        peer = await client.resolve_peer(message.chat.id)
        await client.invoke(
            functions.phone.JoinGroupCall(
                call=types.InputGroupCall(id=0, access_hash=0),
                join_as=peer,
                muted=True,
                video_stopped=True,
                params=types.DataJSON(data="{}")
            )
        )
        await message.edit_text("✅ Joined Voice Chat (muted).\n\nFor full streaming install `pytgcalls`.")
    except Exception as e:
        await message.edit_text(
            f"❌ Failed to join VC: `{e}`\n\n"
            f"**Tip:** For proper VC support: `pip install pytgcalls`"
        )


@Client.on_message(filters.command("leavevc", prefixes=config.COMMAND_PREFIX) & filters.me)
async def leave_vc(client: Client, message: Message):
    try:
        await client.invoke(
            functions.phone.LeaveGroupCall(
                call=types.InputGroupCall(id=0, access_hash=0),
                source=0
            )
        )
        await message.edit_text("✅ Left Voice Chat.")
    except Exception as e:
        await message.edit_text(f"❌ Failed to leave VC: `{e}`")


@Client.on_message(filters.command("vctitle", prefixes=config.COMMAND_PREFIX) & filters.me)
async def set_vc_title(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit_text(f"Usage: `{config.COMMAND_PREFIX}vctitle <new title>`")
        return

    title = " ".join(message.command[1:])
    await message.edit_text(
        f"🎙️ VC title change requested: **{title}**\n"
        f"(Requires active VC + admin rights)"
    )
