"""
👤 User Info — ~50 fields + DP
.info / .whois [reply|@user|id]
"""
from datetime import datetime, timezone
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType, ChatMemberStatus
from bot.client import app
import config

P = config.COMMAND_PREFIX

async def _out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

async def _resolve_user(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    if len(message.command) > 1:
        try:
            return await client.get_users(message.command[1])
        except Exception:
            return None
    return message.from_user

@app.on_message(filters.command(["info", "whois", "userinfo"], prefixes=P))
async def info_cmd(client, message: Message):
    user = await _resolve_user(client, message)
    if not user:
        await _out(message, f"❌ User nahi mila\n<code>{P}info</code> reply/@user/id")
        return
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "User"
    username = f"@{user.username}" if user.username else "None"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "╔══════════════════════════╗",
        "║  👤  <b>USER INFORMATION</b>  ║",
        "╚══════════════════════════╝",
        "",
        "┌─ ✨ <b>Identity</b>",
        f"│ 01 Name: <b>{full_name}</b>",
        f"│ 02 ID: <code>{user.id}</code>",
        f"│ 03 Username: {username}",
        f"│ 04 Mention: {user.mention}",
        f"│ 05 Profile: <a href=\"tg://user?id={user.id}\">Open</a>",
        "├─ 💎 <b>Flags</b>",
        f"│ 06 Premium: {'Yes ✅' if getattr(user, 'is_premium', False) else 'No'}",
        f"│ 07 Verified: {getattr(user, 'is_verified', False)}",
        f"│ 08 Bot: {'Yes' if user.is_bot else 'No'}",
        f"│ 09 Scam: {getattr(user, 'is_scam', False)}",
        f"│ 10 Fake: {getattr(user, 'is_fake', False)}",
        f"│ 11 Restricted: {getattr(user, 'is_restricted', False)}",
        f"│ 12 Deleted: {getattr(user, 'is_deleted', False)}",
        f"│ 13 Support: {getattr(user, 'is_support', False)}",
        "├─ 📡 <b>Network</b>",
        f"│ 14 DC ID: {getattr(user, 'dc_id', 'N/A')}",
        f"│ 15 Lang: {getattr(user, 'language_code', 'N/A')}",
        f"│ 16 Status: {getattr(user, 'status', 'N/A')}",
        f"│ 17 Last online: {getattr(user, 'last_online_date', 'N/A')}",
    ]
    try:
        chat = await client.get_chat(user.id)
        bio = getattr(chat, "bio", None) or "None"
        lines += ["├─ 📝 <b>Profile</b>", f"│ 18 Bio: {bio[:120]}"]
    except Exception:
        lines += ["├─ 📝 Bio: N/A"]
    if user.photo:
        lines += [
            "├─ 🖼 <b>Photo</b>",
            "│ 20 Has DP: Yes ✅",
            f"│ 21 file_id: <code>{user.photo.big_file_id[:28]}...</code>",
        ]
    else:
        lines += ["├─ 🖼 Has DP: No"]
    if message.chat and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        lines.append("├─ 👥 <b>This Group</b>")
        try:
            m = await client.get_chat_member(message.chat.id, user.id)
            lines.append(f"│ 23 Status: {m.status}")
            priv = getattr(m, "privileges", None)
            if priv:
                lines += [
                    f"│ 24 Manage: {getattr(priv, 'can_manage_chat', False)}",
                    f"│ 25 Delete: {getattr(priv, 'can_delete_messages', False)}",
                    f"│ 26 Restrict: {getattr(priv, 'can_restrict_members', False)}",
                    f"│ 27 Promote: {getattr(priv, 'can_promote_members', False)}",
                    f"│ 28 Invite: {getattr(priv, 'can_invite_users', False)}",
                    f"│ 29 Pin: {getattr(priv, 'can_pin_messages', False)}",
                ]
        except Exception as e:
            lines.append(f"│ 23 Member: {type(e).__name__}")
        lines += [f"│ 31 Chat: <code>{message.chat.id}</code>", f"│ 32 Title: {message.chat.title}"]
    lines += [
        "├─ 🔧 <b>Meta</b>",
        f"│ 40 Prefix: <code>{P}</code>",
        f"│ 41 Time: {now}",
        f"│ 42 By: <code>{message.from_user.id if message.from_user else 'N/A'}</code>",
        f"│ 45 Contact: {getattr(user, 'is_contact', False)}",
        f"│ 46 Mutual: {getattr(user, 'is_mutual_contact', False)}",
        f"│ 48 Link: tg://user?id={user.id}",
        f"│ 49 t.me/{user.username}" if user.username else "│ 49 t.me: None",
        f"│ 50 Name len: {len(full_name)}",
        "└──────────────────────────",
    ]
    text = "\n".join(lines)
    try:
        if user.photo:
            path = await client.download_media(user.photo.big_file_id)
            await message.reply_photo(path, caption=text[:1024])
            if len(text) > 1024:
                await message.reply_text(text[1024:4000])
            return
    except Exception:
        pass
    await _out(message, text[:4000])
