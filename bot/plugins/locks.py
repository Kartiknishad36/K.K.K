""".lock / .unlock media|sticker|link|gif|forward|all"""
from pyrogram import Client, filters
from pyrogram.types import Message
import config
from bot.database import db

LOCK_KEYS = {"media": "lock_media", "sticker": "lock_sticker", "link": "lock_link", "gif": "lock_gif", "forward": "lock_forward", "all": "lock_all"}

@Client.on_message(filters.command(["lock", "unlock"], prefixes=config.COMMAND_PREFIX) & filters.me)
async def lock_cmd(client: Client, message: Message):
    if message.chat.type.name not in ["GROUP", "SUPERGROUP"]:
        await message.edit_text("Sirf groups me."); return
    chat_id = message.chat.id
    action = message.command[0].lower()
    if len(message.command) < 2:
        lines = [f"• {n}: **{'ON' if await db.get_chat_flag(chat_id, k, False) else 'OFF'}**" for n, k in LOCK_KEYS.items()]
        await message.edit_text("🔒 **Locks**\n" + "\n".join(lines) + f"\n\n`{config.COMMAND_PREFIX}lock media|sticker|link|gif|forward|all`\n`{config.COMMAND_PREFIX}unlock …`")
        return
    what = message.command[1].lower()
    if what not in LOCK_KEYS:
        await message.edit_text("Unknown lock type."); return
    val = action == "lock"
    if what == "all":
        for k in LOCK_KEYS.values(): await db.set_chat_flag(chat_id, k, val)
    else:
        await db.set_chat_flag(chat_id, LOCK_KEYS[what], val)
    await message.edit_text(f"{'🔒' if val else '🔓'} **{what}** {'locked' if val else 'unlocked'}")

@Client.on_message(filters.group & filters.incoming & ~filters.me & ~filters.service, group=7)
async def lock_watch(client: Client, message: Message):
    if not message.from_user or message.from_user.id == config.OWNER_ID: return
    chat_id = message.chat.id
    if await db.get_chat_flag(chat_id, "lock_all", False):
        try: await message.delete()
        except Exception: pass
        return
    if await db.get_chat_flag(chat_id, "lock_media", False) and (message.photo or message.video or message.document or message.audio or message.voice):
        try: await message.delete()
        except Exception: pass; return
    if await db.get_chat_flag(chat_id, "lock_sticker", False) and message.sticker:
        try: await message.delete()
        except Exception: pass; return
    if await db.get_chat_flag(chat_id, "lock_gif", False) and message.animation:
        try: await message.delete()
        except Exception: pass; return
    if await db.get_chat_flag(chat_id, "lock_forward", False) and message.forward_date:
        try: await message.delete()
        except Exception: pass; return
    if await db.get_chat_flag(chat_id, "lock_link", False):
        t = (message.text or message.caption or "").lower()
        if "http://" in t or "https://" in t or "t.me/" in t:
            try: await message.delete()
            except Exception: pass
