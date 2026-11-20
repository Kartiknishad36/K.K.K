"""
🎵 Music — Shruti API + search

.env:
  SHRUTI_API_URL=https://api.shrutibots.in
  SHRUTI_API_KEY=your_key

Commands:
  .play  <query|url>     — download audio, send in chat
  .vplay <query|url>     — same (video/audio for VC-style)
  .cplay <query|url>     — channel-style send audio
  .song  <query|url>     — alias of play
  .songsearch / .ssearch <query> — top search results

Supports: query text, youtube link, reply to msg with link/text.
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
from pyrogram.enums import MessageEntityType

from bot.client import app
import config

P = config.COMMAND_PREFIX
API_URL = (getattr(config, "SHRUTI_API_URL", None) or os.getenv("SHRUTI_API_URL") or "https://api.shrutibots.in").rstrip("/")
API_KEY = getattr(config, "SHRUTI_API_KEY", None) or os.getenv("SHRUTI_API_KEY") or ""
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
    # bare 11-char id
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
    # unique preserve order
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def _query_from_message(message: Message) -> str:
    # command args
    if message.command and len(message.command) > 1:
        return message.text.split(None, 1)[1].strip()
    # reply
    r = message.reply_to_message
    if r:
        urls = _urls_from_message(r)
        if urls:
            return urls[0]
        return (r.text or r.caption or "").strip()
    # own message urls
    urls = _urls_from_message(message)
    if urls:
        return urls[0]
    return ""


async def yt_search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Search YouTube; returns list of {id,title,duration,url,channel}."""
    results: list[dict[str, Any]] = []
    # 1) youtube-search-python / py_yt
    try:
        try:
            from youtube_search import YoutubeSearch

            data = YoutubeSearch(query, max_results=limit).to_dict()
            for item in data:
                vid = item.get("id") or ""
                results.append(
                    {
                        "id": vid,
                        "title": item.get("title") or "Unknown",
                        "duration": item.get("duration") or "?",
                        "url": f"https://www.youtube.com/watch?v={vid}" if vid else item.get("url_suffix", ""),
                        "channel": item.get("channel") or "",
                    }
                )
            if results:
                return results
        except Exception:
            pass
        try:
            from youtubesearchpython import VideosSearch

            vs = VideosSearch(query, limit=limit)
            data = vs.result().get("result") or []
            for item in data:
                vid = item.get("id") or ""
                results.append(
                    {
                        "id": vid,
                        "title": item.get("title") or "Unknown",
                        "duration": (item.get("duration") or "?"),
                        "url": item.get("link") or f"https://www.youtube.com/watch?v={vid}",
                        "channel": (item.get("channel") or {}).get("name", "") if isinstance(item.get("channel"), dict) else str(item.get("channel") or ""),
                    }
                )
            if results:
                return results
        except Exception:
            pass
    except Exception:
        pass

    # 2) yt-dlp search
    try:
        import yt_dlp

        ydl_opts = {"quiet": True, "skip_download": True, "extract_flat": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
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
                    }
                )
    except Exception:
        pass
    return results


async def resolve_track(query: str) -> dict[str, Any] | None:
    """Return {id,title,url,duration,channel} from url or search."""
    if not query:
        return None
    vid = _extract_yt_id(query)
    if vid:
        return {
            "id": vid,
            "title": query if "http" not in query else f"YouTube {vid}",
            "url": f"https://www.youtube.com/watch?v={vid}",
            "duration": "?",
            "channel": "",
        }
    # if other url, try as id via API later
    if query.startswith("http"):
        return {"id": query, "title": query, "url": query, "duration": "?", "channel": ""}
    hits = await yt_search(query, limit=1)
    return hits[0] if hits else None


async def shruti_download(video_id_or_url: str, media_type: str = "audio") -> Path | None:
    """Download via Shruti API → local path."""
    if not API_KEY:
        return None
    vid = _extract_yt_id(video_id_or_url) or video_id_or_url
    # sanitize filename
    safe = re.sub(r"[^\w-]+", "_", str(vid))[:40]
    ext = "mp3" if media_type == "audio" else "mp4"
    path = DOWNLOAD_DIR / f"{safe}.{ext}"
    if path.exists() and path.stat().st_size > 1024:
        return path

    url = f"{API_URL}/download"
    params = {"url": vid, "type": media_type, "api_key": API_KEY}
    try:
        timeout = aiohttp.ClientTimeout(total=300)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    return None
                # stream to file
                with open(path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(131072):
                        f.write(chunk)
        if path.exists() and path.stat().st_size > 1024:
            return path
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass
        return None
    except Exception:
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass
        return None


async def ytdlp_download_audio(url: str) -> Path | None:
    """Fallback yt-dlp audio download."""
    try:
        import yt_dlp
    except ImportError:
        return None
    outtmpl = str(DOWNLOAD_DIR / "%(id)s.%(ext)s")

    def _run():
        opts = {
            "format": "bestaudio/best",
            "outtmpl": outtmpl,
            "quiet": True,
            "noplaylist": True,
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
            ],
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            vid = info.get("id") if info else None
            if not vid:
                return None
            p = DOWNLOAD_DIR / f"{vid}.mp3"
            if p.exists():
                return p
            # maybe webm/m4a
            for ext in ("mp3", "m4a", "webm", "opus"):
                cand = DOWNLOAD_DIR / f"{vid}.{ext}"
                if cand.exists():
                    return cand
            return None

    try:
        return await asyncio.to_thread(_run)
    except Exception:
        return None


async def get_audio_file(track: dict) -> Path | None:
    vid = track.get("id") or track.get("url") or ""
    path = await shruti_download(vid, "audio")
    if path:
        return path
    url = track.get("url") or (f"https://www.youtube.com/watch?v={vid}" if vid else "")
    if url:
        return await ytdlp_download_audio(url)
    return None


async def _play_flow(client, message: Message, mode: str = "play"):
    query = _query_from_message(message)
    if not query:
        await _out(
            message,
            f"🎵 <b>Usage</b>\n"
            f"<code>{P}play song name</code>\n"
            f"<code>{P}play https://youtu.be/...</code>\n"
            f"Reply link/text + <code>{P}play</code>\n"
            f"Search: <code>{P}songsearch query</code>\n\n"
            f"API: <code>{'SET' if API_KEY else 'MISSING — set SHRUTI_API_KEY'}</code>",
        )
        return

    status = await _out(message, f"🔍 Searching…\n<code>{query[:80]}</code>")
    track = await resolve_track(query)
    if not track:
        if status:
            try:
                await status.edit_text("❌ Song nahi mili.")
            except Exception:
                pass
        return

    title = track.get("title") or "Track"
    if status:
        try:
            await status.edit_text(
                f"⬇️ Downloading…\n🎵 <b>{title}</b>\n🔗 <code>{track.get('id') or track.get('url')}</code>"
            )
        except Exception:
            pass

    path = await get_audio_file(track)
    if not path:
        if status:
            try:
                await status.edit_text(
                    "❌ Download fail.\n"
                    "• Check <code>SHRUTI_API_KEY</code>\n"
                    "• API URL: <code>SHRUTI_API_URL</code>\n"
                    f"• Current: <code>{API_URL}</code>"
                )
            except Exception:
                pass
        return

    caption = (
        f"🎵 <b>{title}</b>\n"
        f"⏱ {track.get('duration', '?')} | 📡 {mode}\n"
        f"🔗 {track.get('url', '')}"
    )
    try:
        if mode == "vplay":
            # try video download else audio
            vpath = await shruti_download(track.get("id") or track.get("url"), "video")
            if vpath:
                await message.reply_video(str(vpath), caption=caption)
            else:
                await message.reply_audio(str(path), caption=caption, title=title[:64])
        else:
            await message.reply_audio(str(path), caption=caption, title=title[:64])
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
    # channel/chat audio send — same pipeline
    await _play_flow(client, message, mode="cplay")


@app.on_message(filters.command(["songsearch", "ssearch", "ys"], prefixes=P))
async def songsearch_cmd(client, message: Message):
    q = _query_from_message(message)
    if not q:
        await _out(message, f"Usage: <code>{P}songsearch ariana positions</code>")
        return
    status = await _out(message, f"🔎 Searching <code>{q[:60]}</code>…")
    hits = await yt_search(q, limit=8)
    if not hits:
        if status:
            try:
                await status.edit_text("❌ No results")
            except Exception:
                pass
        return
    lines = [f"🔎 <b>Search:</b> {q[:40]}", ""]
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


@app.on_message(filters.command(["musichelp", "mhelp"], prefixes=P))
async def musichelp_cmd(client, message: Message):
    await _out(
        message,
        f"🎵 <b>Music Help</b>\n\n"
        f"<code>{P}play query|url</code> — audio\n"
        f"<code>{P}vplay query|url</code> — video/audio\n"
        f"<code>{P}cplay query|url</code> — chat audio\n"
        f"<code>{P}songsearch query</code> — results\n"
        f"Reply + <code>{P}play</code> bhi chalega\n\n"
        f"API URL: <code>{API_URL}</code>\n"
        f"API KEY: <code>{'✅ set' if API_KEY else '❌ missing'}</code>\n\n"
        f"Env: <code>SHRUTI_API_URL</code> · <code>SHRUTI_API_KEY</code>",
    )
