from pyrogram import Client, filters
from pyrogram.types import Message
import config


HELP_TEXT = f"""
**╔══════════════════════════╗**
**║     🤖  USERBOT HELP     ║**
**╚══════════════════════════╝**

**Prefix :** `{config.COMMAND_PREFIX}`
**Total Commands :** 70+

────────────────────
**📌 BASIC**
────────────────────
`{config.COMMAND_PREFIX}help` — Show this menu
`{config.COMMAND_PREFIX}ping` — Check response time
`{config.COMMAND_PREFIX}alive` — Bot status
`{config.COMMAND_PREFIX}id` — Get chat / user ID
`{config.COMMAND_PREFIX}stats` — Account statistics

────────────────────
**😴 AFK**
────────────────────
`{config.COMMAND_PREFIX}afk [reason]` — Enable AFK mode
`{config.COMMAND_PREFIX}unafk` — Disable AFK

────────────────────
**📝 NOTES**
────────────────────
`{config.COMMAND_PREFIX}save <name> <text>` — Save note
`{config.COMMAND_PREFIX}get <name>` — Get note
`{config.COMMAND_PREFIX}clear <name>` — Delete note
`{config.COMMAND_PREFIX}notes` — List all notes
`#name` — Quick get note

────────────────────
**🔍 FILTERS**
────────────────────
`{config.COMMAND_PREFIX}filter <key> <reply>` — Add filter
`{config.COMMAND_PREFIX}stop <key>` — Remove filter
`{config.COMMAND_PREFIX}filters` — List filters

────────────────────
**👋 WELCOME**
────────────────────
`{config.COMMAND_PREFIX}setwelcome <msg>` — Set welcome message
`{config.COMMAND_PREFIX}welcome` — Toggle welcome on/off
**Vars :** `{{mention}}` `{{name}}` `{{id}}` `{{chat}}`

────────────────────
**🗑️ AUTO DELETE**
────────────────────
`{config.COMMAND_PREFIX}autodel <seconds>` — Enable auto-delete
`{config.COMMAND_PREFIX}autodel off` — Disable

────────────────────
**⏰ SCHEDULER**
────────────────────
`{config.COMMAND_PREFIX}schedule <time> <msg>` — Schedule message
`{config.COMMAND_PREFIX}schedules` — List pending
`{config.COMMAND_PREFIX}delschedule <id>` — Delete schedule
**Time :** `10m` `2h` `1d` or `2026-11-13 18:00`

────────────────────
**🛡️ ADMIN**
────────────────────
`{config.COMMAND_PREFIX}ban` — Ban user
`{config.COMMAND_PREFIX}unban` — Unban user
`{config.COMMAND_PREFIX}kick` — Kick user
`{config.COMMAND_PREFIX}mute` — Mute user
`{config.COMMAND_PREFIX}unmute` — Unmute user
`{config.COMMAND_PREFIX}promote` — Promote to admin
`{config.COMMAND_PREFIX}demote` — Demote admin
`{config.COMMAND_PREFIX}pin` — Pin message
`{config.COMMAND_PREFIX}unpin` — Unpin message
`{config.COMMAND_PREFIX}purge` — Delete messages (reply)
`{config.COMMAND_PREFIX}gban` — Global ban
`{config.COMMAND_PREFIX}ungban` — Remove global ban

────────────────────
**🔄 CLONE / MIRROR**
────────────────────
`{config.COMMAND_PREFIX}clone <chat_id>` — Start cloning
`{config.COMMAND_PREFIX}clone off` — Stop cloning
`{config.COMMAND_PREFIX}clones` — List active clones

────────────────────
**🛡️ PM PERMIT**
────────────────────
`{config.COMMAND_PREFIX}approve` — Approve user for PM
`{config.COMMAND_PREFIX}disapprove` — Remove approval

────────────────────
**🛠️ TOOLS**
────────────────────
`{config.COMMAND_PREFIX}info` / `whois` — User information
`{config.COMMAND_PREFIX}tr <lang> <text>` — Translate
`{config.COMMAND_PREFIX}dl` — Download media (reply)
`{config.COMMAND_PREFIX}join <link>` — Join chat / channel
`{config.COMMAND_PREFIX}leave` — Leave current chat
`{config.COMMAND_PREFIX}broadcast <msg>` — Broadcast to PMs
`{config.COMMAND_PREFIX}invite` / `link` — Get invite link

────────────────────
**🤖 AI**
────────────────────
`{config.COMMAND_PREFIX}ai <prompt>` — Ask AI (needs OpenAI key)

────────────────────
**🔐 SESSION MANAGER**
────────────────────
`{config.COMMAND_PREFIX}sessions` — List all sessions
`{config.COMMAND_PREFIX}session <name>` — Switch session
`{config.COMMAND_PREFIX}newsession <name>` — Create new session
`{config.COMMAND_PREFIX}delsession <name>` — Delete session

────────────────────
**🚩 SPAM REPORT**
────────────────────
`{config.COMMAND_PREFIX}report` — Report spam (reply)
`{config.COMMAND_PREFIX}reports` — Show all reports
`{config.COMMAND_PREFIX}clearreports` — Clear reports
`{config.COMMAND_PREFIX}resetwarns` — Reset user warnings

────────────────────
**🎙️ VOICE CHAT**
────────────────────
`{config.COMMAND_PREFIX}vcinfo` — Voice chat status
`{config.COMMAND_PREFIX}joinvc` — Join voice chat
`{config.COMMAND_PREFIX}leavevc` — Leave voice chat
`{config.COMMAND_PREFIX}vctitle <title>` — Set VC title

────────────────────
**🔒 ENCRYPTED NOTES**
────────────────────
`{config.COMMAND_PREFIX}encnote <name> <text>` — Save encrypted note
`{config.COMMAND_PREFIX}decnote <name>` — Decrypt & show
`{config.COMMAND_PREFIX}encnotes` — List encrypted notes
`{config.COMMAND_PREFIX}secretchats` — List secret chats

────────────────────
**🌐 API / WEBHOOK**
────────────────────
`{config.COMMAND_PREFIX}webhook <url> <payload>` — Send webhook
`{config.COMMAND_PREFIX}fetch <url>` — GET any URL
`{config.COMMAND_PREFIX}shorten <url>` — Shorten URL
`{config.COMMAND_PREFIX}sethook <name> <url>` — Save webhook

────────────────────
**Made with ❤️ | Use Responsibly**
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
        f"**User :** {me.first_name}\n"
        f"**ID :** `{me.id}`\n"
        f"**Username :** @{me.username if me.username else 'None'}\n"
        f"**Prefix :** `{config.COMMAND_PREFIX}`"
    )
    await message.edit_text(text)


@Client.on_message(filters.command("id", prefixes=config.COMMAND_PREFIX) & filters.me)
async def id_command(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
        text = (
            f"**User ID :** `{user.id}`\n"
            f"**Chat ID :** `{message.chat.id}`\n"
            f"**Message ID :** `{message.reply_to_message.id}`"
        )
    else:
        text = (
            f"**Chat ID :** `{message.chat.id}`\n"
            f"**Your ID :** `{message.from_user.id if message.from_user else 'N/A'}`"
        )
    await message.edit_text(text)
