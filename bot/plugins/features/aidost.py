import random
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from bot.client import app
import config
P = config.COMMAND_PREFIX
AI_ON = False
LINES = ["Haan bolo 😊", "Acha, phir?", "Hmm interesting…", "Main yahin hu ✨"]
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["aidost"], prefixes=P))
async def aidost_cmd(client, message: Message):
    global AI_ON
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    if arg in ("on", "1"): AI_ON = True
    elif arg in ("off", "0"): AI_ON = False
    else: AI_ON = not AI_ON
    await _out(message, f"🤖 AI Dost: {'ON' if AI_ON else 'OFF'}")
@app.on_message(filters.private & filters.incoming & ~filters.me & filters.text, group=57)
async def aidost_watch(client, message: Message):
    if not AI_ON: return
    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        await message.reply_text(random.choice(LINES))
    except Exception: pass
