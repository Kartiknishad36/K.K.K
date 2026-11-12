from pyrogram import Client, filters
from pyrogram.types import Message
import config

HELP_TEXT = f"""
**🤖 UserBot Help Menu**

**Prefix:** `{config.COMMAND_PREFIX}`

**📌 Basic**
• `{config.COMMAND_PREFIX}ping` - Check bot response time
• `{config.COMMAND_PREFIX}alive` - Bot status
• `{config.COMMAND_PREFIX}help` - This menu
• `{config.COMMAND_PREFIX}id` - Get chat/user ID
• `{config.COMMAND_PREFIX}stats` - Account stats

**😴 AFK**
• `{config.COMMAND_PREFIX}afk [reason]` - Set AFK
• `{config.COMMAND_PREFIX}unafk` - Remove AFK

**📝 Notes**
• `{config.COMMAND_PREFIX}save <name> <content>` - Save note
• `{config.COMMAND_PREFIX}get <name>` - Get note
• `{config.COMMAND_PREFIX}clear <name>` - Delete note
• `{config.COMMAND_PREFIX}notes` - List all notes
• `#name` - Quick get note

**🔍 Filters**
• `{config.COMMAND_PREFIX}filter <keyword> <reply>` - Add filter
• `{config.COMMAND_PREFIX}stop <keyword>` - Remove filter
• `{config.COMMAND_PREFIX}filters` - List filters

**👋 Welcome**
• `{config.COMMAND_PREFIX}setwelcome <message>` - Set welcome
• `{config.COMMAND_PREFIX}welcome` - Toggle welcome
• Variables: `{{mention}}` `{{name}}` `{{id}}` `{{chat}}`

**🗑️ AutoDelete**
• `{config.COMMAND_PREFIX}autodel <seconds>` - Enable auto-delete
• `{config.COMMAND_PREFIX}autodel off` - Disable

**⏰ Scheduler**
• `{config.COMMAND_PREFIX}schedule <time> <message>` - Schedule message
• `{config.COMMAND_PREFIX}schedules` - List pending
• `{config.COMMAND_PREFIX}delschedule <id>` - Delete schedule
• Time: `10m`, `2h`, `1d` or `2026-11-13 15:30`

**🛡️ Admin Tools**
• `{config.COMMAND_PREFIX}ban` / `unban` / `kick`
• `{config.COMMAND_PREFIX}mute` / `unmute`
• `{config.COMMAND_PREFIX}promote` / `demote`
• `{config.COMMAND_PREFIX}pin` / `unpin`
• `{config.COMMAND_PREFIX}purge` - Delete messages
• `{config.COMMAND_PREFIX}gban` / `ungban`

**🔄 Clone / Mirror**
• `{config.COMMAND_PREFIX}clone <target_id>` - Clone this chat to target
• `{config.COMMAND_PREFIX}clone off` - Stop cloning
• `{config.COMMAND_PREFIX}clones` - List active clones

**🛡️ PM Permit**
• `{config.COMMAND_PREFIX}approve` - Approve user for PM
• `{config.COMMAND_PREFIX}disapprove` - Remove approval

**🛠️ Tools**
• `{config.COMMAND_PREFIX}info` / `whois` - User info
• `{config.COMMAND_PREFIX}tr <lang> <text>` - Translate
• `{config.COMMAND_PREFIX}dl` - Download media (reply)
• `{config.COMMAND_PREFIX}join <link>` - Join chat
• `{config.COMMAND_PREFIX}leave` - Leave current chat
• `{config.COMMAND_PREFIX}broadcast <msg>` - Broadcast to PMs

**🤖 AI** (if enabled)
• `{config.COMMAND_PREFIX}ai <prompt>` - Ask AI
"""


@Client.on_message(filters.command(["help", "start"], prefixes=config.COMMAND_PREFIX) & filters.me)
async def help_command(client: Client, message: Message):
    await message.edit_text(HELP_TEXT)


@Client.on_message(filters.command("ping", prefixes=config.COMMAND_PREFIX) & filters.me)
async def ping_command(client: Client, message: Message):
    import time
    start = time.time()
    msg = await message.edit_text("🏓 Pinging...")
    end = time.time()
    await msg.edit_text(f"🏓 **Pong!**\n`{round((end - start) * 1000, 2)} ms`")


@Client.on_message(filters.command("alive", prefixes=config.COMMAND_PREFIX) & filters.me)
async def alive_command(client: Client, message: Message):
    me = await client.get_me()
    text = (
        f"**✅ UserBot is Alive!**\n\n"
        f"**User:** {me.first_name}\n"
        f"**ID:** `{me.id}`\n"
        f"**Username:** @{me.username if me.username else 'None'}\n"
        f"**Prefix:** `{config.COMMAND_PREFIX}`"
    )
    await message.edit_text(text)


@Client.on_message(filters.command("id", prefixes=config.COMMAND_PREFIX) & filters.me)
async def id_command(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
        text = (
            f"**User ID:** `{user.id}`\n"
            f"**Chat ID:** `{message.chat.id}`\n"
            f"**Message ID:** `{message.reply_to_message.id}`"
        )
    else:
        text = (
            f"**Chat ID:** `{message.chat.id}`\n"
            f"**Your ID:** `{message.from_user.id if message.from_user else 'N/A'}`"
        )
    await message.edit_text(text)
