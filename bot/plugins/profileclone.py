"""Profile clone — copy name/bio/photo then .back restore"""
import os
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app, logger
import config

P = config.COMMAND_PREFIX
BACKUP = {}

async def out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["cloneprofile", "pclone", "copyprofile"], prefixes=P))
async def pclone_cmd(client, message: Message):
    user = None
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            user = await client.get_users(message.command[1])
        except Exception:
            await out(message, "User nahi mila")
            return
    else:
        await out(message, f"Reply / `{P}pclone @user`")
        return
    me = await client.get_me()
    if "saved" not in BACKUP:
        BACKUP["saved"] = True
        BACKUP["first_name"] = me.first_name
        BACKUP["last_name"] = me.last_name
        BACKUP["bio"] = ""
        try:
            full = await client.get_chat(me.id)
            BACKUP["bio"] = full.bio or ""
        except Exception:
            pass
        try:
            BACKUP["photo"] = await client.download_media(me.photo.big_file_id) if me.photo else None
        except Exception:
            BACKUP["photo"] = None
    try:
        await client.update_profile(first_name=user.first_name or "User", last_name=user.last_name or "")
    except Exception as e:
        await out(message, f"❌ name: `{e}`")
        return
    try:
        chat = await client.get_chat(user.id)
        if chat.bio:
            await client.update_profile(bio=chat.bio[:70])
    except Exception:
        pass
    try:
        if user.photo:
            path = await client.download_media(user.photo.big_file_id)
            await client.set_profile_photo(photo=path)
            try:
                os.remove(path)
            except Exception:
                pass
    except Exception as e:
        logger.error(f"pclone photo: {e}")
    await out(message, f"✅ Cloned {user.mention}\nRestore: `{P}back`")

@app.on_message(filters.command(["back", "restoreprofile"], prefixes=P), group=1)
async def back_profile(client, message: Message):
    if not BACKUP.get("saved"):
        await out(message, "No backup. Clone someone first.")
        return
    try:
        await client.update_profile(
            first_name=BACKUP.get("first_name") or "User",
            last_name=BACKUP.get("last_name") or "",
            bio=BACKUP.get("bio") or "",
        )
        if BACKUP.get("photo"):
            try:
                await client.set_profile_photo(photo=BACKUP["photo"])
            except Exception:
                pass
        await out(message, "✅ Profile restored")
    except Exception as e:
        await out(message, f"❌ `{e}`")

@app.on_message(filters.command(["clonemode"], prefixes=P))
async def clonemode_cmd(client, message: Message):
    await out(message, f"`{P}pclone` reply/@user\n`{P}back` restore")
