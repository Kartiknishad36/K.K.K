"""
🛡️ DM Permit — 3 warns → report + block
.approve .disapprove .pmpermit .pmwarns
"""
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
APPROVED = set()
PM_ON = True
WARN_COUNT = {}
MAX_WARN = 3

async def _out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["approve", "a"], prefixes=P))
async def approve_cmd(client, message: Message):
    uid = None
    if message.reply_to_message and message.reply_to_message.from_user:
        uid = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try:
            uid = (await client.get_users(message.command[1])).id
        except Exception:
            pass
    elif message.chat and message.chat.type.name == "PRIVATE":
        uid = message.chat.id
    if not uid:
        await _out(message, f"❌ Reply / id\n<code>{P}approve</code>")
        return
    APPROVED.add(uid)
    WARN_COUNT.pop(uid, None)
    await _out(message, f"✅ <b>Approved</b>\n🆔 <code>{uid}</code>")

@app.on_message(filters.command(["disapprove", "da", "unapprove"], prefixes=P))
async def disapprove_cmd(client, message: Message):
    uid = None
    if message.reply_to_message and message.reply_to_message.from_user:
        uid = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try:
            uid = (await client.get_users(message.command[1])).id
        except Exception:
            pass
    if not uid:
        await _out(message, "❌ Reply / user id")
        return
    APPROVED.discard(uid)
    await _out(message, f"🚫 <b>Disapproved</b>\n🆔 <code>{uid}</code>")

@app.on_message(filters.command(["pmpermit"], prefixes=P))
async def pmpermit_toggle(client, message: Message):
    global PM_ON
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    if arg in ("on", "1"):
        PM_ON = True
    elif arg in ("off", "0"):
        PM_ON = False
    else:
        PM_ON = not PM_ON
    await _out(message, f"🛡️ <b>PM Permit:</b> {'ON ✅' if PM_ON else 'OFF ❌'}\n⚠️ Max {MAX_WARN} → block")

@app.on_message(filters.command(["pmwarns"], prefixes=P))
async def pmwarns_cmd(client, message: Message):
    if not WARN_COUNT:
        await _out(message, "📭 No warns")
        return
    lines = ["⚠️ <b>DM Warns</b>"]
    for uid, w in list(WARN_COUNT.items())[:30]:
        lines.append(f"• <code>{uid}</code> → {w}/{MAX_WARN}")
    await _out(message, "\n".join(lines))

@app.on_message(filters.private & filters.incoming & ~filters.me & ~filters.bot, group=40)
async def pm_watcher(client, message: Message):
    if not PM_ON or not message.from_user:
        return
    uid = message.from_user.id
    if uid in APPROVED or uid == getattr(config, "OWNER_ID", 0):
        return
    WARN_COUNT[uid] = WARN_COUNT.get(uid, 0) + 1
    w = WARN_COUNT[uid]
    name = message.from_user.mention
    if w >= MAX_WARN:
        try:
            await message.reply_text(f"🚫 <b>BLOCKED</b>\n{name} — max {MAX_WARN} warns")
            await client.block_user(uid)
            await client.send_message("me", f"🚩 PM Auto-Block\n{name}\n<code>{uid}</code>\nWarns {w}")
        except Exception:
            pass
        return
    try:
        await message.reply_text(
            f"╔══ ⚠️ <b>PM PERMIT</b> ══╗\n"
            f"👋 {name}\n"
            f"📩 Unapproved DM\n"
            f"⚠️ Warn <b>{w}/{MAX_WARN}</b>\n"
            f"Max → REPORT + BLOCK\n"
            f"╚══════════════════╝"
        )
    except Exception:
        pass
