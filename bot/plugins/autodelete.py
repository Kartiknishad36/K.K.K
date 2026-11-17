"""
Auto-delete

.autodel <seconds|off>     — group messages N sec baad delete
.cmddel <seconds|off>      — apne command messages auto-delete (default 1s)
.autodelinfo               — current settings details

Chat watcher: group incoming messages
Cmd watcher:  outgoing messages starting with prefix
"""
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app, logger
import config

P = config.COMMAND_PREFIX

# chat_id -> seconds for ALL incoming group messages
AUTODEL: dict[int, int] = {}
# global: delete own command messages after N seconds (0 = off)
CMD_DEL_SEC = 1


async def out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None


@app.on_message(filters.command(["autodel", "autodelete"], prefixes=P))
async def autodel_cmd(client, message: Message):
    if len(message.command) < 2:
        cur = AUTODEL.get(message.chat.id)
        await out(
            message,
            f"╔══ 🗑 <b>AUTODELETE</b> ══╗\n"
            f"Chat messages: <code>{cur if cur else 'OFF'}</code>\n"
            f"Own commands: <code>{CMD_DEL_SEC or 'OFF'}s</code>\n\n"
            f"Usage:\n"
            f"• <code>{P}autodel 1</code> — group msgs 1s me delete\n"
            f"• <code>{P}autodel off</code>\n"
            f"• <code>{P}cmddel 1</code> — command msg auto-delete\n"
            f"• <code>{P}cmddel off</code>\n"
            f"• <code>{P}autodelinfo</code>\n"
            f"╚══════════════════╝",
        )
        return
    arg = message.command[1].lower()
    if arg in ("off", "0", "disable"):
        AUTODEL.pop(message.chat.id, None)
        await out(message, "🗑 Chat auto-delete <b>OFF</b>")
        return
    try:
        sec = int(arg)
        if sec < 1 or sec > 86400:
            raise ValueError
    except ValueError:
        await out(message, "Seconds must be 1–86400")
        return
    AUTODEL[message.chat.id] = sec
    await out(message, f"✅ Chat auto-delete <b>{sec}s</b>")


@app.on_message(filters.command(["cmddel", "cmddelete"], prefixes=P))
async def cmddel_cmd(client, message: Message):
    global CMD_DEL_SEC
    if len(message.command) < 2:
        await out(
            message,
            f"Own command auto-delete: <code>{CMD_DEL_SEC or 'OFF'}</code>\n"
            f"Usage: <code>{P}cmddel 1</code> | <code>{P}cmddel off</code>",
        )
        return
    arg = message.command[1].lower()
    if arg in ("off", "0", "disable"):
        CMD_DEL_SEC = 0
        await out(message, "🗑 Command auto-delete <b>OFF</b>")
        return
    try:
        sec = int(arg)
        if sec < 0 or sec > 60:
            raise ValueError
    except ValueError:
        await out(message, "Use 0–60 seconds")
        return
    CMD_DEL_SEC = sec
    await out(message, f"✅ Command auto-delete <b>{sec}s</b>")


@app.on_message(filters.command(["autodelinfo"], prefixes=P))
async def autodel_info(client, message: Message):
    cur = AUTODEL.get(message.chat.id)
    await out(
        message,
        f"╔══ 🗑 AUTODELETE DETAILS ══╗\n"
        f"01 Chat ID: `{message.chat.id}`\n"
        f"02 Chat autodel: `{cur if cur else 'OFF'}`\n"
        f"03 Global cmd del: `{CMD_DEL_SEC or 'OFF'}s`\n"
        f"04 Prefix: `{P}`\n"
        f"05 Config ENABLE_AUTODELETE: `{getattr(config, 'ENABLE_AUTODELETE', True)}`\n"
        f"06 Scope chat msgs: group incoming\n"
        f"07 Scope cmd msgs: outgoing with prefix\n"
        f"08 Max chat delay: 86400s\n"
        f"09 Max cmd delay: 60s\n"
        f"└─ END",
    )


@app.on_message(filters.group & filters.incoming, group=50)
async def autodel_watcher(client, message: Message):
    if not getattr(config, "ENABLE_AUTODELETE", True):
        return
    sec = AUTODEL.get(message.chat.id)
    if not sec:
        return
    try:
        await asyncio.sleep(sec)
        await message.delete()
    except Exception:
        pass


@app.on_message(filters.outgoing & filters.text, group=51)
async def cmd_autodel_watcher(client, message: Message):
    """Delete own command messages after CMD_DEL_SEC."""
    global CMD_DEL_SEC
    if not CMD_DEL_SEC:
        return
    text = message.text or ""
    if not text.startswith(P):
        return
    if len(text) <= len(P):
        return
    try:
        await asyncio.sleep(CMD_DEL_SEC)
        await message.delete()
    except Exception:
        pass
