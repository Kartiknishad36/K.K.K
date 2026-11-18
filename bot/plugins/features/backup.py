from pathlib import Path
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
P = config.COMMAND_PREFIX
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["backup"], prefixes=P))
async def backup_cmd(client, message: Message):
    data = Path(getattr(config, "DATA_DIR", Path("data")))
    files = list(data.glob("*")) if data.exists() else []
    lines = [f"💾 <b>Backup</b>", f"Folder: <code>{data}</code>", f"Files: {len(files)}"]
    for f in files[:20]: lines.append(f"• {f.name} ({f.stat().st_size}b)")
    try:
        await client.send_message("me", "\n".join(lines))
        await _out(message, "✅ → Saved Messages")
    except Exception as e:
        await _out(message, f"❌ <code>{e}</code>")
