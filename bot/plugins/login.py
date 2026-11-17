"""
🔐 Multi-account Login — phone OTP + session string
.login +91XXXXXXXXXX → .otp CODE → .2fa PASS
.addsession STRING / .logins / .delsession / .mylogin / .cancellogin
"""
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PhoneNumberInvalid
from bot.client import app
import config

P = config.COMMAND_PREFIX
DATA_FILE = Path(getattr(config, "DATA_DIR", Path("data"))) / "extra_sessions.json"
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
PENDING = {}
RUNNING = {}

def _load():
    if not DATA_FILE.exists():
        return []
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def _save(rows):
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

def _help():
    return (
        f"╔══════════════════════════╗\n"
        f"║  🔐  <b>MULTI LOGIN</b>  ║\n"
        f"╚══════════════════════════╝\n\n"
        f"📱 <b>Number se login</b>\n"
        f"1️⃣ <code>{P}login +91XXXXXXXXXX</code>\n"
        f"2️⃣ <code>{P}otp 12345</code>\n"
        f"3️⃣ <code>{P}2fa password</code> (agar lage)\n\n"
        f"🔑 <code>{P}addsession STRING</code>\n"
        f"📋 <code>{P}logins</code> · <code>{P}delsession 1</code>\n"
        f"👤 <code>{P}mylogin</code> · 🛑 <code>{P}cancellogin</code>\n\n"
        f"⚠️ OTP/2FA/string private me bhejo."
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
    await _finish_client(client, message, tmp, uid)

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
    await _finish_client(client, message, tmp, uid)

async def _finish_client(main_client, message, tmp, uid):
    try:
        me = await tmp.get_me()
        try:
            sstr = await tmp.export_session_string()
        except Exception:
            sstr = ""
        info = {
            "user_id": me.id,
            "name": f"{me.first_name or ''} {me.last_name or ''}".strip(),
            "username": me.username,
            "session": sstr,
            "phone": PENDING.get(uid, {}).get("phone"),
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
        PENDING.pop(uid, None)
        try:
            await main_client.send_message(
                "me",
                f"✅ <b>Login OK</b>\n👤 {info['name']}\n🆔 <code>{info['user_id']}</code>\n📱 {info.get('phone')}\n📦 {len(rows)}",
            )
        except Exception:
            pass
        await _out(message, f"✅ <b>Login success</b>\n👤 {info['name']}\n🆔 <code>{info['user_id']}</code>\n<code>{P}logins</code>")
    except Exception as e:
        await _out(message, f"❌ <code>{e}</code>")
        PENDING.pop(uid, None)

@app.on_message(filters.command(["addsession"], prefixes=P), group=-15)
async def addsession_cmd(client, message: Message):
    if len(message.command) < 2:
        await _out(message, f"Usage: <code>{P}addsession SESSION_STRING</code>")
        return
    raw = message.text.split(None, 1)[1].strip().strip('"').strip("'")
    asyncio.create_task(_del_cmd(message, 0.2))
    status = await _out(message, "⏳ Verify...")
    try:
        tmp = Client(name=f"extra_{int(datetime.now().timestamp())}", api_id=config.API_ID, api_hash=config.API_HASH, session_string=raw, in_memory=True)
        await tmp.start()
        me = await tmp.get_me()
        info = {"user_id": me.id, "name": f"{me.first_name or ''} {me.last_name or ''}".strip(), "username": me.username, "session": raw, "added_at": datetime.now(timezone.utc).isoformat(), "premium": bool(getattr(me, "is_premium", False)), "dc_id": getattr(me, "dc_id", None)}
        await tmp.stop()
    except Exception as e:
        if status:
            await status.edit_text(f"❌ <code>{e}</code>")
        return
    rows = [r for r in _load() if r.get("user_id") != info["user_id"]]
    rows.append(info)
    _save(rows)
    if status:
        await status.edit_text(f"✅ <b>{info['name']}</b>\n🆔 <code>{info['user_id']}</code>\n📦 {len(rows)}")

@app.on_message(filters.command(["logins", "sessionslist"], prefixes=P), group=-15)
async def logins_cmd(client, message: Message):
    rows = _load()
    if not rows:
        await _out(message, f"📭 Empty\n<code>{P}login +phone</code>")
        return
    lines = [f"╔══ 📋 <b>ACCOUNTS</b> ({len(rows)}) ══╗"]
    for i, r in enumerate(rows, 1):
        lines.append(f"\n<b>{i}.</b> {r.get('name')}\n   🆔 <code>{r.get('user_id')}</code>\n   🔗 @{r.get('username') or 'None'}\n   📱 {r.get('phone') or '—'}")
    lines.append(f"\n🗑 <code>{P}delsession 1</code>")
    await _out(message, "\n".join(lines))

@app.on_message(filters.command(["delsession", "logoutlogin"], prefixes=P), group=-15)
async def delsession_cmd(client, message: Message):
    rows = _load()
    if len(message.command) < 2:
        await _out(message, f"<code>{P}delsession 1</code>")
        return
    arg = message.command[1]
    removed = None
    if arg.isdigit():
        n = int(arg)
        if 1 <= n <= len(rows):
            removed = rows.pop(n - 1)
        else:
            for i, r in enumerate(rows):
                if r.get("user_id") == n:
                    removed = rows.pop(i)
                    break
    if not removed:
        await _out(message, "❌ Not found")
        return
    _save(rows)
    await _out(message, f"🗑 Removed <b>{removed.get('name')}</b>")

@app.on_message(filters.command(["mylogin"], prefixes=P), group=-15)
async def mylogin_cmd(client, message: Message):
    me = await client.get_me()
    await _out(message, f"╔══ 👤 <b>MAIN</b> ══╗\n✨ {me.first_name}\n🆔 <code>{me.id}</code>\n📦 Extra: {len(_load())}\n╚══════════════╝")

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
