"""
📋 Feature pack help — only NON-duplicate extras
.fhelp / .features / .feat
"""
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX

TEXT = f"""
╔════════════════════════════╗
║  ✨ <b>FEATURE PACK</b> ✨  ║
║  (no duplicates vs core)   ║
╚════════════════════════════╝

📢 <code>{P}spam</code> <code>{P}typing</code> <code>{P}typing24</code>
🎨 <code>{P}kang</code> <code>{P}sticker</code> <code>{P}meme</code>
🎮 <code>{P}truth</code> <code>{P}dare</code> <code>{P}riddle</code> <code>{P}quiz</code>
📨 <code>{P}af</code> <code>{P}afset</code> <code>{P}fwd</code> <code>{P}fcomment</code>
🎁 <code>{P}giveaway</code> 🎂 <code>{P}bdayadd</code> <code>{P}bdays</code>
🛡️ <code>{P}protect</code> 📹 <code>{P}cctv</code> 📍 <code>{P}fakeloc</code>
🤖 <code>{P}aidost</code> 💼 <code>{P}biz</code> <code>{P}bizadd</code>
🌅 <code>{P}gm</code> <code>{P}gmnow</code> 🔎 <code>{P}search</code>
🎬 <code>{P}movie</code>
💾 <code>{P}backup</code> 🔒 <code>{P}chatlock</code>
🖼 <code>{P}arphoto</code> 🎙️ <code>{P}vtt</code>

────────────────────
📦 <b>Already in core</b> (use those)
• <code>{P}purge</code> → admin.py
• <code>{P}tr</code> → tools.py
• <code>{P}filter</code> / <code>{P}filters</code> → filters.py
• <code>{P}alive</code> <code>{P}ping</code> <code>{P}afk</code> <code>{P}tagall</code>
• <code>{P}login</code> multi-account · <code>{P}auto</code> self_ai
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
