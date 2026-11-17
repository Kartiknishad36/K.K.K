"""
🔐 Multi-Account Login — dusre ID pe bhi SAME bot chalega

Flow:
  .login +91XXXXXXXXXX
  .otp 12345
  .2fa password          (agar lage)
  .addsession <STRING>

Manage:
  .logins                — list + running status
  .startacc 1            — saved account start (bot ON)
  .stopacc 1             — secondary bot stop
  .delsession 1          — remove + stop
  .mylogin / .cancellogin

Har successful login/add par client auto-start +
main app ke saare handlers copy → us ID pe commands same.
"""
import asyncio
import json
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    SessionPasswordNeeded,
    PhoneCodeInvalid,
    PhoneNumberInvalid,
)

from bot.client import app, logger
import config

P = config.COMMAND_PREFIX
DATA_FILE = Path(getattr(config, "DATA_DIR", Path("data"))) / "extra_sessions.json"
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

PENDING: dict = {}
# user_id -> Client
RUNNING: dict[int, Client] = {}


def _load() -> list:
    if not DATA_FILE.exists():
        return []
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save(rows: list):
    DATA_FILE.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")


async def _out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None


async def _del_cmd(message, delay=1.0):
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except Exception:
        pass


def _uid(message):
    return message.from_user.id if message.from_user else 0


def _patch_dispatcher(client: Client):
    """Same sync patch as main — safe handler add."""
    dispatcher = client.dispatcher

    def sync_add_handler(handler, group: int = 0):
        if group not in dispatcher.groups:
            dispatcher.groups[group] = []
            dispatcher.groups = OrderedDict(sorted(dispatcher.groups.items()))
        dispatcher.groups[group].append(handler)

    def sync_remove_handler(handler, group: int = 0):
        if group not in dispatcher.groups:
            raise ValueError(f"Group {group} missing")
        dispatcher.groups[group].remove(handler)

    dispatcher.add_handler = sync_add_handler
    dispatcher.remove_handler = sync_remove_handler


def _copy_handlers(src: Client, dst: Client) -> int:
    """Main bot ke saare handlers secondary client pe copy."""
    n = 0
    try:
        groups = getattr(src.dispatcher, "groups", {}) or {}
        for group, handlers in list(groups.items()):
            for h in list(handlers):
                try:
                    dst.add_handler(h, group)
                    n += 1
                except Exception as e:
                    logger.debug(f"handler copy skip: {e}")
    except Exception as e:
        logger.error(f"copy_handlers: {e}")
    return n


async def start_account(session_string: str, user_id: int, name: str = "") -> Client | None:
    """Start secondary client + attach same bot handlers."""
    if not session_string or len(session_string) < 20:
        raise ValueError("invalid session string")

    # already running
    if user_id in RUNNING:
        c = RUNNING[user_id]
        if c.is_connected:
            return c
        try:
            await c.stop()
        except Exception:
            pass
        RUNNING.pop(user_id, None)

    client = Client(
        name=f"acc_{user_id}",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        session_string=session_string,
        in_memory=True,
        workers=4,
        no_updates=False,
    )
    _patch_dispatcher(client)
    await client.start()
    me = await client.get_me()
    if me.id != user_id and user_id:
        # trust live id
        user_id = me.id
    copied = _copy_handlers(app, client)
    RUNNING[user_id] = client
    logger.info(
        f"Multi-account START: {me.first_name} [{me.id}] handlers_copied={copied}"
    )
    return client


async def stop_account(user_id: int) -> bool:
    c = RUNNING.pop(user_id, None)
    if not c:
        return False
    try:
        await c.stop()
    except Exception as e:
        logger.error(f"stop_account {user_id}: {e}")
    return True


async def restore_all_accounts():
    """Bot boot pe saari saved sessions start (auto ON)."""
    rows = _load()
    ok = fail = 0
    for r in rows:
        sstr = r.get("session") or ""
        uid = r.get("user_id") or 0
        if not sstr or not uid:
            continue
        try:
            await start_account(sstr, uid, r.get("name") or "")
            ok += 1
        except Exception as e:
            fail += 1
            logger.error(f"restore {uid}: {e}")
    logger.info(f"Multi-account restore: ok={ok} fail={fail} running={len(RUNNING)}")
    return ok, fail


def _help():
    return (
        f"╔════════════════════════════╗\n"
        f"║  🔐  <b>MULTI-ACCOUNT BOT</b>  ║\n"
        f"╚════════════════════════════╝\n\n"
        f"📌 <b>Dusra ID add = us pe bhi same bot</b>\n\n"
        f"📱 <b>Phone login</b>\n"
        f"• <code>{P}login +91XXXXXXXXXX</code>\n"
        f"• <code>{P}otp 12345</code>\n"
        f"• <code>{P}2fa password</code>\n\n"
        f"🔑 <b>Session string</b>\n"
        f"• <code>{P}addsession STRING</code>\n\n"
        f"⚡ <b>Control</b>\n"
        f"• <code>{P}logins</code> — list + 🟢 running\n"
        f"• <code>{P}startacc 1</code> — account start\n"
        f"• <code>{P}stopacc 1</code> — account stop\n"
        f"• <code>{P}delsession 1</code> — delete\n"
        f"• <code>{P}mylogin</code> · <code>{P}cancellogin</code>\n\n"
        f"✅ Login success → auto start + handlers copy\n"
        f"⚠️ OTP / string private me hi bhejo."
    )


@app.on_message(filters.command(["login"], prefixes=P), group=-15)
async def login_cmd(client, message: Message):
    if len(message.command) < 2:
        await _out(message, _help())
        asyncio.create_task(_del_cmd(message))
        return
    phone = message.command[1].strip()
    if not phone.startswith("+") or not any(c.isdigit() for c in phone):
        await _out(message, f"❌ Format: <code>{P}login +9198XXXXXXXX</code>")
        return
    uid = _uid(message)
    status = await _out(message, f"📱 OTP bhej rahe hain → <code>{phone}</code>...")
    try:
        tmp = Client(
            name=f"login_{uid}_{int(datetime.now().timestamp())}",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            in_memory=True,
        )
        await tmp.connect()
        sent = await tmp.send_code(phone)
        PENDING[uid] = {
            "step": "otp",
            "phone": phone,
            "client": tmp,
            "phone_code_hash": sent.phone_code_hash,
        }
        if status:
            await status.edit_text(
                f"✅ OTP bhej diya → <code>{phone}</code>\n"
                f"Ab: <code>{P}otp 12345</code>\n"
                f"Cancel: <code>{P}cancellogin</code>"
            )
    except PhoneNumberInvalid:
        if status:
            await status.edit_text("❌ Invalid phone")
    except Exception as e:
        if status:
            try:
                await status.edit_text(f"❌ <code>{type(e).__name__}: {e}</code>")
            except Exception:
                pass
    asyncio.create_task(_del_cmd(message))


@app.on_message(filters.command(["otp"], prefixes=P), group=-15)
async def otp_cmd(client, message: Message):
    uid = _uid(message)
    st = PENDING.get(uid)
    if not st or st.get("step") != "otp":
        await _out(message, f"❌ Pehle <code>{P}login +phone</code>")
        return
    if len(message.command) < 2:
        await _out(message, f"Usage: <code>{P}otp 12345</code>")
        return
    code = message.command[1].strip()
    tmp = st["client"]
    try:
        await tmp.sign_in(st["phone"], st["phone_code_hash"], code)
    except SessionPasswordNeeded:
        st["step"] = "2fa"
        await _out(message, f"🔒 2FA\n<code>{P}2fa your_password</code>")
        asyncio.create_task(_del_cmd(message, 0.3))
        return
    except PhoneCodeInvalid:
        await _out(message, "❌ OTP galat")
        return
    except Exception as e:
        await _out(message, f"❌ <code>{e}</code>")
        return
    await _finish_and_start(client, message, tmp, uid)


@app.on_message(filters.command(["2fa", "password"], prefixes=P), group=-15)
async def twofa_cmd(client, message: Message):
    uid = _uid(message)
    st = PENDING.get(uid)
    if not st or st.get("step") != "2fa":
        await _out(message, "❌ No 2FA pending")
        return
    if len(message.command) < 2:
        await _out(message, f"Usage: <code>{P}2fa password</code>")
        return
    pwd = message.text.split(None, 1)[1]
    tmp = st["client"]
    try:
        await tmp.check_password(pwd)
    except Exception as e:
        await _out(message, f"❌ 2FA fail: <code>{e}</code>")
        return
    await _finish_and_start(client, message, tmp, uid)


async def _finish_and_start(main_client, message, tmp: Client, owner_uid: int):
    """Export session, save, start live multi-account client."""
    try:
        me = await tmp.get_me()
        try:
            sstr = await tmp.export_session_string()
        except Exception:
            sstr = ""
        phone = PENDING.get(owner_uid, {}).get("phone")
        info = {
            "user_id": me.id,
            "name": f"{me.first_name or ''} {me.last_name or ''}".strip(),
            "username": me.username,
            "session": sstr,
            "phone": phone,
            "added_at": datetime.now(timezone.utc).isoformat(),
            "premium": bool(getattr(me, "is_premium", False)),
            "dc_id": getattr(me, "dc_id", None),
        }
        try:
            await tmp.disconnect()
        except Exception:
            pass
        rows = [r for r in _load() if r.get("user_id") != info["user_id"]]
        rows.append(info)
        _save(rows)
        PENDING.pop(owner_uid, None)

        # LIVE bot on this account
        started = False
        if sstr:
            try:
                await start_account(sstr, info["user_id"], info["name"])
                started = True
            except Exception as e:
                logger.error(f"auto-start after login: {e}")

        try:
            await main_client.send_message(
                "me",
                f"✅ <b>Account linked</b>\n"
                f"👤 {info['name']}\n"
                f"🆔 <code>{info['user_id']}</code>\n"
                f"📱 {phone or '—'}\n"
                f"⚡ Bot live: {'YES 🟢' if started else 'NO — use startacc'}\n"
                f"📦 Total: {len(rows)} | Running: {len(RUNNING)}",
            )
        except Exception:
            pass

        await _out(
            message,
            f"✅ <b>Login success</b>\n"
            f"👤 {info['name']}\n"
            f"🆔 <code>{info['user_id']}</code>\n"
            f"⚡ Same bot is ID pe: <b>{'ON 🟢' if started else 'OFF'}</b>\n"
            f"📋 <code>{P}logins</code>",
        )
    except Exception as e:
        await _out(message, f"❌ <code>{e}</code>")
        PENDING.pop(owner_uid, None)


@app.on_message(filters.command(["addsession"], prefixes=P), group=-15)
async def addsession_cmd(client, message: Message):
    if len(message.command) < 2:
        await _out(message, f"Usage: <code>{P}addsession SESSION_STRING</code>")
        return
    raw = message.text.split(None, 1)[1].strip().strip('"').strip("'")
    asyncio.create_task(_del_cmd(message, 0.2))
    status = await _out(message, "⏳ Session verify + bot start...")
    try:
        # verify first
        tmp = Client(
            name=f"chk_{int(datetime.now().timestamp())}",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=raw,
            in_memory=True,
        )
        await tmp.start()
        me = await tmp.get_me()
        info = {
            "user_id": me.id,
            "name": f"{me.first_name or ''} {me.last_name or ''}".strip(),
            "username": me.username,
            "session": raw,
            "added_at": datetime.now(timezone.utc).isoformat(),
            "premium": bool(getattr(me, "is_premium", False)),
            "dc_id": getattr(me, "dc_id", None),
        }
        await tmp.stop()
    except Exception as e:
        if status:
            await status.edit_text(f"❌ <code>{e}</code>")
        return

    rows = [r for r in _load() if r.get("user_id") != info["user_id"]]
    rows.append(info)
    _save(rows)

    started = False
    try:
        await start_account(raw, info["user_id"], info["name"])
        started = True
    except Exception as e:
        logger.error(f"addsession start: {e}")

    if status:
        await status.edit_text(
            f"✅ <b>{info['name']}</b> added\n"
            f"🆔 <code>{info['user_id']}</code>\n"
            f"⚡ Bot live: <b>{'ON 🟢' if started else 'OFF'}</b>\n"
            f"📦 Saved: {len(rows)} | Running: {len(RUNNING)}\n"
            f"Ab is ID se bhi <code>{P}ping</code> chalega."
        )


@app.on_message(filters.command(["logins", "sessionslist"], prefixes=P), group=-15)
async def logins_cmd(client, message: Message):
    rows = _load()
    if not rows:
        await _out(message, f"📭 Empty\n<code>{P}login +phone</code> ya <code>{P}addsession</code>")
        return
    lines = [f"╔══ 📋 <b>ACCOUNTS</b> ({len(rows)}) ══╗"]
    for i, r in enumerate(rows, 1):
        uid = r.get("user_id")
        live = uid in RUNNING and RUNNING[uid].is_connected
        flag = "🟢 LIVE" if live else "🔴 STOPPED"
        lines.append(
            f"\n<b>{i}.</b> {r.get('name') or 'User'} {flag}\n"
            f"   🆔 <code>{uid}</code>\n"
            f"   🔗 @{r.get('username') or 'None'}\n"
            f"   📱 {r.get('phone') or '—'}"
        )
    lines.append(
        f"\n⚡ <code>{P}startacc 1</code> · 🛑 <code>{P}stopacc 1</code>\n"
        f"🗑 <code>{P}delsession 1</code>\n"
        f"Running now: <code>{len(RUNNING)}</code>\n"
        f"╚════════════════════╝"
    )
    await _out(message, "\n".join(lines))


def _pick_row(arg: str):
    rows = _load()
    if not arg.isdigit():
        return None, rows, None
    n = int(arg)
    if 1 <= n <= len(rows):
        return rows[n - 1], rows, n - 1
    for i, r in enumerate(rows):
        if r.get("user_id") == n:
            return r, rows, i
    return None, rows, None


@app.on_message(filters.command(["startacc", "runacc"], prefixes=P), group=-15)
async def startacc_cmd(client, message: Message):
    if len(message.command) < 2:
        await _out(message, f"Usage: <code>{P}startacc 1</code>")
        return
    row, rows, idx = _pick_row(message.command[1])
    if not row:
        await _out(message, "❌ Account nahi mila")
        return
    sstr = row.get("session") or ""
    if not sstr:
        await _out(message, "❌ Session string missing — re-login")
        return
    status = await _out(message, "⚡ Starting bot on account...")
    try:
        await start_account(sstr, row["user_id"], row.get("name") or "")
        if status:
            await status.edit_text(
                f"🟢 <b>LIVE</b>\n👤 {row.get('name')}\n🆔 <code>{row.get('user_id')}</code>\n"
                f"Ab is ID pe bhi same commands chalenge."
            )
    except Exception as e:
        if status:
            await status.edit_text(f"❌ <code>{e}</code>")


@app.on_message(filters.command(["stopacc"], prefixes=P), group=-15)
async def stopacc_cmd(client, message: Message):
    if len(message.command) < 2:
        await _out(message, f"Usage: <code>{P}stopacc 1</code>")
        return
    row, rows, idx = _pick_row(message.command[1])
    if not row:
        await _out(message, "❌ Not found")
        return
    ok = await stop_account(row["user_id"])
    await _out(
        message,
        f"🛑 Stopped <b>{row.get('name')}</b>" if ok else "ℹ️ Already stopped",
    )


@app.on_message(filters.command(["delsession", "logoutlogin"], prefixes=P), group=-15)
async def delsession_cmd(client, message: Message):
    if len(message.command) < 2:
        await _out(message, f"<code>{P}delsession 1</code>")
        return
    row, rows, idx = _pick_row(message.command[1])
    if not row or idx is None:
        await _out(message, "❌ Not found")
        return
    await stop_account(row.get("user_id") or 0)
    rows.pop(idx)
    _save(rows)
    await _out(message, f"🗑 Removed <b>{row.get('name')}</b>")


@app.on_message(filters.command(["mylogin"], prefixes=P), group=-15)
async def mylogin_cmd(client, message: Message):
    me = await client.get_me()
    await _out(
        message,
        f"╔══ 👤 <b>MAIN</b> ══╗\n"
        f"✨ {me.first_name}\n"
        f"🆔 <code>{me.id}</code>\n"
        f"📦 Saved: {len(_load())}\n"
        f"🟢 Running: {len(RUNNING)}\n"
        f"╚══════════════╝",
    )


@app.on_message(filters.command(["cancellogin"], prefixes=P), group=-15)
async def cancellogin_cmd(client, message: Message):
    uid = _uid(message)
    st = PENDING.pop(uid, None)
    if st and st.get("client"):
        try:
            await st["client"].disconnect()
        except Exception:
            pass
    await _out(message, "🛑 Cancelled" if st else "ℹ️ Nothing pending")
