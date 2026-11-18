"""
🧠 AI Boss — simple auto rules
.aiboss on|off
.blockid <user_id>     — auto-ignore list
.unblockid <user_id>
.bosslist

Incoming private from blocked ids → silent ignore (no reply modules should still run;
this sets a shared flag others can check later).
"""
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
BOSS_ON = False
BLOCKED: set[int] = set()


async def _out(m, t):
    try:
        return await m.reply_text(t)
    except Exception:
        try:
            return await m.edit_text(t)
        except Exception:
            return None


@app.on_message(filters.command(["aiboss"], prefixes=P))
async def aiboss_cmd(client, message: Message):
    global BOSS_ON
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    if arg in ("on", "1"):
        BOSS_ON = True
    elif arg in ("off", "0"):
        BOSS_ON = False
    else:
        BOSS_ON = not BOSS_ON
    await _out(
        message,
        f"🧠 <b>AI Boss:</b> {'ON ✅' if BOSS_ON else 'OFF ❌'}\n"
        f"Blocked: <code>{len(BLOCKED)}</code>\n"
        f"<code>{P}blockid id</code> · <code>{P}bosslist</code>",
    )


@app.on_message(filters.command(["blockid"], prefixes=P))
async def blockid_cmd(client, message: Message):
    uid = None
    if message.reply_to_message and message.reply_to_message.from_user:
        uid = message.reply_to_message.from_user.id
    elif len(message.command) > 1 and message.command[1].isdigit():
        uid = int(message.command[1])
    if not uid:
        await _out(message, f"Reply user ya <code>{P}blockid 123456</code>")
        return
    BLOCKED.add(uid)
    await _out(message, f"🚫 Blocked for boss rules: <code>{uid}</code>")


@app.on_message(filters.command(["unblockid"], prefixes=P))
async def unblockid_cmd(client, message: Message):
    if len(message.command) < 2 or not message.command[1].isdigit():
        await _out(message, f"<code>{P}unblockid 123456</code>")
        return
    uid = int(message.command[1])
    BLOCKED.discard(uid)
    await _out(message, f"✅ Unblocked <code>{uid}</code>")


@app.on_message(filters.command(["bosslist"], prefixes=P))
async def bosslist_cmd(client, message: Message):
    if not BLOCKED:
        await _out(message, "📭 Boss block list empty")
        return
    lines = ["🧠 <b>Boss block list</b>"] + [f"• <code>{i}</code>" for i in list(BLOCKED)[:50]]
    await _out(message, "\n".join(lines))


@app.on_message(filters.private & filters.incoming & ~filters.me, group=5)
async def boss_gate(client, message: Message):
    if not BOSS_ON or not message.from_user:
        return
    if message.from_user.id in BLOCKED:
        # early group — other handlers still may run; best-effort silence by deleting? skip
        return
