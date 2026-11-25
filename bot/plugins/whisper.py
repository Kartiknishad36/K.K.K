"""
🔒 Whisper (userbot-safe — NO inline buttons)

Telegram USER account inline callback buttons support nahi karta.
Flow:
  1) Group teaser + ID
  2) Target ko DM secret (agar privacy allow)
  3) .reveal <id> — sirf target/sender

.whisper / .w  @user text | reply + text
.reveal / .ows / .readw / .openw  <id>
.swhisper / .sw / .secret  @user [sec] text
.wlist  .wclear
"""
from __future__ import annotations

import asyncio
import random
import re
import time
from typing import Any

from pyrogram import filters
from pyrogram.types import Message

from bot.client import app
import config

P = config.COMMAND_PREFIX

WHISPERS: dict[str, dict[str, Any]] = {}
MAX_WHISPERS = 300
DEFAULT_SECRET_SEC = 10
MAX_SECRET_SEC = 120


async def _out(m: Message, t: str):
    try:
        return await m.reply_text(t)
    except Exception:
        try:
            return await m.edit_text(t)
        except Exception:
            return None


def _new_id() -> str:
    for _ in range(30):
        wid = str(random.randint(100000, 999999))
        if wid not in WHISPERS:
            return wid
    return str(int(time.time() * 1000) % 10**9)


def _trim():
    if len(WHISPERS) <= MAX_WHISPERS:
        return
    items = sorted(WHISPERS.items(), key=lambda x: x[1].get("ts", 0))
    for k, _ in items[: len(WHISPERS) - MAX_WHISPERS]:
        WHISPERS.pop(k, None)


async def _resolve_target(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
        text = " ".join(message.command[1:]) if len(message.command) > 1 else ""
        return target, text

    if len(message.command) < 3:
        return None, (
            f"🔒 <b>Whisper Help</b>\n\n"
            f"• <code>{P}whisper @user secret text</code>\n"
            f"• Reply + <code>{P}w secret text</code>\n\n"
            f"Padhna (target):\n"
            f"• <code>{P}reveal 123456</code>\n\n"
            f"DM auto-delete:\n"
            f"• <code>{P}swhisper @user text</code>\n"
            f"• <code>{P}swhisper @user 20 text</code>\n\n"
            f"⚠️ User account pe button support nahi —\n"
            f"isliye <code>{P}reveal ID</code> se khulta hai."
        )

    raw = message.command[1].lstrip("@")
    try:
        target = await client.get_users(int(raw) if raw.isdigit() else raw)
    except Exception:
        return None, "❌ User nahi mila — sahi @username / id do."

    text = " ".join(message.command[2:])
    return target, text


@app.on_message(filters.command(["whisper", "w"], prefixes=P))
async def group_whisper(client, message: Message):
    target, text = await _resolve_target(client, message)
    if target is None:
        await _out(message, text)
        return
    if not (text or "").strip():
        await _out(message, "❌ Secret text likho.")
        return
    if getattr(target, "is_bot", False):
        await _out(message, "❌ Bot pe whisper nahi.")
        return

    me = message.from_user or await client.get_me()
    wid = _new_id()
    secret = text.strip()
    WHISPERS[wid] = {
        "from_id": me.id,
        "from_name": me.first_name or "User",
        "to_id": target.id,
        "to_name": target.first_name or "User",
        "text": secret,
        "ts": time.time(),
        "chat_id": message.chat.id,
    }
    _trim()

    mention = f"<a href='tg://user?id={target.id}'>{target.first_name}</a>"
    teaser = (
        f"🔒 <b>Secret Whisper</b>\n\n"
        f"👤 For: {mention}\n"
        f"🆔 Code: <code>{wid}</code>\n\n"
        f"Padhne ke liye:\n"
        f"<code>{P}reveal {wid}</code>\n\n"
        f"Sirf <b>{target.first_name}</b> (ya sender) dekh sakta hai."
    )

    try:
        await message.reply_text(teaser, disable_web_page_preview=True)
    except Exception as e:
        await _out(message, f"❌ Group message fail: <code>{e}</code>")
        WHISPERS.pop(wid, None)
        return

    dm_ok = False
    try:
        await client.send_message(
            target.id,
            f"🔒 <b>Whisper for you</b>\n"
            f"From: <b>{me.first_name}</b>\n"
            f"Code: <code>{wid}</code>\n\n"
            f"{secret}\n\n"
            f"Group: <code>{P}reveal {wid}</code>",
        )
        dm_ok = True
    except Exception:
        dm_ok = False

    try:
        await message.delete()
    except Exception:
        pass

    note = await _out(
        message,
        f"✅ Whisper <code>{wid}</code>\n"
        f"DM target: {'✅' if dm_ok else '❌ privacy — unhe .reveal use karna hoga'}",
    )
    if note:
        await asyncio.sleep(5)
        try:
            await note.delete()
        except Exception:
            pass


@app.on_message(filters.command(["reveal", "ows", "readw", "openw"], prefixes=P))
async def reveal_cmd(client, message: Message):
    uid = message.from_user.id if message.from_user else 0

    wid = None
    if len(message.command) > 1 and message.command[1].isdigit():
        wid = message.command[1]
    elif message.reply_to_message and (message.reply_to_message.text or ""):
        m = re.search(r"\b(\d{6,9})\b", message.reply_to_message.text or "")
        if m:
            wid = m.group(1)

    if not wid:
        await _out(
            message,
            f"Usage:\n<code>{P}reveal 123456</code>\n"
            f"Ya teaser pe reply + <code>{P}reveal</code>",
        )
        return

    data = WHISPERS.get(wid)
    if not data:
        await _out(message, "⏳ Whisper expire / galat code.")
        return

    if uid not in (data["to_id"], data["from_id"]):
        await _out(message, "😏 Ye secret tumhare liye nahi hai.")
        return

    body = (
        f"🔓 <b>Whisper</b> <code>{wid}</code>\n"
        f"From: <b>{data['from_name']}</b> → <b>{data['to_name']}</b>\n\n"
        f"{data['text']}"
    )

    try:
        await client.send_message(uid, body)
        await _out(message, "✅ Secret tumhari <b>DM</b> me bhej diya.")
        return
    except Exception:
        pass

    await _out(message, body)


@app.on_message(filters.command(["swhisper", "sw", "secret"], prefixes=P))
async def dm_whisper(client, message: Message):
    if len(message.command) < 3:
        await _out(
            message,
            f"🔒 <b>Secret DM</b>\n"
            f"<code>{P}swhisper @user text</code>\n"
            f"<code>{P}swhisper @user 20 text</code>\n"
            f"Default delete: <code>{DEFAULT_SECRET_SEC}s</code>",
        )
        return

    raw = message.command[1].lstrip("@")
    try:
        target = await client.get_users(int(raw) if raw.isdigit() else raw)
    except Exception:
        await _out(message, "❌ User nahi mila.")
        return

    rest = message.command[2:]
    sec = DEFAULT_SECRET_SEC
    if rest and rest[0].isdigit():
        sec = max(3, min(int(rest[0]), MAX_SECRET_SEC))
        text = " ".join(rest[1:])
    else:
        text = " ".join(rest)

    if not text.strip():
        await _out(message, "❌ Message khali.")
        return

    me = message.from_user or await client.get_me()
    try:
        sent = await client.send_message(
            target.id,
            f"🔒 <b>Secret</b> from <b>{me.first_name}</b>\n\n"
            f"{text.strip()}\n\n"
            f"⚠️ Auto-delete in <code>{sec}s</code>",
        )
    except Exception as e:
        await _out(message, f"❌ DM fail: <code>{type(e).__name__}: {e}</code>")
        return

    await _out(message, f"✅ Secret DM → <b>{target.first_name}</b> · {sec}s")
    try:
        await message.delete()
    except Exception:
        pass

    async def _del():
        await asyncio.sleep(sec)
        try:
            await sent.delete()
        except Exception:
            pass

    asyncio.create_task(_del())


@app.on_message(filters.command(["wlist"], prefixes=P))
async def wlist_cmd(client, message: Message):
    await _out(message, f"🔒 Active: <code>{len(WHISPERS)}</code> · <code>{P}wclear</code>")


@app.on_message(filters.command(["wclear"], prefixes=P))
async def wclear_cmd(client, message: Message):
    n = len(WHISPERS)
    WHISPERS.clear()
    await _out(message, f"🗑 Cleared <code>{n}</code>")
