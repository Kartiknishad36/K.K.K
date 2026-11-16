"""PM Permit — approve/disapprove private messages"""
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
APPROVED = set()
PM_ON = True
WARN_COUNT = {}
MAX_WARN = 3

async def out(message, text):
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
        await out(message, "Reply / user id do.")
        return
    APPROVED.add(uid)
    WARN_COUNT.pop(uid, None)
    await out(message, f"✅ Approved `{uid}`")

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
        await out(message, "Reply / user id do.")
        return
    APPROVED.discard(uid)
    await out(message, f"❌ Disapproved `{uid}`")

@app.on_message(filters.command(["pmpermit"], prefixes=P))
async def pmpermit_toggle(client, message: Message):
    global PM_ON
    PM_ON = not PM_ON
    await out(message, f"PM Permit: **{'ON' if PM_ON else 'OFF'}**")

@app.on_message(filters.private & filters.incoming & ~filters.me & ~filters.bot, group=40)
async def pm_watcher(client, message: Message):
    if not PM_ON or not message.from_user:
        return
    uid = message.from_user.id
    if uid in APPROVED or uid == config.OWNER_ID:
        return
    WARN_COUNT[uid] = WARN_COUNT.get(uid, 0) + 1
    if WARN_COUNT[uid] >= MAX_WARN:
        try:
            await client.block_user(uid)
            await message.reply_text("🚫 Blocked — too many messages without approval.")
        except Exception:
            pass
        return
    try:
        await message.reply_text(f"⚠️ PM Permit active.\nWarns: {WARN_COUNT[uid]}/{MAX_WARN}")
    except Exception:
        pass
