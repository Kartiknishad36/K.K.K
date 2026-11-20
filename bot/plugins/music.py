"""
🎵 Music — public all groups

.play / .vplay / .cplay  query|url|reply
→ search → download (Shruti API + multi URL + yt-dlp)
→ auto VC join/play
→ thumb + requester DP + song card + audio

Env:
  SHRUTI_API_URL=https://api.shrutibots.in
  SHRUTI_API_KEY=...
"""
from __future__ import annotations

import os
import re
import asyncio
from pathlib import Path
from typing import Any

import aiohttp
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType, ChatType

from bot.client import app
from bot.helpers import vc as vcmod
import config

P = config.COMMAND_PREFIX
API_KEY = getattr(config, "SHRUTI_API_KEY", None) or os.getenv("SHRUTI_API_KEY") or ""
# try multiple known bases if one fails
_API_BASES = []
for u in [
    getattr(config, "SHRUTI_API_URL", None) or os.getenv("SHRUTI_API_URL"),
    "https://api.shrutibots.in",
    "https://api01.shrutibots.site",
    "https://api.shrutibots.site",
]:
    if u:
        u = u.rstrip("/")
        if u not in _API_BASES:
            _API_BASES.append(u)

DOWNLOAD_DIR = Path(getattr(config, "DATA_DIR", Path("data"))) / "music"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

YT_ID_RE = re.compile(
    r"(?:youtube\.com/(?:watch\?v=|shorts/|embed/)|youtu\.be/)([\w-]{6,})"
)
URL_RE = re.compile(r"https?://\S+")


async def _out(m: Message, t: str):
    try:
        return await m.reply_text(t)
    except Exception:
        try:
            return await m.edit_text(t)
        except Exception:
            return None


def _extract_yt_id(text: str) -> str | None:
    if not text:
        return None
    m = YT_ID_RE.search(text)
    if m:
        return m.group(1)
    t = text.strip()
    if re.fullmatch(r"[\w-]{11}", t):
        return t
    return None


def _urls_from_message(message: Message) -> list[str]:
    urls = []
    text = message.text or message.caption or ""
    if text:
        urls.extend(URL_RE.findall(text))
    entities = list(message.entities or []) + list(message.caption_entities or [])
    for e in entities:
        if e.type == MessageEntityType.URL and text:
            urls.append(text[e.offset : e.offset + e.length])
        elif e.type == MessageEntityType.TEXT_LINK and e.url:
            urls.append(e.url)
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def _query_from_message(message: Message) -> str:
    if message.command and len(message.command) > 1:
        return message.text.split(None, 1)[1].strip()
    r = message.reply_to_message
    if r:
        urls = _urls_from_message(r)
        if urls:
            return urls[0]
        return (r.text or r.caption or "").strip()
    urls = _urls_from_message(message)
    return urls[0] if urls else ""


def thumb_url(vid: str) -> str:
    if not vid or len(vid) < 6 or vid.startswith("http"):
        return ""
    return f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"


async def yt_search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    try:
        from youtube_search import YoutubeSearch

        for item in YoutubeSearch(query, max_results=limit).to_dict():
            vid = item.get("id") or ""
            results.append(
                {
                    "id": vid,
                    "title": item.get("title") or "Unknown",
                    "duration": item.get("duration") or "?",
                    "url": f"https://www.youtube.com/watch?v={vid}" if vid else "",
                    "channel": item.get("channel") or "",
                    "thumb": thumb_url(vid),
                }
            )
        if results:
            return results
    except Exception:
        pass
    try:
        from youtubesearchpython import VideosSearch

        for item in (VideosSearch(query, limit=limit).result().get("result") or []):
            vid = item.get("id") or ""
            ch = item.get("channel")
            th = ""
            thumbs = item.get("thumbnails") or []
            if thumbs:
                th = thumbs[0].get("url") or ""
            results.append(
                {
                    "id": vid,
                    "title": item.get("title") or "Unknown",
                    "duration": item.get("duration") or "?",
                    "url": item.get("link") or f"https://www.youtube.com/watch?v={vid}",
                    "channel": ch.get("name", "") if isinstance(ch, dict) else str(ch or ""),
                    "thumb": th or thumb_url(vid),
                }
            )
        if results:
            return results
    except Exception:
        pass
    try:
        import yt_dlp

        with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True, "extract_flat": True}) as ydl:
            info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            for e in (info or {}).get("entries") or []:
                if not e:
                    continue
                vid = e.get("id") or ""
                results.append(
                    {
                        "id": vid,
                        "title": e.get("title") or "Unknown",
                        "duration": str(e.get("duration") or "?"),
                        "url": e.get("webpage_url") or f"https://www.youtube.com/watch?v={vid}",
                        "channel": e.get("channel") or e.get("uploader") or "",
                        "thumb": thumb_url(vid),
                    }
                )
    except Exception:
        pass
    return results


async def resolve_track(query: str) -> dict[str, Any] | None:
    if not query:
        return None
    vid = _extract_yt_id(query)
    if vid:
        hits = await yt_search(f"https://www.youtube.com/watch?v={vid}", limit=1)
        if hits:
            return hits[0]
        return {
            "id": vid,
            "title": f"YouTube {vid}",
            "url": f"https://www.youtube.com/watch?v={vid}",
            "duration": "?",
            "channel": "",
            "thumb": thumb_url(vid),
        }
    if query.startswith("http"):
        return {"id": query, "title": query, "url": query, "duration": "?", "channel": "", "thumb": ""}
    hits = await yt_search(query, limit=1)
    return hits[0] if hits else None


async def shruti_download(video_id_or_url: str, media_type: str = "audio") -> Path | None:
    if not API_KEY:
        return None
    vid = _extract_yt_id(video_id_or_url) or video_id_or_url
    safe = re.sub(r"[^\w-]+", "_", str(vid))[:40]
    ext = "mp3" if media_type == "audio" else "mp4"
    path = DOWNLOAD_DIR / f"{safe}.{ext}"
    if path.exists() and path.stat().st_size > 1024:
        return path

    timeout = aiohttp.ClientTimeout(total=300)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for base in _API_BASES:
            try:
                async with session.get(
                    f"{base}/download",
                    params={"url": vid, "type": media_type, "api_key": API_KEY},
                ) as resp:
                    if resp.status != 200:
                        continue
                    with open(path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(131072):
                            f.write(chunk)
                if path.exists() and path.stat().st_size > 1024:
                    return path
                path.unlink(missing_ok=True)
            except Exception:
                try:
                    path.unlink(missing_ok=True)
                except Exception:
                    pass
    return None


async def ytdlp_download_audio(url: str) -> Path | None:
    try:
        import yt_dlp
    except ImportError:
        return None
    outtmpl = str(DOWNLOAD_DIR / "%(id)s.%(ext)s")

    def _run():
        opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": outtmpl,
            "quiet": True,
            "noplaylist": True,
            "nocheckcertificate": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            vid = (info or {}).get("id")
            if not vid:
                return None
            for ext in ("m4a", "webm", "mp3", "opus", "ogg"):
                cand = DOWNLOAD_DIR / f"{vid}.{ext}"
                if cand.exists() and cand.stat().st_size > 1024:
                    return cand
            return None

    try:
        return await asyncio.to_thread(_run)
    except Exception:
        return None


async def get_audio_file(track: dict) -> Path | None:
    vid = track.get("id") or ""
    url = track.get("url") or (f"https://www.youtube.com/watch?v={vid}" if vid else "")
    path = await shruti_download(vid or url, "audio")
    if path:
        return path
    if url:
        return await ytdlp_download_audio(url)
    return None


async def _download_thumb(url: str) -> Path | None:
    if not url:
        return None
    path = DOWNLOAD_DIR / "thumb_tmp.jpg"
    try:
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.read()
                path.write_bytes(data)
                return path if path.stat().st_size > 100 else None
    except Exception:
        return None


async def _play_flow(client, message: Message, mode: str = "play"):
    query = _query_from_message(message)
    if not query:
        await _out(
            message,
            f"🎵 <code>{P}play song name</code>\n"
            f"Reply + <code>{P}play</code>\n"
            f"API key: <code>{'SET' if API_KEY else 'MISSING — Render/Railway pe SHRUTI_API_KEY daalo'}</code>",
        )
        return

    status = await _out(message, f"🔍 Searching…\n<code>{query[:80]}</code>")
    track = await resolve_track(query)
    if not track:
        if status:
            try:
                await status.edit_text("❌ Song nahi mili")
            except Exception:
                pass
        return

    title = track.get("title") or "Track"
    vid = track.get("id") or ""
    if status:
        try:
            await status.edit_text(f"⬇️ Downloading…\n🎵 <b>{title}</b>")
        except Exception:
            pass

    path = await get_audio_file(track)
    if not path:
        if status:
            try:
                await status.edit_text(
                    "❌ Download fail\n"
                    f"• SHRUTI_API_KEY: <code>{'set' if API_KEY else 'NOT SET'}</code>\n"
                    f"• Tried: <code>{', '.join(_API_BASES)}</code>\n"
                    "• yt-dlp fallback bhi fail (ffmpeg/network?)\n"
                    "Render/Railway env me key daal ke redeploy karo"
                )
            except Exception:
                pass
        return

    who = message.from_user
    who_name = who.mention if who else "User"
    chat = message.chat
    is_group = chat and chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)

    # --- auto VC ---
    vc_line = ""
    if is_group:
        if status:
            try:
                await status.edit_text(f"🎙️ VC join…\n🎵 <b>{title}</b>")
            except Exception:
                pass
        ok, info = await vcmod.play_file(client, chat.id, path, title=title)
        vc_line = f"\n🎙️ <b>VC:</b> {'✅ ' + info if ok else '⚠️ ' + info}"

    # --- card: thumb + DP + name ---
    thumb = track.get("thumb") or thumb_url(vid)
    caption = (
        f"🎵 <b>{title}</b>\n"
        f"👤 Requested by: {who_name}\n"
        f"📺 {track.get('channel') or 'YouTube'}\n"
        f"⏱ {track.get('duration', '?')} | 📡 <code>{mode}</code>\n"
        f"🔗 {track.get('url', '')}"
        f"{vc_line}"
    )

    try:
        # 1) photo card with song art
        tpath = await _download_thumb(thumb)
        if tpath:
            try:
                await message.reply_photo(str(tpath), caption=caption)
            except Exception:
                await message.reply_text(caption)
            try:
                tpath.unlink(missing_ok=True)
            except Exception:
                pass
        else:
            await message.reply_text(caption)

        # 2) requester DP (small)
        if who:
            try:
                photos = [p async for p in client.get_chat_photos(who.id, limit=1)]
                if photos:
                    await message.reply_photo(
                        photos[0].file_id,
                        caption=f"🎧 Requested by {who_name}",
                    )
            except Exception:
                pass

        # 3) audio / video file
        if mode == "vplay":
            vpath = await shruti_download(vid or track.get("url"), "video")
            if vpath:
                await message.reply_video(str(vpath), caption=f"🎬 {title}")
            else:
                await message.reply_audio(str(path), title=title[:64], caption=f"🎧 {title}")
        else:
            await message.reply_audio(str(path), title=title[:64], caption=f"🎧 {title}")

        if status:
            try:
                await status.delete()
            except Exception:
                pass
    except Exception as e:
        if status:
            try:
                await status.edit_text(f"❌ Send fail: <code>{e}</code>")
            except Exception:
                pass


@app.on_message(filters.command(["play", "song"], prefixes=P))
async def play_cmd(client, message: Message):
    await _play_flow(client, message, mode="play")


@app.on_message(filters.command(["vplay"], prefixes=P))
async def vplay_cmd(client, message: Message):
    await _play_flow(client, message, mode="vplay")


@app.on_message(filters.command(["cplay"], prefixes=P))
async def cplay_cmd(client, message: Message):
    await _play_flow(client, message, mode="cplay")


@app.on_message(filters.command(["songsearch", "ssearch", "ys"], prefixes=P))
async def songsearch_cmd(client, message: Message):
    q = _query_from_message(message)
    if not q:
        await _out(message, f"Usage: <code>{P}songsearch name</code>")
        return
    status = await _out(message, f"🔎 <code>{q[:60]}</code>…")
    hits = await yt_search(q, limit=8)
    if not hits:
        if status:
            try:
                await status.edit_text("❌ No results")
            except Exception:
                pass
        return
    lines = [f"🔎 <b>{q[:40]}</b>", ""]
    for i, h in enumerate(hits, 1):
        lines.append(
            f"<b>{i}.</b> {h.get('title')}\n"
            f"    ⏱ {h.get('duration')} · {h.get('channel')}\n"
            f"    <code>{P}play {h.get('url')}</code>"
        )
    text = "\n".join(lines)
    if status:
        try:
            await status.edit_text(text)
            return
        except Exception:
            pass
    await _out(message, text)


@app.on_message(filters.command(["stop"], prefixes=P))
async def stop_cmd(client, message: Message):
    await _out(message, f"⏹ {await vcmod.stop(message.chat.id)}")


@app.on_message(filters.command(["skip"], prefixes=P))
async def skip_cmd(client, message: Message):
    await _out(message, f"⏭ {await vcmod.skip(message.chat.id)}")


@app.on_message(filters.command(["joinvc"], prefixes=P))
async def joinvc_cmd(client, message: Message):
    ok, info = await vcmod.ensure_group_call(client, message.chat.id)
    await _out(message, f"{'✅' if ok else '❌'} {info}")


@app.on_message(filters.command(["leavevc"], prefixes=P))
async def leavevc_cmd(client, message: Message):
    await _out(message, f"🚪 {await vcmod.stop(message.chat.id)}")


@app.on_message(filters.command(["musichelp", "mhelp"], prefixes=P))
async def musichelp_cmd(client, message: Message):
    await _out(
        message,
        f"🎵 <b>Music</b> — all members / all groups\n\n"
        f"<code>{P}play</code> <code>{P}vplay</code> <code>{P}cplay</code>\n"
        f"<code>{P}songsearch</code> <code>{P}stop</code> <code>{P}skip</code>\n"
        f"<code>{P}joinvc</code> <code>{P}leavevc</code>\n\n"
        f"Play = thumb + DP + audio + auto VC try\n"
        f"API key: <code>{'✅' if API_KEY else '❌ NOT SET'}</code>",
    )
