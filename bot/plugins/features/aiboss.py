from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
P = config.COMMAND_PREFIX
BOSS_ON = False
BLOCKED = set()
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["aiboss"], prefixes=P))
async def aiboss_cmd(client, message: Message):
    global BOSS_ON
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    if arg in ("on", "1"): BOSS_ON = True
    elif arg in ("off", "0"): BOSS_ON = False
    else: BOSS_ON = not BOSS_ON
    await _out(message, f"🧠 AI Boss: {'ON' if BOSS_ON else 'OFF'} | blocked={len(BLOCKED)}")
@app.on_message(filters.command(["blockid"], prefixes=P))
async def blockid_cmd(client, message: Message):
    uid = None
    if message.reply_to_message and message.reply_to_message.from_user:
        uid = message.reply_to_message.from_user.id
    elif len(message.command) > 1 and message.command[1].isdigit():
        uid = int(message.command[1])
    if not uid:
        await _out(message, f"<code>{P}blockid 123</code>"); return
    BLOCKED.add(uid); await _out(message, f"🚫 <code>{uid}</code>")
@app.on_message(filters.command(["unblockid"], prefixes=P))
async def unblockid_cmd(client, message: Message):
    if len(message.command) < 2 or not message.command[1].isdigit():
        await _out(message, f"<code>{P}unblockid 123</code>"); return
    BLOCKED.discard(int(message.command[1])); await _out(message, "✅ Unblocked")
@app.on_message(filters.command(["bosslist"], prefixes=P))
async def bosslist_cmd(client, message: Message):
    if not BLOCKED:
        await _out(message, "📭 Empty"); return
    await _out(message, "🧠\n" + "\n".join(f"• <code>{i}</code>" for i in list(BLOCKED)[:50]))
