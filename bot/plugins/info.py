"""Enhanced .info / .whois — full user report"""
from datetime import datetime, timezone
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType, ChatMemberStatus, UserStatus
import config
from bot.database import db

DC_MAP = {1: "Miami, FL, USA", 2: "Amsterdam, NL", 3: "Miami, FL, USA", 4: "Amsterdam, NL", 5: "Singapore"}

def _yn(v):
    return "✅ Yes" if v else "❌ No"

def _status_line(status):
    if status is None: return "Hidden / Unknown"
    if status == UserStatus.ONLINE: return "🟢 Online"
    if status == UserStatus.OFFLINE:
        was = getattr(status, "was_online", None)
        return f"⚫ Offline · last seen {was}" if was else "⚫ Offline"
    if status == UserStatus.RECENTLY: return "🟡 Recently"
    if status == UserStatus.LAST_WEEK: return "🟠 Last week"
    if status == UserStatus.LAST_MONTH: return "🔴 Last month"
    return str(status)

def _member_status(st):
    return {ChatMemberStatus.OWNER: "👑 Owner", ChatMemberStatus.ADMINISTRATOR: "🛡 Admin",
            ChatMemberStatus.MEMBER: "👤 Member", ChatMemberStatus.RESTRICTED: "🚫 Restricted",
            ChatMemberStatus.LEFT: "🚪 Left", ChatMemberStatus.BANNED: "⛔ Banned"}.get(st, str(st))

def _approx_reg(uid):
    try: uid = int(uid)
    except Exception: return "—"
    for threshold, label in [(10**9,"2020+"),(5*10**8,"2018–2020"),(2*10**8,"2016–2018"),(10**8,"2015–2016"),(5*10**7,"2014–2015"),(10**7,"2013–2014"),(10**6,"2013 early"),(0,"early")]:
        if uid >= threshold: return label
    return "—"

@Client.on_message(filters.command(["info", "whois"], prefixes=config.COMMAND_PREFIX) & filters.me)
async def info_cmd(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user.id
    else:
        parts = (message.text or "").split()
        target = parts[1].lstrip("@") if len(parts) > 1 else "me"
    status_msg = await message.edit_text("⏳ **Scanning user…**")
    try:
        user = await client.get_users(target)
        try: chat = await client.get_chat(user.id)
        except Exception: chat = None
        common_list = []
        try: common_list = await client.get_common_chats(user.id)
        except Exception: pass
        full = (user.first_name or "") + (f" {user.last_name}" if user.last_name else "")
        bio = getattr(chat, "bio", None) or "—"
        status = _status_line(getattr(user, "status", None))
        is_owner = user.id == config.OWNER_ID
        link = f"[{full or user.id}](tg://user?id={user.id})"
        photo_n = 0
        try:
            async for _ in client.get_chat_photos(user.id, limit=50): photo_n += 1
        except Exception: pass
        dc = getattr(user, "dc_id", None)
        dc_loc = DC_MAP.get(dc, "Unknown") if dc else "—"
        lines = [
            "╔════════════════════════════╗", "║   💎 **FULL USER INFO**    ║", "╚════════════════════════════╝", "",
            "**─── Identity ───**", f"👤 Name: **{full or '—'}**", f"🔖 Username: @{user.username or '—'}",
            f"🆔 User ID: `{user.id}`", f"🔗 Profile: {link}",
            f"🌐 t.me: " + (f"https://t.me/{user.username}" if user.username else "—"), "",
            "**─── Presence ───**", f"📡 Status: {status}", f"🗣 Language: `{getattr(user, 'language_code', None) or '—'}`",
            f"🏛 DC ID: `{dc or '—'}` ({dc_loc})", f"📅 Approx. era: `{_approx_reg(user.id)}`", f"📝 Bio: {str(bio)[:300]}", "",
            "**─── Flags ───**", f"⭐ Premium: {_yn(getattr(user, 'is_premium', False))}", f"✅ Verified: {_yn(getattr(user, 'is_verified', False))}",
            f"🤖 Bot: {_yn(user.is_bot)}", f"🗑 Deleted: {_yn(getattr(user, 'is_deleted', False))}",
            f"🎭 Fake: {_yn(getattr(user, 'is_fake', False))}", f"⚠️ Scam: {_yn(getattr(user, 'is_scam', False))}",
            f"👑 Is OWNER: {_yn(is_owner)}", "", "**─── Media ───**", f"🖼 Profile photos: `{photo_n}`", f"👀 Common chats: `{len(common_list)}`",
        ]
        gban = await db.is_gbanned(user.id)
        if gban:
            lines += ["", f"⚠️ **Globally Banned**\nReason: {gban.get('reason', '—')}"]
        if message.chat and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
            lines += ["", "**─── This chat ───**", f"Chat: {message.chat.title or message.chat.id}"]
            try:
                member = await client.get_chat_member(message.chat.id, user.id)
                lines.append(f"Status: {_member_status(member.status)}")
            except Exception:
                lines.append("Status: not in chat / hidden")
            try:
                warns = await db.get_warnings(user.id, message.chat.id)
                lines.append(f"Warnings: `{warns}`")
            except Exception: pass
        if common_list:
            lines += ["", "**─── Common chats (sample) ───**"]
            for ch in common_list[:15]:
                lines.append(f"• {ch.title or ch.first_name or ch.id} (`{ch.id}`)")
        lines += ["", f"⏱ `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}`"]
        text = "\n".join(lines)
        if len(text) > 4000: text = text[:3990] + "\n…"
        await status_msg.edit_text(text)
    except Exception as e:
        await status_msg.edit_text(f"❌ `{type(e).__name__}: {e}`")
