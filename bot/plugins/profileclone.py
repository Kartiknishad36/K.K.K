"""
Profile Cloner
  .clonemode on|off
  .clone              (reply / id / @username)
  .back               restore name/bio + delete only cloned DP(s)

Note: Telegram user ID / @username clone nahi ho sakte (platform limit).
Name, bio, DP same dikhte hain.
"""

import os
import json
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message
import config

BACKUP_FILE = Path("data") / "my_backup.json"
CLONE_ON = True


async def _photo_ids(client: Client) -> list:
    """Current profile photo file_ids (newest first)."""
    ids = []
    try:
        async for photo in client.get_chat_photos("me", limit=20):
            fid = getattr(photo, "file_id", None)
            if fid:
                ids.append(fid)
    except Exception as e:
        print(f"[clone] photo list: {e}")
    return ids


async def _resolve_user(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        chat = await client.get_chat(u.id)
        return u, chat

    parts = (message.text or "").split()
    if len(parts) < 2:
        return None, None
    arg = parts[1].strip()
    try:
        if arg.isdigit() or (arg.startswith("-") and arg[1:].isdigit()):
            chat = await client.get_chat(int(arg))
        else:
            chat = await client.get_chat(arg)
        try:
            u = await client.get_users(chat.id)
        except Exception:
            u = chat
        return u, chat
    except Exception:
        return None, None


@Client.on_message(filters.command("clonemode", prefixes=config.COMMAND_PREFIX) & filters.me)
async def clone_toggle(client: Client, message: Message):
    global CLONE_ON
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.edit_text(
            f"**Cloner:** `{'ON' if CLONE_ON else 'OFF'}`\n\n"
            f"`{config.COMMAND_PREFIX}clonemode on` | `{config.COMMAND_PREFIX}clonemode off`"
        )
        return
    arg = parts[1].lower()
    if arg in ("on", "1", "enable"):
        CLONE_ON = True
        await message.edit_text("✅ Cloner **ON**")
    elif arg in ("off", "0", "disable"):
        CLONE_ON = False
        await message.edit_text("❌ Cloner **OFF**")
    else:
        await message.edit_text(f"Usage: `{config.COMMAND_PREFIX}clonemode on|off`")


@Client.on_message(filters.command("clone", prefixes=config.COMMAND_PREFIX) & filters.me)
async def clone_profile(client: Client, message: Message):
    global CLONE_ON
    if not CLONE_ON:
        await message.edit_text(f"Cloner OFF — `{config.COMMAND_PREFIX}clonemode on`")
        return

    target_user, target_chat = await _resolve_user(client, message)
    if not target_chat:
        await message.edit_text(
            f"**Usage:**\n"
            f"• Reply + `{config.COMMAND_PREFIX}clone`\n"
            f"• `{config.COMMAND_PREFIX}clone 123456789`\n"
            f"• `{config.COMMAND_PREFIX}clone @username`"
        )
        return

    me_chat = await client.get_chat("me")
    old_photo_ids = await _photo_ids(client)
    backup = {
        "first_name": me_chat.first_name or "",
        "last_name": me_chat.last_name or "",
        "bio": getattr(me_chat, "bio", None) or "",
        "photo_ids_before": old_photo_ids,
        "added_photo_ids": [],
    }
    try:
        BACKUP_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(backup, f, ensure_ascii=False, indent=2)
    except Exception as e:
        await message.edit_text(f"❌ Backup fail: `{e}`")
        return

    name = (
        getattr(target_user, "first_name", None)
        or getattr(target_chat, "first_name", None)
        or "User"
    )
    mention = (
        target_user.mention
        if hasattr(target_user, "mention")
        else f"`{target_chat.id}`"
    )
    uid = target_chat.id
    uname = (
        getattr(target_chat, "username", None)
        or getattr(target_user, "username", None)
        or "—"
    )

    m = await message.edit_text(f"🔄 Cloning {mention}…\nID: `{uid}`")

    added_ids = []
    try:
        dp_ok = False
        try:
            target_photos = []
            async for ph in client.get_chat_photos(uid, limit=1):
                target_photos.append(ph)
            if target_photos:
                path = await client.download_media(target_photos[0].file_id)
                if path:
                    await client.set_profile_photo(photo=path)
                    try:
                        os.remove(path)
                    except Exception:
                        pass
                    dp_ok = True
            else:
                photo = getattr(target_chat, "photo", None)
                if photo:
                    file_id = getattr(photo, "big_file_id", None)
                    path = await client.download_media(file_id or photo)
                    if path:
                        await client.set_profile_photo(photo=path)
                        try:
                            os.remove(path)
                        except Exception:
                            pass
                        dp_ok = True
        except Exception as e:
            await m.edit_text(f"⚠️ DP skip: `{e}`\nName/bio continue…")

        if dp_ok:
            new_ids = await _photo_ids(client)
            old_set = set(old_photo_ids)
            for fid in new_ids:
                if fid not in old_set:
                    added_ids.append(fid)
            backup["added_photo_ids"] = added_ids
            try:
                with open(BACKUP_FILE, "w", encoding="utf-8") as f:
                    json.dump(backup, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

        first_name = (getattr(target_chat, "first_name", None) or name or " ")[:64]
        last_name = (getattr(target_chat, "last_name", None) or "")[:64]
        bio = (getattr(target_chat, "bio", None) or "")[:70]

        await client.update_profile(
            first_name=first_name or " ",
            last_name=last_name,
            bio=bio,
        )

        await m.edit_text(
            f"✅ **Cloned**\n\n"
            f"**From:** {mention}\n"
            f"**Target ID:** `{uid}`\n"
            f"**Username:** @{uname}\n"
            f"**Name:** **{first_name} {last_name}**\n"
            f"**Bio:** _{bio or '—'}_\n"
            f"**DP:** {'✅' if dp_ok else '❌'}\n"
            f"**Added photos:** `{len(added_ids)}`\n\n"
            f"_Note: Telegram ID / @username change nahi hote._\n"
            f"Restore: `{config.COMMAND_PREFIX}back`"
        )
    except Exception as e:
        await m.edit_text(f"❌ Clone error: `{e}`")


@Client.on_message(filters.command("back", prefixes=config.COMMAND_PREFIX) & filters.me)
async def restore_profile(client: Client, message: Message):
    if not BACKUP_FILE.exists():
        await message.edit_text(f"Backup nahi — pehle `{config.COMMAND_PREFIX}clone` chalao.")
        return

    m = await message.edit_text("♻️ Restoring…")
    try:
        with open(BACKUP_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        added = data.get("added_photo_ids") or []
        deleted = 0
        if added:
            for fid in added:
                try:
                    await client.delete_profile_photos(fid)
                    deleted += 1
                except Exception as e:
                    print(f"[clone] delete photo: {e}")
        else:
            before = set(data.get("photo_ids_before") or [])
            if before:
                current = await _photo_ids(client)
                for fid in current:
                    if fid not in before:
                        try:
                            await client.delete_profile_photos(fid)
                            deleted += 1
                        except Exception:
                            pass

        await client.update_profile(
            first_name=(data.get("first_name") or " ")[:64],
            last_name=(data.get("last_name") or "")[:64],
            bio=(data.get("bio") or "")[:70],
        )

        await m.edit_text(
            f"✅ **Back done**\n\n"
            f"Name/bio restore ✅\n"
            f"Cloned DP deleted: `{deleted}`\n"
            f"Purani DPs safe ✅"
        )
    except Exception as e:
        await m.edit_text(f"❌ Back error: `{e}`")
