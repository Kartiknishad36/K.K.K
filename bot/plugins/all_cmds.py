"""K.K.K UserBot — ALL commands in one module (styled + working)"""
import asyncio
import html
from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatType, ChatMembersFilter
from pyrogram.errors import FloodWait

from bot.client import app, logger
import config

try:
    from bot.database import db
except Exception:
    db = None

P = (config.COMMAND_PREFIX or ".").strip() or "."


def cmd(*names):
    return filters.command(list(names), prefixes=[P, "!", "/"])


async def reply(message: Message, text: str):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            try:
                return await app.send_message(message.chat.id, text)
            except Exception as e:
                logger.error(f"reply fail: {e}")
                return None


def mention(u) -> str:
    if not u:
        return "User"
    name = html.escape(u.first_name or "User")
    return f'<a href="tg://user?id={u.id}">{name}</a>'


HELP = f"""
╔══════════════════════════╗
║   ⚡ <b>K.K.K USERBOT</b>   ║
╚══════════════════════════╝

<b>Prefix:</b> <code>{P}</code>

┌─ 📌 <b>BASIC</b>
│ <code>{P}ping</code> <code>{P}alive</code> <code>{P}help</code>
│ <code>{P}id</code> <code>{P}info</code> <code>{P}menu</code>
│
├─ 👥 <b>TAG</b>
│ <code>{P}tagall</code> [msg] — sab members
│ <code>{P}tag</code> [msg] — ek-ek
│ <code>{P}tagadmin</code> — admins
│ <code>{P}tagstop</code> — stop
│
├─ 🛡 <b>ADMIN</b>
│ <code>{P}ban</code> <code>{P}unban</code> <code>{P}kick</code>
│ <code>{P}mute</code> <code>{P}unmute</code>
│ <code>{P}promote</code> <code>{P}demote</code>
│ <code>{P}pin</code> <code>{P}unpin</code> <code>{P}purge</code>
│
├─ 🎨 <b>FUN</b>
│ <code>{P}cat</code> <code>{P}rose</code> <code>{P}moon</code>
│ <code>{P}heart</code> <code>{P}hacker</code>
│ <code>{P}ok</code> <code>{P}vip</code> <code>{P}king</code>
│ <code>{P}funhelp</code>
│
├─ 😴 <b>AFK</b>
│ <code>{P}afk</code> [reason] · <code>{P}unafk</code>
│
└─ 📝 <b>NOTES</b>
  <code>{P}save</code> <code>{P}get</code> <code>{P}notes</code> <code>{P}clear</code>
"""


@app.on_message(cmd("menu", "cmds", "commands"), group=-3)
async def cmd_menu(client, message: Message):
    await reply(message, HELP)


@app.on_message(cmd("info", "whois"), group=-3)
async def cmd_info(client, message: Message):
    user = None
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            user = await client.get_users(message.command[1])
        except Exception:
            await reply(message, "❌ User nahi mila.")
            return
    else:
        user = message.from_user or await client.get_me()
    full = f"{user.first_name or ''} {user.last_name or ''}".strip()
    uname = f"@{user.username}" if user.username else "None"
    text = (
        f"╔══ 👤 <b>USER INFO</b> ══╗\n\n"
        f"<b>Name:</b> {html.escape(full)}\n"
        f"<b>ID:</b> <code>{user.id}</code>\n"
        f"<b>Username:</b> {uname}\n"
        f"<b>Bot:</b> {'Yes' if user.is_bot else 'No'}\n"
        f"<b>Premium:</b> {'Yes' if getattr(user, 'is_premium', False) else 'No'}\n"
        f"<b>DC:</b> <code>{getattr(user, 'dc_id', 'N/A')}</code>\n"
        f"<b>Mention:</b> {mention(user)}\n"
    )
    if message.chat and message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        try:
            m = await client.get_chat_member(message.chat.id, user.id)
            text += f"<b>Status here:</b> {m.status}\n"
        except Exception:
            pass
    await reply(message, text)


TAG_RUN = {}


@app.on_message(cmd("tagall"), group=-3)
async def cmd_tagall(client, message: Message):
    if not message.chat or message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await reply(message, "❌ Sirf group me.")
        return
    chat_id = message.chat.id
    if TAG_RUN.get(chat_id):
        await reply(message, f"⏳ <code>{P}tagstop</code>")
        return
    extra = message.text.split(None, 1)[1] if message.text and len(message.text.split(None, 1)) > 1 else ""
    TAG_RUN[chat_id] = True
    await reply(message, "👥 <b>Tagall start…</b>")
    users = []
    try:
        async for mem in client.get_chat_members(chat_id):
            u = mem.user
            if u and not u.is_bot and not u.is_deleted:
                users.append(u)
    except Exception as e:
        TAG_RUN[chat_id] = False
        await reply(message, f"❌ <code>{e}</code>")
        return
    n = 0
    try:
        for i in range(0, len(users), 5):
            if not TAG_RUN.get(chat_id):
                break
            batch = users[i:i+5]
            body = " ".join(mention(u) for u in batch)
            if extra:
                body = f"{html.escape(extra)}\n{body}"
            try:
                await client.send_message(chat_id, body)
                n += len(batch)
            except FloodWait as fw:
                await asyncio.sleep(fw.value + 1)
            except Exception:
                pass
            await asyncio.sleep(0.8)
        await reply(message, f"✅ Tagall done — <code>{n}</code>")
    finally:
        TAG_RUN[chat_id] = False


@app.on_message(cmd("tag"), group=-3)
async def cmd_tag(client, message: Message):
    if not message.chat or message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await reply(message, "❌ Sirf group me.")
        return
    chat_id = message.chat.id
    if TAG_RUN.get(chat_id):
        await reply(message, f"⏳ <code>{P}tagstop</code>")
        return
    extra = message.text.split(None, 1)[1] if message.text and len(message.text.split(None, 1)) > 1 else ""
    TAG_RUN[chat_id] = True
    n = 0
    try:
        async for mem in client.get_chat_members(chat_id):
            if not TAG_RUN.get(chat_id):
                break
            u = mem.user
            if not u or u.is_bot or u.is_deleted:
                continue
            text = mention(u)
            if extra:
                text = f"{html.escape(extra)}\n{text}"
            try:
                await client.send_message(chat_id, text)
                n += 1
            except FloodWait as fw:
                await asyncio.sleep(fw.value + 1)
            except Exception:
                pass
            await asyncio.sleep(0.6)
        await reply(message, f"✅ Tagged <code>{n}</code>")
    finally:
        TAG_RUN[chat_id] = False


@app.on_message(cmd("tagadmin", "tagadmins"), group=-3)
async def cmd_tagadmins(client, message: Message):
    if not message.chat or message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await reply(message, "❌ Sirf group me.")
        return
    lines = []
    try:
        async for mem in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
            u = mem.user
            if u and not u.is_bot:
                lines.append(mention(u))
        if not lines:
            await reply(message, "No admins.")
            return
        await reply(message, "🛡 <b>Admins</b>\n" + " ".join(lines))
    except Exception as e:
        await reply(message, f"❌ <code>{e}</code>")


@app.on_message(cmd("tagstop", "tagallstop"), group=-3)
async def cmd_tagstop(client, message: Message):
    TAG_RUN[message.chat.id] = False
    await reply(message, "🛑 Tagall stopped.")


async def _target(client, message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user, " ".join(message.command[1:]) if len(message.command) > 1 else "No reason"
    if len(message.command) > 1:
        try:
            u = await client.get_users(message.command[1])
            return u, " ".join(message.command[2:]) if len(message.command) > 2 else "No reason"
        except Exception:
            return None, None
    return None, None


@app.on_message(cmd("ban"), group=-3)
async def cmd_ban(client, message: Message):
    user, reason = await _target(client, message)
    if not user:
        await reply(message, f"Usage: reply / <code>{P}ban @user</code>")
        return
    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await reply(message, f"🔨 Banned {mention(user)}\n{html.escape(reason)}")
    except Exception as e:
        await reply(message, f"❌ <code>{e}</code>")


@app.on_message(cmd("unban"), group=-3)
async def cmd_unban(client, message: Message):
    user, _ = await _target(client, message)
    if not user:
        await reply(message, "Reply/username do.")
        return
    try:
        await client.unban_chat_member(message.chat.id, user.id)
        await reply(message, f"✅ Unbanned {mention(user)}")
    except Exception as e:
        await reply(message, f"❌ <code>{e}</code>")


@app.on_message(cmd("kick"), group=-3)
async def cmd_kick(client, message: Message):
    user, reason = await _target(client, message)
    if not user:
        await reply(message, "Reply/username do.")
        return
    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await client.unban_chat_member(message.chat.id, user.id)
        await reply(message, f"👢 Kicked {mention(user)}")
    except Exception as e:
        await reply(message, f"❌ <code>{e}</code>")


@app.on_message(cmd("mute"), group=-3)
async def cmd_mute(client, message: Message):
    user, reason = await _target(client, message)
    if not user:
        await reply(message, "Reply/username do.")
        return
    try:
        await client.restrict_chat_member(message.chat.id, user.id, ChatPermissions(can_send_messages=False))
        await reply(message, f"🔇 Muted {mention(user)}")
    except Exception as e:
        await reply(message, f"❌ <code>{e}</code>")


@app.on_message(cmd("unmute"), group=-3)
async def cmd_unmute(client, message: Message):
    user, _ = await _target(client, message)
    if not user:
        await reply(message, "Reply/username do.")
        return
    try:
        await client.restrict_chat_member(
            message.chat.id, user.id,
            ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True),
        )
        await reply(message, f"🔊 Unmuted {mention(user)}")
    except Exception as e:
        await reply(message, f"❌ <code>{e}</code>")


@app.on_message(cmd("promote"), group=-3)
async def cmd_promote(client, message: Message):
    user, _ = await _target(client, message)
    if not user:
        await reply(message, "Reply/username do.")
        return
    try:
        await client.promote_chat_member(message.chat.id, user.id, can_manage_chat=True, can_delete_messages=True, can_restrict_members=True, can_invite_users=True, can_pin_messages=True)
        await reply(message, f"⬆️ Promoted {mention(user)}")
    except Exception as e:
        await reply(message, f"❌ <code>{e}</code>")


@app.on_message(cmd("demote"), group=-3)
async def cmd_demote(client, message: Message):
    user, _ = await _target(client, message)
    if not user:
        await reply(message, "Reply/username do.")
        return
    try:
        await client.promote_chat_member(message.chat.id, user.id, can_manage_chat=False, can_delete_messages=False, can_restrict_members=False, can_invite_users=False, can_pin_messages=False)
        await reply(message, f"⬇️ Demoted {mention(user)}")
    except Exception as e:
        await reply(message, f"❌ <code>{e}</code>")


@app.on_message(cmd("pin"), group=-3)
async def cmd_pin(client, message: Message):
    if not message.reply_to_message:
        await reply(message, "Reply karke pin.")
        return
    try:
        await message.reply_to_message.pin()
        await reply(message, "📌 Pinned.")
    except Exception as e:
        await reply(message, f"❌ <code>{e}</code>")


@app.on_message(cmd("unpin"), group=-3)
async def cmd_unpin(client, message: Message):
    try:
        if message.reply_to_message:
            await message.reply_to_message.unpin()
        else:
            await client.unpin_chat_message(message.chat.id)
        await reply(message, "📌 Unpinned.")
    except Exception as e:
        await reply(message, f"❌ <code>{e}</code>")


@app.on_message(cmd("purge"), group=-3)
async def cmd_purge(client, message: Message):
    if not message.reply_to_message:
        await reply(message, "Reply + purge")
        return
    try:
        ids = list(range(message.reply_to_message.id, message.id))
        for i in range(0, len(ids), 100):
            await client.delete_messages(message.chat.id, ids[i:i+100])
        try:
            await message.delete()
        except Exception:
            pass
        m = await client.send_message(message.chat.id, f"🗑 Purged {len(ids)}")
        await asyncio.sleep(2)
        await m.delete()
    except Exception as e:
        await reply(message, f"❌ <code>{e}</code>")


AFK = {"on": False, "reason": ""}


@app.on_message(cmd("afk"), group=-3)
async def cmd_afk(client, message: Message):
    reason = " ".join(message.command[1:]) if len(message.command) > 1 else "AFK"
    AFK["on"] = True
    AFK["reason"] = reason
    await reply(message, f"😴 AFK ON\n{html.escape(reason)}")


@app.on_message(cmd("unafk", "back"), group=-3)
async def cmd_unafk(client, message: Message):
    AFK["on"] = False
    await reply(message, "✅ AFK OFF")


@app.on_message(filters.mentioned & filters.incoming & ~filters.me, group=5)
async def afk_watcher(client, message: Message):
    if not AFK["on"]:
        return
    try:
        await message.reply_text(f"😴 AFK: {html.escape(AFK['reason'])}")
    except Exception:
        pass


NOTES = {}


@app.on_message(cmd("save"), group=-3)
async def cmd_save(client, message: Message):
    if len(message.command) < 3:
        await reply(message, f"{P}save name text")
        return
    name = message.command[1].lower()
    NOTES[name] = message.text.split(None, 2)[2]
    await reply(message, f"💾 Saved {name}")


@app.on_message(cmd("get"), group=-3)
async def cmd_get(client, message: Message):
    if len(message.command) < 2:
        await reply(message, f"{P}get name")
        return
    text = NOTES.get(message.command[1].lower())
    await reply(message, text or "❌ Note nahi")


@app.on_message(cmd("notes"), group=-3)
async def cmd_notes(client, message: Message):
    await reply(message, "📝 " + (", ".join(NOTES) if NOTES else "empty"))


@app.on_message(cmd("clear"), group=-3)
async def cmd_clear(client, message: Message):
    if len(message.command) < 2:
        await reply(message, f"{P}clear name")
        return
    NOTES.pop(message.command[1].lower(), None)
    await reply(message, "🗑 cleared")


async def animate(message, frames, delay=0.45):
    msg = await reply(message, f"<pre>{frames[0]}</pre>")
    if not msg:
        return
    for fr in frames[1:]:
        await asyncio.sleep(delay)
        try:
            await msg.edit_text(f"<pre>{fr}</pre>")
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except Exception:
            break


CAT = [" /\\_/\\\n( o.o )\n > ^ <", " /\\_/\\\n( ^.^ )\n > ^ < meow"]
ROSE = ["   @", "  \\|/\n   |", " *\\|/*\n   | ROSE"]
MOON = ["🌑", "🌓", "🌕", "🌗", "🌑"]
HEART = ["♡", "♡ ♡", "♡ LOVE ♡"]
HACK = ["connecting...", "bypass...", "HACKED"]


@app.on_message(cmd("cat"), group=-3)
async def cmd_cat(c, m):
    await animate(m, CAT)


@app.on_message(cmd("rose"), group=-3)
async def cmd_rose(c, m):
    await animate(m, ROSE, 0.5)


@app.on_message(cmd("moon"), group=-3)
async def cmd_moon(c, m):
    await animate(m, MOON, 0.4)


@app.on_message(cmd("heart"), group=-3)
async def cmd_heart(c, m):
    await animate(m, HEART, 0.4)


@app.on_message(cmd("hacker", "hack"), group=-3)
async def cmd_hack(c, m):
    await animate(m, HACK, 0.5)


@app.on_message(cmd("ok"), group=-3)
async def cmd_ok(c, m):
    await reply(m, "<pre>  ___  _  __\n / _ \\| |/ /\n| |_| |   <\n \\___/|_|\\_\\</pre>")


@app.on_message(cmd("vip"), group=-3)
async def cmd_vip(c, m):
    await reply(m, "<pre>VIP</pre>")


@app.on_message(cmd("king"), group=-3)
async def cmd_king(c, m):
    await reply(m, "<pre>KING</pre>")


@app.on_message(cmd("pro"), group=-3)
async def cmd_pro(c, m):
    await reply(m, "<pre>PRO</pre>")


@app.on_message(cmd("boss"), group=-3)
async def cmd_boss(c, m):
    await reply(m, "<pre>BOSS</pre>")


@app.on_message(cmd("funhelp", "arts"), group=-3)
async def cmd_funhelp(c, m):
    await reply(m, f"🎨 {P}cat {P}rose {P}moon {P}heart {P}hacker {P}ok {P}vip {P}king")


logger.info("all_cmds.py loaded")
