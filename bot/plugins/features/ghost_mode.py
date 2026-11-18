"""
👻 Ghost Mode
Messages read without pushing "seen" when possible.

.ghost on|off
.ghoststatus

Note: Telegram always may mark read on open in official apps.
Userbot side: we avoid calling read_chat_history while ON.
"""
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
GHOST = False


async def _out(m, t):
    try:
        return await m.reply_text(t)
    except Exception:
        try:
            return await m.edit_text(t)
        except Exception:
            return None


@app.on_message(filters.command(["ghost"], prefixes=P))
async def ghost_cmd(client, message: Message):
    global GHOST
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    if arg in ("on", "1", "enable"):
        GHOST = True
    elif arg in ("off", "0", "disable"):
        GHOST = False
    else:
        GHOST = not GHOST
    await _out(
        message,
        f"👻 <b>Ghost Mode:</b> {'ON ✅' if GHOST else 'OFF ❌'}\n\n"
        f"• ON: bot will try <b>not</b> to mark chats as read\n"
        f"• Phone app se chat khologe to seen lag sakta hai\n"
        f"Status: <code>{P}ghoststatus</code>",
    )


@app.on_message(filters.command(["ghoststatus"], prefixes=P))
async def ghost_status(client, message: Message):
    await _out(
        message,
        f"👻 Ghost: <b>{'ON' if GHOST else 'OFF'}</b>\n"
        f"Toggle: <code>{P}ghost on</code> / <code>{P}ghost off</code>",
    )


# Optional: block read_history style updates while ghost — best-effort hook
@app.on_message(filters.incoming & ~filters.me, group=70)
async def ghost_no_read(client, message: Message):
    if not GHOST:
        return
    # Do nothing — no read_chat_history call
    return
