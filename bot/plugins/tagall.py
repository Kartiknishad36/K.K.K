"""TagAll — full members, batch tag"""
import asyncio
import html

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMembersFilter, ChatType
from pyrogram.errors import FloodWait, ChatAdminRequired

from bot.client import app
import config

P = config.COMMAND_PREFIX
RUNNING = set()
BATCH = 8
DELAY = 1.2


def _mention(u) -> str:
    name = html.escape((u.first_name or "User").strip() or "User")
    return f'<a href="tg://user?id={u.id}">{name}</a>'


async def _collect(client, chat_id: int, admins_only: bool = False):
    seen = set()
    users = []
    filters_try = (
        [ChatMembersFilter.ADMINISTRATORS]
        if admins_only
        else [ChatMembersFilter.SEARCH, ChatMembersFilter.RECENT]
    )
    for f in filters_try:
        try:
            kw = {"chat_id": chat_id, "filter": f}
            if f == ChatMembersFilter.SEARCH:
                kw["query"] = ""
            async for m in client.get_chat_members(**kw):
                u = m.user
                if not u or u.id in seen or u.is_bot or getattr(u, "is_deleted", False):
                    continue
                seen.add(u.id)
                users.append(u)
        except Exception:
            continue
    if not users and not admins_only:
        try:
            async for m in client.get_chat_members(chat_id):
                u = m.user
                if not u or u.id in seen or u.is_bot or getattr(u, "is_deleted", False):
                    continue
                seen.add(u.id)
                users.append(u)
        except Exception:
            pass
    return users


@app.on_message(filters.command(["tagall"], prefixes=P))
async def tag_all(client, message: Message):
    if not message.chat or message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        try:
            return await message.edit_text("Sirf groups me.")
        except Exception:
            return await message.reply_text("Sirf groups me.")
    chat_id = message.chat.id
    if chat_id in RUNNING:
        return await message.reply_text("Pehle se chal raha — `.tagallstop`")
    extra = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    RUNNING.add(chat_id)
    status = await message.reply_text("Members collect...")
    try:
        members = await _collect(client, chat_id)
        if not members:
            return await status.edit_text("No members found.")
        n = 0
        for i in range(0, len(members), BATCH):
            if chat_id not in RUNNING:
                break
            batch = members[i:i+BATCH]
            body = " ".join(_mention(u) for u in batch)
            if extra:
                body = html.escape(extra) + "\n" + body
            try:
                await client.send_message(chat_id, body)
                n += len(batch)
            except FloodWait as e:
                await asyncio.sleep(min(int(e.value) + 1, 90))
            except Exception:
                pass
            await asyncio.sleep(DELAY)
        await status.edit_text(f"Done — `{n}` members")
    except Exception as e:
        await status.edit_text(f"Error: `{e}`")
    finally:
        RUNNING.discard(chat_id)


@app.on_message(filters.command(["tag"], prefixes=P))
async def tag_one(client, message: Message):
    if not message.chat or message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return await message.reply_text("Sirf groups me.")
    chat_id = message.chat.id
    if chat_id in RUNNING:
        return await message.reply_text("Already running — `.tagallstop`")
    extra = " ".join(message.command[1:]) if len(message.command) > 1 else "Hello!"
    RUNNING.add(chat_id)
    status = await message.reply_text("One-by-one tag...")
    try:
        members = await _collect(client, chat_id)
        n = 0
        for u in members:
            if chat_id not in RUNNING:
                break
            try:
                await client.send_message(chat_id, f"{_mention(u)}\n\n{html.escape(extra)}")
                n += 1
            except FloodWait as e:
                await asyncio.sleep(min(int(e.value) + 1, 90))
            except Exception:
                pass
            await asyncio.sleep(2.0)
        await status.edit_text(f"Done — `{n}` members")
    except Exception as e:
        await status.edit_text(f"Error: `{e}`")
    finally:
        RUNNING.discard(chat_id)


@app.on_message(filters.command(["tagadmin", "tagadmins"], prefixes=P))
async def tag_admins(client, message: Message):
    if not message.chat or message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return await message.reply_text("Sirf groups me.")
    extra = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    status = await message.reply_text("Admins collect...")
    try:
        admins = await _collect(client, message.chat.id, admins_only=True)
        if not admins:
            return await status.edit_text("No admins.")
        mentions = " ".join(_mention(u) for u in admins)
        text = f"**Admins:**\n{mentions}"
        if extra:
            text = html.escape(extra) + "\n\n" + text
        await client.send_message(message.chat.id, text)
        await status.edit_text(f"Tagged `{len(admins)}` admins")
    except Exception as e:
        await status.edit_text(f"Error: `{e}`")


@app.on_message(filters.command(["tagallstop", "tagstop"], prefixes=P))
async def tag_stop(client, message: Message):
    RUNNING.discard(message.chat.id)
    await message.reply_text("Tagall stop signal.")
