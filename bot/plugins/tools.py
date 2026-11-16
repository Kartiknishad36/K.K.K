"""Tools — stats translate download join leave broadcast invite"""
import asyncio
from datetime import datetime, timezone
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from bot.client import app, logger
import config

P = config.COMMAND_PREFIX

async def out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception as e:
            logger.error(f"tools out: {e}")
            return None

@app.on_message(filters.command(["stats", "account"], prefixes=P))
async def stats_cmd(client, message: Message):
    me = await client.get_me()
    lines = [
        "╔══ 📊 ACCOUNT STATS ══╗",
        f"01 Name: {me.first_name} {me.last_name or ''}".strip(),
        f"02 ID: `{me.id}`",
        f"03 Username: @{me.username}" if me.username else "03 Username: None",
        f"04 Premium: {getattr(me, 'is_premium', False)}",
        f"05 DC: {getattr(me, 'dc_id', 'N/A')}",
        f"06 Bot: {me.is_bot}",
        f"07 Verified: {getattr(me, 'is_verified', False)}",
        f"08 Prefix: `{P}`",
        f"09 Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
    ]
    groups = channels = users = bots = 0
    try:
        async for d in client.get_dialogs():
            t = d.chat.type
            if t in (ChatType.GROUP, ChatType.SUPERGROUP):
                groups += 1
            elif t == ChatType.CHANNEL:
                channels += 1
            elif t == ChatType.PRIVATE:
                if getattr(d.chat, "is_bot", False):
                    bots += 1
                else:
                    users += 1
    except Exception as e:
        lines.append(f"10 Dialogs error: {type(e).__name__}")
    lines += [
        f"10 Groups: {groups}",
        f"11 Channels: {channels}",
        f"12 Users (DM): {users}",
        f"13 Bots (DM): {bots}",
        f"14 Total: {groups+channels+users+bots}",
        "└─ ✅ END STATS",
    ]
    await out(message, "\n".join(lines))

@app.on_message(filters.command(["tr", "translate"], prefixes=P))
async def translate_cmd(client, message: Message):
    if len(message.command) < 3:
        await out(message, f"Usage: `{P}tr <lang> <text>`")
        return
    lang = message.command[1]
    text = " ".join(message.command[2:])
    await out(message, f"🌐 **To:** `{lang}`\n**Text:** {text}")

@app.on_message(filters.command(["dl", "download"], prefixes=P))
async def download_cmd(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.media:
        await out(message, "Reply to media with `.dl`")
        return
    status = await out(message, "⬇️ Downloading...")
    try:
        path = await message.reply_to_message.download()
        await status.edit_text(f"✅ `{path}`")
    except Exception as e:
        await status.edit_text(f"❌ `{e}`")

@app.on_message(filters.command(["join"], prefixes=P))
async def join_cmd(client, message: Message):
    if len(message.command) < 2:
        await out(message, f"Usage: `{P}join <link|@user>`")
        return
    target = message.command[1]
    try:
        await client.join_chat(target)
        await out(message, f"✅ Joined `{target}`")
    except Exception as e:
        await out(message, f"❌ `{e}`")

@app.on_message(filters.command(["leave"], prefixes=P))
async def leave_cmd(client, message: Message):
    try:
        chat_id = message.command[1] if len(message.command) > 1 else message.chat.id
        await out(message, "👋 Leaving...")
        await client.leave_chat(chat_id)
    except Exception as e:
        await out(message, f"❌ `{e}`")

@app.on_message(filters.command(["invite", "link"], prefixes=P))
async def invite_cmd(client, message: Message):
    try:
        link = await client.export_chat_invite_link(message.chat.id)
        await out(message, f"🔗 {link}")
    except Exception as e:
        await out(message, f"❌ `{e}`")

@app.on_message(filters.command(["broadcast", "bc"], prefixes=P))
async def broadcast_cmd(client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        await out(message, f"Usage: `{P}broadcast <msg>`")
        return
    text = message.reply_to_message.text if message.reply_to_message and message.reply_to_message.text else " ".join(message.command[1:])
    status = await out(message, "📢 Broadcasting...")
    ok = fail = 0
    try:
        async for d in client.get_dialogs():
            if d.chat.type != ChatType.PRIVATE:
                continue
            try:
                await client.send_message(d.chat.id, text)
                ok += 1
            except Exception:
                fail += 1
            await asyncio.sleep(0.3)
    except Exception as e:
        await status.edit_text(f"❌ `{e}`")
        return
    await status.edit_text(f"📢 Done\n✅ {ok} | ❌ {fail}")
