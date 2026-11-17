"""
📢 Broadcast Module

.broadcast <msg>  — ALL groups + channels
.gcast <msg>      — ONLY groups / supergroups
.dmcast <msg>     — ONLY private DMs
.stopcast         — stop
.caststatus       — status
"""
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from bot.client import app
import config

P = config.COMMAND_PREFIX
CAST_RUN = {"on": False}


async def _out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None


def _get_text(message: Message) -> str:
    if message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption):
        return message.reply_to_message.text or message.reply_to_message.caption
    parts = (message.text or "").split(None, 1)
    return parts[1] if len(parts) > 1 else ""


async def _run_cast(client, message: Message, mode: str, text: str):
    if CAST_RUN.get("on"):
        await _out(message, f"⏳ Already running — <code>{P}stopcast</code>")
        return
    if not text:
        await _out(
            message,
            f"╔══ 📢 <b>CAST HELP</b> ══╗\n"
            f"• <code>{P}broadcast msg</code> — groups + channels\n"
            f"• <code>{P}gcast msg</code> — only groups\n"
            f"• <code>{P}dmcast msg</code> — only DMs\n"
            f"• Reply + command bhi chalega\n"
            f"• <code>{P}stopcast</code> — stop\n"
            f"╚══════════════════╝",
        )
        return

    CAST_RUN["on"] = True
    status = await _out(message, f"📢 <b>{mode}</b> start...\nStop: <code>{P}stopcast</code>")
    ok = fail = skip = 0
    try:
        async for d in client.get_dialogs():
            if not CAST_RUN.get("on"):
                break
            chat = d.chat
            t = chat.type
            if mode == "broadcast":
                if t not in (ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL):
                    continue
            elif mode == "gcast":
                if t not in (ChatType.GROUP, ChatType.SUPERGROUP):
                    continue
            elif mode == "dmcast":
                if t != ChatType.PRIVATE:
                    continue
                if getattr(chat, "is_bot", False):
                    skip += 1
                    continue
            else:
                continue
            try:
                await client.send_message(chat.id, text)
                ok += 1
            except Exception:
                fail += 1
            await asyncio.sleep(0.35)
    except Exception as e:
        if status:
            try:
                await status.edit_text(f"❌ <code>{e}</code>\n✅ {ok} | ❌ {fail}")
            except Exception:
                pass
        CAST_RUN["on"] = False
        return
    CAST_RUN["on"] = False
    if status:
        try:
            await status.edit_text(
                f"✅ <b>{mode}</b> done\n"
                f"📤 Sent: <code>{ok}</code>\n"
                f"❌ Fail: <code>{fail}</code>\n"
                f"⏭ Skip: <code>{skip}</code>"
            )
        except Exception:
            pass


@app.on_message(filters.command(["broadcast"], prefixes=P))
async def broadcast_cmd(client, message: Message):
    await _run_cast(client, message, "broadcast", _get_text(message))


@app.on_message(filters.command(["gcast"], prefixes=P))
async def gcast_cmd(client, message: Message):
    await _run_cast(client, message, "gcast", _get_text(message))


@app.on_message(filters.command(["dmcast"], prefixes=P))
async def dmcast_cmd(client, message: Message):
    await _run_cast(client, message, "dmcast", _get_text(message))


@app.on_message(filters.command(["stopcast", "caststop"], prefixes=P))
async def stopcast_cmd(client, message: Message):
    CAST_RUN["on"] = False
    await _out(message, "🛑 Cast stop signal.")


@app.on_message(filters.command(["caststatus"], prefixes=P))
async def caststatus_cmd(client, message: Message):
    await _out(
        message,
        f"╔══ 📢 <b>CAST STATUS</b> ══╗\n"
        f"Running: <b>{'YES' if CAST_RUN.get('on') else 'NO'}</b>\n"
        f"• <code>{P}broadcast</code> → groups + channels\n"
        f"• <code>{P}gcast</code> → groups only\n"
        f"• <code>{P}dmcast</code> → DMs only\n"
        f"╚══════════════════╝",
    )
