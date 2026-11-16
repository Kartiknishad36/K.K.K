from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

HELP_TEXT = f"""
**╔══════════════════════════╗**
**║     🤖  USERBOT HELP     ║**
**╚══════════════════════════╝**

**Prefix :** `{config.COMMAND_PREFIX}`
**Total Commands :** 80+

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

────────────────────
**🛡️ ADMIN**
────────────────────
`{config.COMMAND_PREFIX}ban` `unban` `kick` `mute` `unmute`
`{config.COMMAND_PREFIX}promote` `demote` `pin` `unpin` `purge`
`{config.COMMAND_PREFIX}gban` `ungban`

────────────────────
**🔄 CLONE**
────────────────────
`{config.COMMAND_PREFIX}clone` `clone off` `clones`

────────────────────
**🛠️ TOOLS**
────────────────────
`{config.COMMAND_PREFIX}info` / `whois` — User information
`{config.COMMAND_PREFIX}tr` `dl` `join` `leave` `broadcast`

────────────────────
**📢 TAGALL**
────────────────────
`{config.COMMAND_PREFIX}tagall` `tag` `tagadmin` `tagallstop`

────────────────────
**🎨 FUN**
────────────────────
`{config.COMMAND_PREFIX}cat` `rose` `hacker` `moon` `heart`
`{config.COMMAND_PREFIX}ok` `vip` `king` `pro` `funhelp`

**Made with ❤️ | Use Responsibly**
"""

@app.on_message(filters.command(["help", "start"], prefixes=config.COMMAND_PREFIX))
async def help_command(client, message: Message):
    try:
        await message.edit_text(HELP_TEXT)
    except Exception:
        await message.reply_text(HELP_TEXT)

@app.on_message(filters.command("ping", prefixes=config.COMMAND_PREFIX))
async def ping_command(client, message: Message):
    import time
    start = time.time()
    try:
        msg = await message.edit_text("🏓 Pinging...")
        end = time.time()
        await msg.edit_text(f"🏓 **Pong!**\n`{round((end - start) * 1000, 2)} ms`")
    except Exception:
        await message.reply_text("🏓 **Pong!**")

@app.on_message(filters.command("alive", prefixes=config.COMMAND_PREFIX))
async def alive_command(client, message: Message):
    me = await client.get_me()
    text = (
        f"**✅ UserBot is Alive!**\n\n"
        f"**User :** {me.first_name}\n"
        f"**ID :** `{me.id}`\n"
        f"**Username :** @{me.username if me.username else 'None'}\n"
        f"**Prefix :** `{config.COMMAND_PREFIX}`"
    )
    try:
        await message.edit_text(text)
    except Exception:
        await message.reply_text(text)

@app.on_message(filters.command("id", prefixes=config.COMMAND_PREFIX))
async def id_command(client, message: Message):
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
    try:
        await message.edit_text(text)
    except Exception:
        await message.reply_text(text)
