""".zombies | .zombies clean | .zombies ban"""
import asyncio
from pyrogram import Client, filters
from bot.client import app
from pyrogram.types import Message
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.errors import FloodWait, ChatAdminRequired
import config

@app.on_message(filters.command(["zombies", "cleanzombies", "zombie"], prefixes=config.COMMAND_PREFIX) & filters.me)
async def zombies_cmd(client: Client, message: Message):
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await message.edit_text("Sirf groups me."); return
    arg = message.command[1].lower() if len(message.command) > 1 else "count"
    do_clean = arg in ("clean", "clear", "kick", "ban", "remove")
    permanent_ban = arg == "ban" or (len(message.command) > 2 and message.command[2].lower() == "ban")
    status = await message.edit_text("👻 Zombie scan…")
    zombies, scanned = [], 0
    try:
        async for member in client.get_chat_members(message.chat.id):
            scanned += 1
            u = member.user
            if not u or not u.is_deleted:
                continue
            if member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                continue
            zombies.append(u.id)
    except ChatAdminRequired:
        await status.edit_text("❌ Admin rights chahiye."); return
    except Exception as e:
        await status.edit_text(f"❌ `{e}`"); return
    if not zombies:
        await status.edit_text(f"✅ Clean — scanned `{scanned}`, zombies `0`"); return
    if not do_clean:
        await status.edit_text(
            f"👻 Zombies: `{len(zombies)}` / scanned `{scanned}`\n"
            f"`{config.COMMAND_PREFIX}zombies clean` | `{config.COMMAND_PREFIX}zombies ban`"
        )
        return
    removed = failed = 0
    await status.edit_text(f"🧹 Cleaning `{len(zombies)}`…")
    for uid in zombies:
        try:
            await client.ban_chat_member(message.chat.id, uid)
            if not permanent_ban:
                try:
                    await client.unban_chat_member(message.chat.id, uid)
                except Exception:
                    pass
            removed += 1
        except FloodWait as e:
            await asyncio.sleep(min(e.value, 20) + 1)
            try:
                await client.ban_chat_member(message.chat.id, uid)
                if not permanent_ban:
                    await client.unban_chat_member(message.chat.id, uid)
                removed += 1
            except Exception:
                failed += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.2)
    await status.edit_text(f"✅ Removed `{removed}` | Failed `{failed}`")
