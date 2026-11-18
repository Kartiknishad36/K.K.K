from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
P = config.COMMAND_PREFIX
TEXT = f"""
╔══ ✨ <b>FEATURE FILES</b> ══╗
<code>{P}spam</code> <code>{P}typing</code> <code>{P}kang</code> <code>{P}sticker</code>
<code>{P}truth</code> <code>{P}dare</code> <code>{P}riddle</code> <code>{P}quiz</code>
<code>{P}af</code> <code>{P}fwd</code> <code>{P}fcomment</code>
<code>{P}giveaway</code> <code>{P}bdayadd</code> <code>{P}bdays</code>
<code>{P}protect</code> <code>{P}cctv</code> <code>{P}meme</code> <code>{P}fakeloc</code>
<code>{P}aidost</code> <code>{P}biz</code> <code>{P}gmnow</code> <code>{P}search</code>
<code>{P}movie</code> <code>{P}backup</code> <code>{P}chatlock</code>
<code>{P}arphoto</code> <code>{P}vtt</code> <code>{P}ghost</code>
<code>{P}screentime</code> <code>{P}vf</code> <code>{P}vrobot</code>
<code>{P}photocheck</code> <code>{P}aiboss</code> <code>{P}remind</code>
<code>{P}panel</code>
╚══════════════════╝
"""
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["fhelp", "features", "feat"], prefixes=P))
async def fhelp_cmd(client, message: Message):
    await _out(message, TEXT)
