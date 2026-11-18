"""
🖼 Photo check / meta
.photocheck — reply photo
.imginfo — same
"""
import os
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX


async def _out(m, t):
    try:
        return await m.reply_text(t)
    except Exception:
        try:
            return await m.edit_text(t)
        except Exception:
            return None


@app.on_message(filters.command(["photocheck", "imginfo", "photometa"], prefixes=P))
async def photocheck_cmd(client, message: Message):
    r = message.reply_to_message
    if not r or not r.photo:
        await _out(message, f"Reply photo + <code>{P}photocheck</code>")
        return
    p = r.photo
    lines = [
        "🖼 <b>Photo Meta</b>",
        f"01 File ID: <code>{p.file_id[:40]}...</code>",
        f"02 Unique: <code>{p.file_unique_id}</code>",
        f"03 W×H: <code>{p.width}×{p.height}</code>",
        f"04 Size: <code>{p.file_size or 'N/A'}</code> bytes",
    ]
    path = None
    try:
        path = await r.download()
        lines.append(f"05 Local: <code>{path}</code>")
        try:
            from PIL import Image

            img = Image.open(path)
            lines.append(f"06 Format: <code>{img.format}</code>")
            lines.append(f"07 Mode: <code>{img.mode}</code>")
            lines.append(f"08 PIL size: <code>{img.size}</code>")
            # basic "suspicious" heuristics only
            w, h = img.size
            if w < 50 or h < 50:
                lines.append("09 Flag: very small image")
            else:
                lines.append("09 Flag: normal dimensions")
        except Exception as e:
            lines.append(f"06 PIL: {e}")
    except Exception as e:
        lines.append(f"05 Download error: {e}")
    finally:
        if path:
            try:
                os.remove(path)
            except Exception:
                pass
    lines.append("\n⚠️ Ye real deepfake-detect nahi hai — sirf meta.")
    await _out(message, "\n".join(lines))
