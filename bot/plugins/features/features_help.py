"""📋 .fhelp / .features"""
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
TEXT = f"""
╔════════════════════════════╗
║  ✨ <b>FEATURE PACK</b> ✨  ║
╚════════════════════════════╝

🧹 <code>{P}purge</code> <code>{P}spam</code> <code>{P}typing</code>
🎨 <code>{P}kang</code> <code>{P}sticker</code> <code>{P}meme</code>
🌐 <code>{P}tr</code> 🎮 <code>{P}truth</code> <code>{P}dare</code> <code>{P}quiz</code>
📨 <code>{P}af</code> <code>{P}fwd</code> <code>{P}fcomment</code>
🎁 <code>{P}giveaway</code> 🎂 <code>{P}bdayadd</code> <code>{P}bdays</code>
🛡️ <code>{P}protect</code> 📹 <code>{P}cctv</code> 📍 <code>{P}fakeloc</code>
🤖 <code>{P}aidost</code> 💼 <code>{P}biz</code>
🌅 <code>{P}gmnow</code> 🔎 <code>{P}search</code> 🎬 <code>{P}movie</code>
🧲 <code>{P}filteradd</code> 💾 <code>{P}backup</code>
🖼 <code>{P}arphoto</code>

⚠️ Skipped (safety/API): Fake Pay, OTP steal, Member chori, Fake Blue Tick, WhatsApp bridge, profile-view spy
Multi-account: <code>{P}login</code>
"""

async def _out(m, t):
    try:
        return await m.reply_text(t)
    except Exception:
        try:
            return await m.edit_text(t)
        except Exception:
            return None

@app.on_message(filters.command(["fhelp", "features", "feat"], prefixes=P))
async def fhelp_cmd(client, message: Message):
    await _out(message, TEXT)
