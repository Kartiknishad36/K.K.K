"""
Userbot .login DISABLED — interactive login SIRF env / BOT se.

Commands:
  .login .cancellogin .logoutlogin .addsession .mylogin .logins

- Command message auto-delete after reply
- Full status + details → Saved Messages (me)
- Session string never printed in public chats
"""
import asyncio
from datetime import datetime, timezone

from pyrogram import filters
from pyrogram.types import Message

from bot.client import app
import config

P = config.COMMAND_PREFIX

# delay before deleting the user's command message (seconds)
CMD_DELETE_AFTER = 1.0
# delay before deleting the bot reply in chat (0 = keep)
REPLY_DELETE_AFTER = 0

LOGIN_CMDS = [
    "login",
    "cancellogin",
    "logoutlogin",
    "addsession",
    "mylogin",
    "logins",
    "sessionlogin",
]


def _owner_ok(message: Message) -> bool:
    uid = message.from_user.id if message.from_user else 0
    owner = getattr(config, "OWNER_ID", 0) or 0
    if not owner:
        return True  # no owner set → allow self-userbot
    return uid == owner or (message.outgoing if hasattr(message, "outgoing") else False)


async def _safe_delete(msg: Message | None):
    if not msg:
        return
    try:
        await msg.delete()
    except Exception:
        pass


async def _auto_del_cmd(message: Message):
    """Delete the command message itself."""
    try:
        await asyncio.sleep(CMD_DELETE_AFTER)
        await message.delete()
    except Exception:
        pass


async def _to_saved(client, text: str):
    """Send detailed log to Saved Messages only (never public)."""
    try:
        await client.send_message("me", text)
        return True
    except Exception:
        return False


async def _reply(message: Message, text: str):
    try:
        r = await message.reply_text(text)
    except Exception:
        try:
            r = await message.edit_text(text)
        except Exception:
            r = None
    asyncio.create_task(_auto_del_cmd(message))
    if r and REPLY_DELETE_AFTER > 0:

        async def _later():
            await asyncio.sleep(REPLY_DELETE_AFTER)
            await _safe_delete(r)

        asyncio.create_task(_later())
    return r


def _login_help() -> str:
    return (
        f"╔══ 🔐 <b>LOGIN MODULE</b> ══╗\n\n"
        f"<b>Status:</b> Userbot interactive login is <b>DISABLED</b>\n\n"
        f"📌 <b>Why?</b>\n"
        f"• Session chat me leak na ho\n"
        f"• Phone/OTP/2FA public group me unsafe\n"
        f"• Production me <code>SESSION_STRING</code> env use karo\n\n"
        f"📌 <b>Kaise login kare?</b>\n"
        f"1. Local / VPS pe StringSession banao\n"
        f"2. Render/Railway env me set karo:\n"
        f"   <code>API_ID</code> <code>API_HASH</code> <code>SESSION_STRING</code> <code>OWNER_ID</code>\n"
        f"3. Deploy → userbot start\n\n"
        f"📌 <b>Commands (info only)</b>\n"
        f"• <code>{P}login</code> — ye help + Saved Messages log\n"
        f"• <code>{P}mylogin</code> — current account details (Saved)\n"
        f"• <code>{P}logins</code> — same as mylogin\n"
        f"• <code>{P}addsession</code> — session add guide\n"
        f"• <code>{P}cancellogin</code> — no active flow\n"
        f"• <code>{P}logoutlogin</code> — no active flow\n"
        f"• <code>{P}sessions</code> — session.py full info\n\n"
        f"📌 <b>Auto-delete</b>\n"
        f"• Command message ~{CMD_DELETE_AFTER}s me delete\n"
        f"• Full details sirf <b>Saved Messages</b> me\n\n"
        f"╚══════════════════════╝"
    )


async def _session_details(client) -> str:
    me = await client.get_me()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "╔══ 🔐 LOGIN / SESSION DETAILS ══╗",
        f"01 Time: {now}",
        f"02 Name: {me.first_name} {me.last_name or ''}".strip(),
        f"03 User ID: `{me.id}`",
        f"04 Username: @{me.username}" if me.username else "04 Username: None",
        f"05 Premium: {getattr(me, 'is_premium', False)}",
        f"06 Verified: {getattr(me, 'is_verified', False)}",
        f"07 Restricted: {getattr(me, 'is_restricted', False)}",
        f"08 Scam: {getattr(me, 'is_scam', False)}",
        f"09 Fake: {getattr(me, 'is_fake', False)}",
        f"10 Bot flag: {me.is_bot}",
        f"11 DC ID: {getattr(me, 'dc_id', 'N/A')}",
        f"12 Language: {getattr(me, 'language_code', 'N/A')}",
        f"13 Session name: `{getattr(config, 'SESSION_NAME', 'N/A')}`",
        f"14 SESSION_STRING set: {bool(getattr(config, 'SESSION_STRING', None))}",
        f"15 API_ID set: {bool(getattr(config, 'API_ID', None))}",
        f"16 API_HASH set: {bool(getattr(config, 'API_HASH', None))}",
        f"17 OWNER_ID: `{getattr(config, 'OWNER_ID', 0)}`",
        f"18 Prefix: `{P}`",
        f"19 Interactive login: DISABLED",
        f"20 OTP flow: N/A (use env session)",
        f"21 2FA flow: N/A (use env session)",
        f"22 Public chat login: BLOCKED",
        f"23 Saved Messages log: YES",
        f"24 Command auto-delete: {CMD_DELETE_AFTER}s",
        "25 Note: Session string kabhi group me mat bhejo",
        "└─ END LOGIN DETAILS",
    ]
    return "\n".join(lines)


@app.on_message(
    filters.command(LOGIN_CMDS, prefixes=P),
    group=-15,
)
async def login_module(client, message: Message):
    cmd = (message.command[0] if message.command else "login").lower()

    # public short reply
    if cmd in ("login", "sessionlogin"):
        await _reply(message, _login_help())
        # full dump → Saved Messages
        detail = await _session_details(client)
        await _to_saved(
            client,
            detail
            + "\n\n"
            + f"Trigger: <code>{P}{cmd}</code>\n"
            + f"Chat: `{message.chat.id if message.chat else 'N/A'}`\n"
            + f"From: `{message.from_user.id if message.from_user else 'N/A'}`",
        )
        return

    if cmd in ("mylogin", "logins"):
        detail = await _session_details(client)
        ok = await _to_saved(client, detail)
        await _reply(
            message,
            "✅ Full login/session details <b>Saved Messages</b> me bhej diye.\n"
            if ok
            else "⚠️ Saved Messages fail — check session.\n" + detail[:800],
        )
        return

    if cmd == "addsession":
        guide = (
            f"╔══ 📎 <b>ADD SESSION GUIDE</b> ══╗\n\n"
            f"1. Pyrogram StringSession generate karo (local)\n"
            f"2. Host env variables:\n"
            f"   <code>API_ID=...</code>\n"
            f"   <code>API_HASH=...</code>\n"
            f"   <code>SESSION_STRING=...</code>\n"
            f"   <code>OWNER_ID=...</code>\n"
            f"   <code>COMMAND_PREFIX=.</code>\n\n"
            f"3. Redeploy service\n"
            f"4. Check: <code>{P}sessions</code> / <code>{P}mylogin</code>\n\n"
            f"⚠️ String session chat me paste mat karo.\n"
            f"╚══════════════════════╝"
        )
        await _reply(message, guide)
        await _to_saved(client, guide + f"\n\nChat: `{message.chat.id}`")
        return

    if cmd in ("cancellogin", "logoutlogin"):
        await _reply(
            message,
            f"ℹ️ Koi active interactive login flow nahi hai.\n"
            f"Userbot login chat se band hai.\n"
            f"Details: <code>{P}login</code>",
        )
        await _to_saved(
            client,
            f"🔐 {P}{cmd} used — no active OTP flow\n"
            f"Time: {datetime.now(timezone.utc).isoformat()}\n"
            f"Chat: `{message.chat.id}`",
        )
        return

    # fallback
    await _reply(message, _login_help())
