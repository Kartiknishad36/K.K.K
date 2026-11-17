"""
🔐 Multi-Account Login Manager
Add / list / remove other user accounts (session strings).

Commands:
  .login          — help menu
  .addsession     — add another account session
  .logins         — list saved accounts
  .delsession     — remove account by id/index
  .mylogin        — main account status
  .cancellogin    — cancel pending add
  .logoutlogin    — alias delsession help
"""
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.client import app
import config

P = config.COMMAND_PREFIX
DATA_FILE = Path(getattr(config, "DATA_DIR", Path("data"))) / "extra_sessions.json"
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

PENDING: dict[int, dict] = {}
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


async def _out(message: Message, text: str):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None


async def _del_cmd(message: Message, delay: float = 1.0):
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except Exception:
        pass


def _help() -> str:
    return (
        f"╔══════════════════════════╗\n"
        f"║  🔐  <b>MULTI LOGIN</b>  ║\n"
        f"╚══════════════════════════╝\n\n"
        f"📌 <b>Dusre account add karo</b> (session string se)\n\n"
        f"✨ <b>Commands</b>\n"
        f"• <code>{P}addsession</code> — naya account add\n"
        f"• <code>{P}addsession &lt;string&gt;</code> — direct string\n"
        f"• <code>{P}logins</code> — saved accounts list\n"
        f"• <code>{P}delsession &lt;no|#id&gt;</code> — account hatao\n"
        f"• <code>{P}mylogin</code> — main account status\n"
        f"• <code>{P}cancellogin</code> — pending cancel\n"
        f"• <code>{P}login</code> — yeh help\n\n"
        f"⚠️ Session string <b>sirf private / Saved Messages</b> me bhejo.\n"
        f"Group me mat paste karo.\n"
    )


@app.on_message(filters.command(["login"], prefixes=P), group=-15)
async def login_help(client, message: Message):
    await _out(message, _help())
    asyncio.create_task(_del_cmd(message))


@app.on_message(filters.command(["mylogin"], prefixes=P), group=-15)
async def mylogin_cmd(client, message: Message):
    me = await client.get_me()
    rows = _load()
    text = (
        f"╔══ 👤 <b>MAIN ACCOUNT</b> ══╗\n"
        f"✨ Name: <b>{me.first_name}</b>\n"
        f"🆔 ID: <code>{me.id}</code>\n"
        f"🔗 Username: {'@' + me.username if me.username else 'None'}\n"
        f"💎 Premium: {getattr(me, 'is_premium', False)}\n"
        f"📡 DC: {getattr(me, 'dc_id', 'N/A')}\n"
        f"📦 Extra accounts saved: <code>{len(rows)}</code>\n"
        f"⚡ Running extra clients: <code>{len(RUNNING)}</code>\n"
        f"🕒 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"╚════════════════════╝"
    )
    await _out(message, text)
    asyncio.create_task(_del_cmd(message))


@app.on_message(filters.command(["addsession"], prefixes=P), group=-15)
async def addsession_cmd(client, message: Message):
    uid = message.from_user.id if message.from_user else 0
    owner = getattr(config, "OWNER_ID", 0) or 0
    if owner and uid and uid != owner and not getattr(message, "outgoing", False):
        await _out(message, "❌ Sirf owner extra account add kar sakta hai.")
        asyncio.create_task(_del_cmd(message))
        return

    if len(message.command) > 1:
        raw = message.text.split(None, 1)[1].strip()
        asyncio.create_task(_del_cmd(message, 0.3))
        await _register_session(client, message, raw)
        return

    PENDING[uid or 0] = {"step": "wait_string"}
    await _out(
        message,
        f"🔐 <b>Add Account</b>\n\n"
        f"Ab <b>session string</b> bhejo (next message).\n"
        f"Cancel: <code>{P}cancellogin</code>\n\n"
        f"⚠️ Private / Saved Messages recommended.",
    )
    asyncio.create_task(_del_cmd(message))


@app.on_message(filters.text & ~filters.via_bot, group=-14)
async def addsession_capture(client, message: Message):
    uid = message.from_user.id if message.from_user else 0
    if uid not in PENDING:
        me_pending = None
        for k, v in list(PENDING.items()):
            if v.get("step") == "wait_string":
                me_pending = k
                break
        if me_pending is None:
            return
        uid = me_pending
    if PENDING.get(uid, {}).get("step") != "wait_string":
        return
    text = (message.text or "").strip()
    if not text or text.startswith(P):
        return
    PENDING.pop(uid, None)
    asyncio.create_task(_del_cmd(message, 0.2))
    await _register_session(client, message, text)


async def _register_session(client, message: Message, session_string: str):
    session_string = session_string.strip().strip('"').strip("'")
    if len(session_string) < 20:
        await _out(message, "❌ Session string bahut short / invalid.")
        return

    status = await _out(message, "⏳ Session verify kar raha hoon...")
    try:
        tmp = Client(
            name=f"extra_{int(datetime.now().timestamp())}",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=session_string,
            in_memory=True,
        )
        await tmp.start()
        me = await tmp.get_me()
        info = {
            "user_id": me.id,
            "name": f"{me.first_name or ''} {me.last_name or ''}".strip(),
            "username": me.username,
            "session": session_string,
            "added_at": datetime.now(timezone.utc).isoformat(),
            "premium": bool(getattr(me, "is_premium", False)),
            "dc_id": getattr(me, "dc_id", None),
        }
        await tmp.stop()
    except Exception as e:
        if status:
            try:
                await status.edit_text(f"❌ Session invalid:\n<code>{type(e).__name__}: {e}</code>")
            except Exception:
                pass
        return

    rows = _load()
    rows = [r for r in rows if r.get("user_id") != info["user_id"]]
    rows.append(info)
    _save(rows)

    try:
        await client.send_message(
            "me",
            f"✅ <b>Extra account added</b>\n"
            f"👤 {info['name']}\n"
            f"🆔 <code>{info['user_id']}</code>\n"
            f"🔗 @{info['username'] or 'None'}\n"
            f"💎 Premium: {info['premium']}\n"
            f"📦 Total saved: {len(rows)}\n"
            f"🕒 {info['added_at']}",
        )
    except Exception:
        pass

    msg = (
        f"✅ <b>Account added</b>\n\n"
        f"👤 <b>{info['name']}</b>\n"
        f"🆔 <code>{info['user_id']}</code>\n"
        f"🔗 @{info['username'] or 'None'}\n"
        f"💎 Premium: {info['premium']}\n"
        f"📡 DC: {info['dc_id']}\n"
        f"📦 Total: <code>{len(rows)}</code>\n\n"
        f"List: <code>{P}logins</code>"
    )
    if status:
        try:
            await status.edit_text(msg)
            return
        except Exception:
            pass
    await _out(message, msg)


@app.on_message(filters.command(["logins", "sessionslist"], prefixes=P), group=-15)
async def logins_cmd(client, message: Message):
    rows = _load()
    if not rows:
        await _out(message, f"📭 Koi extra account nahi.\nAdd: <code>{P}addsession</code>")
        asyncio.create_task(_del_cmd(message))
        return
    lines = [f"╔══ 📋 <b>SAVED ACCOUNTS</b> ({len(rows)}) ══╗"]
    for i, r in enumerate(rows, 1):
        lines.append(
            f"\n<b>{i}.</b> {r.get('name') or 'User'}\n"
            f"   🆔 <code>{r.get('user_id')}</code>\n"
            f"   🔗 @{r.get('username') or 'None'}\n"
            f"   💎 {r.get('premium', False)} | 📡 DC {r.get('dc_id', 'N/A')}\n"
            f"   🕒 {str(r.get('added_at', ''))[:19]}"
        )
    lines.append(f"\n🗑 Remove: <code>{P}delsession 1</code>")
    lines.append("╚════════════════════╝")
    await _out(message, "\n".join(lines))
    asyncio.create_task(_del_cmd(message))


@app.on_message(filters.command(["delsession", "logoutlogin"], prefixes=P), group=-15)
async def delsession_cmd(client, message: Message):
    rows = _load()
    if len(message.command) < 2:
        await _out(message, f"Usage:\n<code>{P}delsession 1</code>\n<code>{P}delsession 123456789</code>")
        asyncio.create_task(_del_cmd(message))
        return
    arg = message.command[1].lstrip("#")
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
        await _out(message, "❌ Account nahi mila.")
        asyncio.create_task(_del_cmd(message))
        return
    _save(rows)
    uid = removed.get("user_id")
    if uid in RUNNING:
        try:
            await RUNNING[uid].stop()
        except Exception:
            pass
        RUNNING.pop(uid, None)
    await _out(
        message,
        f"🗑 Removed: <b>{removed.get('name')}</b> (<code>{uid}</code>)\nRemaining: <code>{len(rows)}</code>",
    )
    asyncio.create_task(_del_cmd(message))


@app.on_message(filters.command(["cancellogin"], prefixes=P), group=-15)
async def cancellogin_cmd(client, message: Message):
    uid = message.from_user.id if message.from_user else 0
    if uid in PENDING or 0 in PENDING:
        PENDING.pop(uid, None)
        PENDING.pop(0, None)
        await _out(message, "🛑 Pending addsession cancel.")
    else:
        await _out(message, "ℹ️ Koi pending login nahi.")
    asyncio.create_task(_del_cmd(message))
