"""
🔒 Whisper — secret messages

.whisper / .w  @user text     — group me button; sirf target + sender dekh sake
.whisper / .w  (reply) text   — reply target ko secret
.swhisper / .sw / .secret @user [sec] text
                               — DM secret, auto-delete (default 10s)
.wlist                         — active whispers count (owner)
.wclear                        — memory clear

Note: Button callbacks userbot account se kaam karte hain jab message
us account ne bheja ho. Target ko alert me text dikhega.
"""
from __future__ import annotations

import asyncio
import random
import time
from typing import Any

from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from bot.client import app
import config

P = config.COMMAND_PREFIX

# whisper_id -> data
WHISPERS: dict[str, dict[str, Any]] = {}
# max keep
MAX_WHISPERS = 200
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
    for _ in range(20):
        wid = str(random.randint(100000, 999999))
        if wid not in WHISPERS:
            return wid
    return str(int(time.time() * 1000) % 10**9)


def _trim():
    if len(WHISPERS) <= MAX_WHISPERS:
        return
    # drop oldest by ts
    items = sorted(WHISPERS.items(), key=lambda x: x[1].get("ts", 0))
    for k, _ in items[: len(WHISPERS) - MAX_WHISPERS]:
        WHISPERS.pop(k, None)


async def _resolve_target(client, message: Message):
    """Return (user, secret_text) or (None, error)."""
    # reply path
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
        text = " ".join(message.command[1:]) if len(message.command) > 1 else ""
        return target, text

    if len(message.command) < 3:
        return None, (
            f"🔒 <b>Whisper</b>\n\n"
            f"Group:\n<code>{P}whisper @user secret text</code>\n"
            f"Reply + <code>{P}w secret text</code>\n\n"
            f"DM auto-delete:\n<code>{P}swhisper @user secret</code>\n"
            f"<code>{P}swhisper @user 15 secret</code> (sec)"
        )

    raw = message.command[1].lstrip("@")
    try:
        if raw.isdigit():
            target = await client.get_users(int(raw))
        else:
            target = await client.get_users(raw)
    except Exception:
        return None, "❌ User nahi mila — sahi @username / id do."

    text = " ".join(message.command[2:])
    return target, text


# ─── Group whisper ───────────────────────────────────────────
@app.on_message(filters.command(["whisper", "w"], prefixes=P))
async def group_whisper(client, message: Message):
    target, text = await _resolve_target(client, message)
    if target is None:
        await _out(message, text)  # error / help
        return
    if not (text or "").strip():
        await _out(message, "❌ Secret text likho.")
        return
    if target.is_bot:
        await _out(message, "❌ Bot pe whisper nahi.")
        return

    wid = _new_id()
    me = message.from_user or await client.get_me()
    WHISPERS[wid] = {
        "from_id": me.id,
        "from_name": me.first_name or "User",
        "to_id": target.id,
        "to_name": target.first_name or "User",
        "text": text.strip(),
        "ts": time.time(),
        "chat_id": message.chat.id,
    }
    _trim()

    btn = InlineKeyboardMarkup(
        [[InlineKeyboardButton("👁️ Show Secret Message", callback_data=f"whisper_{wid}")]]
    )
    mention = f"[{target.first_name}](tg://user?id={target.id})"
    try:
        await message.reply_text(
            f"🔒 <b>Secret Message</b> for {mention}\n\n"
            f"Sirf wahi (aur sender) dekh sakta hai.\n"
            f"ID: <code>{wid}</code>",
            reply_markup=btn,
            disable_web_page_preview=True,
        )
    except Exception as e:
        await _out(message, f"❌ Send fail: <code>{e}</code>")
        WHISPERS.pop(wid, None)
        return

    try:
        await message.delete()
    except Exception:
        pass


@app.on_callback_query(filters.regex(r"^whisper_\d+$"))
async def whisper_button(client, query: CallbackQuery):
    wid = query.data.split("_", 1)[1]
    data = WHISPERS.get(wid)
    if not data:
        await query.answer("⏳ Ye whisper expire / clear ho gaya!", show_alert=True)
        return

    uid = query.from_user.id if query.from_user else 0
    if uid not in (data["to_id"], data["from_id"]):
        await query.answer("Ye message tumhare liye nahi hai 😏", show_alert=True)
        return

    # Telegram alert limit ~200 chars — split if long
    body = f"From {data['from_name']}:\n\n{data['text']}"
    if len(body) > 180:
        body = body[:177] + "..."
    await query.answer(body, show_alert=True)


# ─── Secret DM (auto delete) ─────────────────────────────────
@app.on_message(filters.command(["swhisper", "sw", "secret"], prefixes=P))
async def dm_whisper(client, message: Message):
    if len(message.command) < 3:
        await _out(
            message,
            f"🔒 <b>Secret DM</b>\n"
            f"<code>{P}swhisper @user text</code>\n"
            f"<code>{P}swhisper @user 20 text</code> — 20 sec delete\n"
            f"Default delete: <code>{DEFAULT_SECRET_SEC}s</code>",
        )
        return

    raw = message.command[1].lstrip("@")
    try:
        if raw.isdigit():
            target = await client.get_users(int(raw))
        else:
            target = await client.get_users(raw)
    except Exception:
        await _out(message, "❌ User nahi mila.")
        return

    # optional seconds as 2nd arg
    rest = message.command[2:]
    sec = DEFAULT_SECRET_SEC
    if rest and rest[0].isdigit():
        sec = max(3, min(int(rest[0]), MAX_SECRET_SEC))
        text = " ".join(rest[1:])
    else:
        text = " ".join(rest)

    if not text.strip():
        await _out(message, "❌ Message khali hai.")
        return

    me = message.from_user or await client.get_me()
    try:
        sent = await client.send_message(
            target.id,
            f"🔒 <b>Secret Message</b> from <b>{me.first_name}</b>\n\n"
            f"{text.strip()}\n\n"
            f"⚠️ Auto-delete in <code>{sec}s</code>",
        )
    except Exception as e:
        await _out(
            message,
            f"❌ DM nahi gaya (privacy / block?): <code>{type(e).__name__}: {e}</code>",
        )
        return

    await _out(
        message,
        f"✅ Secret DM → <b>{target.first_name}</b>\n"
        f"⏱ Delete in <code>{sec}s</code>",
    )
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


# ─── Owner helpers ───────────────────────────────────────────
@app.on_message(filters.command(["wlist"], prefixes=P))
async def wlist_cmd(client, message: Message):
    await _out(
        message,
        f"🔒 Active whispers: <code>{len(WHISPERS)}</code>\n"
        f"Clear: <code>{P}wclear</code>",
    )


@app.on_message(filters.command(["wclear"], prefixes=P))
async def wclear_cmd(client, message: Message):
    n = len(WHISPERS)
    WHISPERS.clear()
    await _out(message, f"🗑 Cleared <code>{n}</code> whispers.")
