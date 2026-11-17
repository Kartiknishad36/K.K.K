"""
📥 Media Download — reply + URL links
.dl / .dl <url> / .savemedia / .mediainfo / .batchdl / .getthumb
"""
import asyncio
import os
import re
from pathlib import Path
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
DL_DIR = Path(getattr(config, "DATA_DIR", Path("data"))) / "downloads"
DL_DIR.mkdir(parents=True, exist_ok=True)
URL_RE = re.compile(r"https?://\S+", re.I)

async def _out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

def _kind(m):
    for k in ("photo", "video", "animation", "audio", "voice", "document", "sticker", "video_note"):
        if getattr(m, k, None):
            return k
    return "media"

def _download_url_sync(url: str) -> str:
    out_tmpl = str(DL_DIR / "%(title).80s.%(ext)s")
    try:
        import yt_dlp
        opts = {"outtmpl": out_tmpl, "quiet": True, "noplaylist": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            if path and os.path.exists(path):
                return path
            for ext in ("mp4", "webm", "mkv", "mp3"):
                p2 = path.rsplit(".", 1)[0] + "." + ext if path else ""
                if p2 and os.path.exists(p2):
                    return p2
    except Exception:
        pass
    import urllib.request
    name = url.split("?")[0].rstrip("/").split("/")[-1] or "file.bin"
    if "." not in name:
        name += ".bin"
    path = str(DL_DIR / name[:80])
    urllib.request.urlretrieve(url, path)
    return path

@app.on_message(filters.command(["mediainfo", "minfo"], prefixes=P))
async def mediainfo_cmd(client, message: Message):
    r = message.reply_to_message
    if not r or not r.media:
        await _out(message, f"📎 Reply + <code>{P}mediainfo</code>")
        return
    lines = ["╔══ 🎞 <b>MEDIA INFO</b> ══╗", f"01 Type: <b>{_kind(r)}</b>", f"02 Msg: <code>{r.id}</code>"]
    if r.video:
        lines += [f"05 Duration: {r.video.duration}s", f"06 Size: {r.video.file_size}"]
    if r.document:
        lines += [f"05 File: {r.document.file_name}", f"06 Size: {r.document.file_size}"]
    if r.photo:
        lines += [f"05 W×H: {r.photo.width}×{r.photo.height}"]
    lines.append("└─ END")
    await _out(message, "\n".join(lines))

@app.on_message(filters.command(["dl", "download", "mdl"], prefixes=P))
async def download_cmd(client, message: Message):
    url = None
    if len(message.command) > 1:
        m = URL_RE.search(message.text or "")
        if m:
            url = m.group(0)
    if url:
        status = await _out(message, f"⬇️ Link download...\n<code>{url[:60]}</code>")
        try:
            path = await asyncio.to_thread(_download_url_sync, url)
            size = os.path.getsize(path) if path and os.path.exists(path) else 0
            try:
                await message.reply_document(path, caption=f"✅ Link DL\n📦 {size} bytes")
            except Exception:
                await message.reply_text(f"✅ <code>{path}</code>\n📦 {size}")
            if status:
                try:
                    await status.delete()
                except Exception:
                    pass
        except Exception as e:
            if status:
                await status.edit_text(f"❌ <code>{e}</code>")
        return
    r = message.reply_to_message
    if not r or not r.media:
        await _out(message, f"╔══ 📥 <b>DOWNLOAD</b> ══╗\n• Reply + <code>{P}dl</code>\n• <code>{P}dl https://...</code>\n• <code>{P}savemedia</code>\n• <code>{P}batchdl 5</code>\n╚══════════════════╝")
        return
    status = await _out(message, f"⬇️ Downloading <b>{_kind(r)}</b>...")
    try:
        path = await r.download(file_name=str(DL_DIR) + "/")
        size = os.path.getsize(path) if path and os.path.exists(path) else 0
        if status:
            await status.edit_text(f"✅ <code>{path}</code>\n📦 {size} bytes")
    except Exception as e:
        if status:
            await status.edit_text(f"❌ <code>{e}</code>")

@app.on_message(filters.command(["savemedia", "smdl"], prefixes=P))
async def savemedia_cmd(client, message: Message):
    r = message.reply_to_message
    if not r or not r.media:
        await _out(message, f"Reply + <code>{P}savemedia</code>")
        return
    status = await _out(message, "💾 Saving...")
    try:
        path = await r.download(file_name=str(DL_DIR) + "/")
        await client.send_document("me", path, caption=f"📥 {_kind(r)}")
        if status:
            await status.edit_text("✅ Saved Messages")
    except Exception as e:
        if status:
            await status.edit_text(f"❌ <code>{e}</code>")

@app.on_message(filters.command(["getthumb", "thumb"], prefixes=P))
async def getthumb_cmd(client, message: Message):
    r = message.reply_to_message
    if not r or not r.video or not r.video.thumbs:
        await _out(message, "Reply video")
        return
    path = await client.download_media(r.video.thumbs[-1].file_id)
    await message.reply_photo(path, caption="🖼 Thumb")

@app.on_message(filters.command(["batchdl"], prefixes=P))
async def batchdl_cmd(client, message: Message):
    n = 5
    if len(message.command) > 1 and message.command[1].isdigit():
        n = min(int(message.command[1]), 20)
    status = await _out(message, f"📥 Batch {n}...")
    got = 0
    async for m in client.get_chat_history(message.chat.id, limit=80):
        if got >= n:
            break
        if not m.media:
            continue
        try:
            await m.download(file_name=str(DL_DIR) + "/")
            got += 1
        except Exception:
            pass
        await asyncio.sleep(0.3)
    if status:
        await status.edit_text(f"✅ {got} files")
