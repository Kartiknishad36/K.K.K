"""
📥 Media Download Module — full details

.dl / .download     — reply media download
.mdl                — same
.batchdl            — download last N media in chat
.getthumb           — photo/video thumb
.savemedia          — download + send to Saved Messages
.mediainfo          — replied media full details
"""
import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path

from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
DL_DIR = Path(getattr(config, "DATA_DIR", Path("data"))) / "downloads"
DL_DIR.mkdir(parents=True, exist_ok=True)


async def _out(message, text):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None


def _media_kind(m: Message) -> str:
    if not m:
        return "none"
    if m.photo:
        return "photo"
    if m.video:
        return "video"
    if m.animation:
        return "animation"
    if m.audio:
        return "audio"
    if m.voice:
        return "voice"
    if m.video_note:
        return "video_note"
    if m.document:
        return "document"
    if m.sticker:
        return "sticker"
    return "unknown"


def _media_details(m: Message) -> str:
    kind = _media_kind(m)
    lines = [
        "╔══ 🎞 <b>MEDIA INFO</b> ══╗",
        f"01 Type: <b>{kind}</b>",
        f"02 Msg ID: <code>{m.id}</code>",
        f"03 Chat: <code>{m.chat.id if m.chat else 'N/A'}</code>",
        f"04 Date: {m.date}",
        f"05 Caption: {(m.caption or 'None')[:80]}",
    ]
    if m.photo:
        p = m.photo
        lines += [
            f"06 Photo file_id: <code>{p.file_id[:40]}...</code>",
            f"07 W×H: {p.width}×{p.height}",
            f"08 Size: {p.file_size or 0} bytes",
        ]
    if m.video:
        v = m.video
        lines += [
            f"06 Duration: {v.duration}s",
            f"07 W×H: {v.width}×{v.height}",
            f"08 Size: {v.file_size or 0} bytes",
            f"09 MIME: {v.mime_type}",
            f"10 File: {v.file_name or 'N/A'}",
        ]
    if m.document:
        d = m.document
        lines += [
            f"06 File: {d.file_name or 'N/A'}",
            f"07 MIME: {d.mime_type}",
            f"08 Size: {d.file_size or 0} bytes",
        ]
    if m.audio:
        a = m.audio
        lines += [
            f"06 Title: {a.title or 'N/A'}",
            f"07 Performer: {a.performer or 'N/A'}",
            f"08 Duration: {a.duration}s",
            f"09 Size: {a.file_size or 0} bytes",
        ]
    if m.voice:
        lines.append(f"06 Voice duration: {m.voice.duration}s")
    if m.animation:
        an = m.animation
        lines += [
            f"06 Duration: {an.duration}s",
            f"07 W×H: {an.width}×{an.height}",
            f"08 Size: {an.file_size or 0} bytes",
        ]
    if m.sticker:
        s = m.sticker
        lines += [
            f"06 Emoji: {s.emoji}",
            f"07 Set: {s.set_name}",
            f"08 Animated: {s.is_animated}",
            f"09 Video: {s.is_video}",
        ]
    lines.append("└─ END MEDIA INFO")
    return "\n".join(lines)


@app.on_message(filters.command(["mediainfo", "minfo"], prefixes=P))
async def mediainfo_cmd(client, message: Message):
    r = message.reply_to_message
    if not r or not r.media:
        await _out(message, f"📎 Reply to media + <code>{P}mediainfo</code>")
        return
    await _out(message, _media_details(r))


@app.on_message(filters.command(["dl", "download", "mdl"], prefixes=P))
async def download_cmd(client, message: Message):
    r = message.reply_to_message
    if not r or not r.media:
        await _out(
            message,
            f"╔══ 📥 <b>DOWNLOAD</b> ══╗\n"
            f"• Reply media + <code>{P}dl</code>\n"
            f"• <code>{P}savemedia</code> → Saved Messages\n"
            f"• <code>{P}mediainfo</code> → full details\n"
            f"• <code>{P}batchdl 5</code> → last N media\n"
            f"╚══════════════════╝",
        )
        return
    status = await _out(message, f"⬇️ Downloading <b>{_media_kind(r)}</b>...")
    try:
        path = await r.download(file_name=str(DL_DIR) + "/")
        size = os.path.getsize(path) if path and os.path.exists(path) else 0
        text = (
            f"✅ <b>Downloaded</b>\n"
            f"📁 <code>{path}</code>\n"
            f"📦 Size: <code>{size}</code> bytes\n"
            f"🎞 Type: {_media_kind(r)}"
        )
        if status:
            await status.edit_text(text)
        else:
            await _out(message, text)
    except Exception as e:
        err = f"❌ <code>{type(e).__name__}: {e}</code>"
        if status:
            try:
                await status.edit_text(err)
            except Exception:
                pass
        else:
            await _out(message, err)


@app.on_message(filters.command(["savemedia", "smdl"], prefixes=P))
async def savemedia_cmd(client, message: Message):
    r = message.reply_to_message
    if not r or not r.media:
        await _out(message, f"Reply media + <code>{P}savemedia</code>")
        return
    status = await _out(message, "💾 Saving to Saved Messages...")
    try:
        path = await r.download(file_name=str(DL_DIR) + "/")
        await client.send_document(
            "me",
            path,
            caption=f"📥 Saved • {_media_kind(r)} • {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}",
        )
        if status:
            await status.edit_text("✅ Saved Messages me bhej diya.")
    except Exception as e:
        if status:
            try:
                await status.edit_text(f"❌ <code>{e}</code>")
            except Exception:
                pass


@app.on_message(filters.command(["getthumb", "thumb"], prefixes=P))
async def getthumb_cmd(client, message: Message):
    r = message.reply_to_message
    if not r:
        await _out(message, f"Reply video/photo + <code>{P}getthumb</code>")
        return
    try:
        if r.video and r.video.thumbs:
            path = await client.download_media(r.video.thumbs[-1].file_id)
            await message.reply_photo(path, caption="🖼 Video thumb")
        elif r.photo:
            await message.reply_text("ℹ️ Ye already photo hai.")
        else:
            await _out(message, "❌ Thumb nahi mila.")
    except Exception as e:
        await _out(message, f"❌ <code>{e}</code>")


@app.on_message(filters.command(["batchdl"], prefixes=P))
async def batchdl_cmd(client, message: Message):
    n = 5
    if len(message.command) > 1 and message.command[1].isdigit():
        n = min(int(message.command[1]), 20)
    status = await _out(message, f"📥 Batch download last <code>{n}</code> media...")
    got = 0
    try:
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
            await asyncio.sleep(0.4)
        if status:
            await status.edit_text(f"✅ Batch done: <code>{got}</code> files → <code>{DL_DIR}</code>")
    except Exception as e:
        if status:
            try:
                await status.edit_text(f"❌ <code>{e}</code>")
            except Exception:
                pass
