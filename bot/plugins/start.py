from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
import time

P = config.COMMAND_PREFIX

HELP_TEXT = f"""
╔══════════════════════════╗
║   🤖  <b>K.K.K USERBOT</b>   ║
║      ✨ Premium Menu ✨     ║
╚══════════════════════════╝

🔹 <b>Prefix:</b> <code>{P}</code>
🔹 <b>Modules:</b> full loaded

────────────────────
📌 <b>BASIC</b>
────────────────────
• <code>{P}help</code> — yeh menu
• <code>{P}ping</code> — speed check
• <code>{P}alive</code> — status
• <code>{P}id</code> — chat / user id
• <code>{P}stats</code> — account stats

────────────────────
🔐 <b>MULTI LOGIN</b>
────────────────────
• <code>{P}login</code> — login help
• <code>{P}addsession</code> — dusra account add
• <code>{P}logins</code> — saved accounts
• <code>{P}delsession</code> — account hatao
• <code>{P}mylogin</code> — main account

────────────────────
📢 <b>BROADCAST</b>
────────────────────
• <code>{P}broadcast</code> — groups + channels
• <code>{P}gcast</code> — only groups
• <code>{P}dmcast</code> — only DMs
• <code>{P}stopcast</code> — stop
• <code>{P}caststatus</code> — status

────────────────────
📥 <b>MEDIA</b>
────────────────────
• <code>{P}dl</code> — reply download
• <code>{P}savemedia</code> — Saved Messages
• <code>{P}mediainfo</code> — full media info
• <code>{P}batchdl</code> — last N media
• <code>{P}getthumb</code> — video thumb

────────────────────
😴 <b>AFK</b>
────────────────────
• <code>{P}afk</code> / <code>{P}unafk</code>

────────────────────
📝 <b>NOTES & FILTERS</b>
────────────────────
• <code>{P}save</code> <code>{P}get</code> <code>{P}notes</code>
• <code>{P}filter</code> <code>{P}stop</code> <code>{P}filters</code>

────────────────────
👋 <b>WELCOME / AUTODEL</b>
────────────────────
• <code>{P}setwelcome</code> <code>{P}welcome</code>
• <code>{P}autodel</code> <code>{P}cmddel</code>

────────────────────
🛡️ <b>ADMIN</b>
────────────────────
• ban unban kick mute unmute
• promote demote pin purge gban

────────────────────
👥 <b>TAGALL</b>
────────────────────
• <code>{P}tagall</code> <code>{P}tag</code> <code>{P}tagadmin</code>
• <code>{P}tagallstop</code>

────────────────────
🔥 <b>BRO / FUN</b>
────────────────────
• <code>{P}bro</code> <code>{P}broall</code> <code>{P}unbro</code>
• <code>{P}cat</code> <code>{P}rose</code> <code>{P}hacker</code>
• <code>{P}moon</code> <code>{P}heart</code>

────────────────────
🛠️ <b>TOOLS</b>
────────────────────
• <code>{P}info</code> <code>{P}whois</code>
• <code>{P}join</code> <code>{P}leave</code> <code>{P}invite</code>
• <code>{P}pclone</code> <code>{P}back</code>
• <code>{P}sha</code> <code>{P}time</code> <code>{P}echo</code>

╚══════════════════════════╝
"""


async def _out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None


@app.on_message(filters.command(["help", "menu", "cmds"], prefixes=P))
async def help_cmd(client, message: Message):
    await _out(message, HELP_TEXT)


@app.on_message(filters.command(["ping"], prefixes=P))
async def ping_cmd(client, message: Message):
    t1 = time.time()
    m = await _out(message, "🏓 pong...")
    t2 = time.time()
    if m:
        try:
            await m.edit_text(f"🏓 <b>Pong</b>\n⚡ <code>{(t2 - t1) * 1000:.0f} ms</code>")
        except Exception:
            pass


@app.on_message(filters.command(["alive"], prefixes=P))
async def alive_cmd(client, message: Message):
    me = await client.get_me()
    await _out(
        message,
        f"╔══ ✅ <b>ALIVE</b> ══╗\n"
        f"👤 {me.first_name}\n"
        f"🆔 <code>{me.id}</code>\n"
        f"🔹 Prefix: <code>{P}</code>\n"
        f"💎 Premium: {getattr(me, 'is_premium', False)}\n"
        f"╚══════════════╝",
    )


@app.on_message(filters.command(["id"], prefixes=P))
async def id_cmd(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        await _out(
            message,
            f"👤 <b>{u.first_name}</b>\n"
            f"🆔 <code>{u.id}</code>\n"
            f"💬 Chat: <code>{message.chat.id}</code>\n"
            f"🔗 @{u.username or 'None'}",
        )
    else:
        await _out(
            message,
            f"💬 Chat: <code>{message.chat.id}</code>\n"
            f"👤 You: <code>{message.from_user.id if message.from_user else 'N/A'}</code>\n"
            f"📂 Type: {message.chat.type}",
        )
