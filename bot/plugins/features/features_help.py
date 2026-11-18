"""
📋 Feature pack help
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
╚════════════════════════════╝

📢 <code>{P}spam</code> <code>{P}typing</code> <code>{P}typing24</code>
🎨 <code>{P}kang</code> <code>{P}sticker</code> <code>{P}meme</code>
🎮 <code>{P}truth</code> <code>{P}dare</code> <code>{P}quiz</code>
📨 <code>{P}af</code> <code>{P}fwd</code> <code>{P}fcomment</code>
🎁 <code>{P}giveaway</code> 🎂 <code>{P}bdayadd</code> <code>{P}bdays</code>
🛡️ <code>{P}protect</code> 📹 <code>{P}cctv</code> 📍 <code>{P}fakeloc</code>
🤖 <code>{P}aidost</code> 💼 <code>{P}biz</code>
🌅 <code>{P}gmnow</code> 🔎 <code>{P}search</code> 🎬 <code>{P}movie</code>
💾 <code>{P}backup</code> 🔒 <code>{P}chatlock</code>
🖼 <code>{P}arphoto</code> 🎙️ <code>{P}vtt</code>

🆕 <b>New extras</b>
👻 <code>{P}ghost</code> <code>{P}ghoststatus</code>
⏱️ <code>{P}screentime</code> <code>{P}uptime</code>
🎙️ <code>{P}vf</code> <code>{P}vrobot</code>
🖼 <code>{P}photocheck</code>
🧠 <code>{P}aiboss</code> <code>{P}blockid</code> <code>{P}bosslist</code>
⏰ <code>{P}remind 5m text</code> <code>{P}remindlist</code>
🌐 <code>{P}panel</code>

Core (alag files): <code>{P}purge</code> <code>{P}tr</code> <code>{P}filter</code>
<code>{P}alive</code> <code>{P}afk</code> <code>{P}tagall</code> <code>{P}login</code>
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
