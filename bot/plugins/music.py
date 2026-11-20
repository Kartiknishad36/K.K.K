"""
🎵 Music — public in ALL groups (members can use)
Other bot commands stay owner-only via access.py whitelist.

.env:
  SHRUTI_API_URL=https://api.shrutibots.in
  SHRUTI_API_KEY=your_key

.play / .vplay / .cplay — search|url|reply → download → auto VC join try → chat audio fallback
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
    if urls:
        return urls[0]
    return ""


async def yt_search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
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
                        "url": f"https://www.youtube.com/watch?v={vid}" if vid else "",
                        "channel": item.get("channel") or "",
                    }
                )
            if results:
                return results
        except Exception:
            pass
        try:
            from youtubesearchpython import VideosSearch

            data = VideosSearch(query, limit=limit).result().get("result") or []
            for item in data:
                vid = item.get("id") or ""
                ch = item.get("channel")
                results.append(
                    {
                        "id": vid,
                        "title": item.get("title") or "Unknown",
                        "duration": item.get("duration") or "?",
                        "url": item.get("link") or f"https://www.youtube.com/watch?v={vid}",
                        "channel": ch.get("name", "") if isinstance(ch, dict) else str(ch or ""),
                    }
                )
            if results:
                return results
        except Exception:
            pass
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
        return {
            "id": vid,
            "title": f"YouTube {vid}",
            "url": f"https://www.youtube.com/watch?v={vid}",
            "duration": "?",
            "channel": "",
        }
    if query.startswith("http"):
        return {"id": query, "title": query, "url": query, "duration": "?", "channel": ""}
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
    try:
        timeout = aiohttp.ClientTimeout(total=300)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                f"{API_URL}/download",
                params={"url": vid, "type": media_type, "api_key": API_KEY},
            ) as resp:
                if resp.status != 200:
                    return None
                with open(path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(131072):
                        f.write(chunk)
        if path.exists() and path.stat().st_size > 1024:
            return path
        path.unlink(missing_ok=True)
        return None
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
            f"🎵 <b>Usage</b> (sab members use kar sakte — all groups)\n"
            f"<code>{P}play song name</code>\n"
            f"<code>{P}play https://youtu.be/...</code>\n"
            f"Reply + <code>{P}play</code>\n"
            f"VC: auto-join try on group play\n"
            f"API key: <code>{'SET' if API_KEY else 'MISSING'}</code>",
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
            await status.edit_text(f"⬇️ Downloading…\n🎵 <b>{title}</b>")
        except Exception:
            pass

    path = await get_audio_file(track)
    if not path:
        if status:
            try:
                await status.edit_text(
                    "❌ Download fail — set <code>SHRUTI_API_KEY</code>\n"
                    f"API: <code>{API_URL}</code>"
                )
            except Exception:
                pass
        return

    who = message.from_user.mention if message.from_user else "User"
    caption = (
        f"🎵 <b>{title}</b>\n"
        f"👤 {who}\n"
        f"⏱ {track.get('duration', '?')} | 📡 {mode}\n"
        f"🔗 {track.get('url', '')}"
    )

    vc_note = ""
    chat = message.chat
    is_group = chat and chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)
    if is_group and mode in ("play", "vplay", "cplay"):
        if status:
            try:
                await status.edit_text(f"🎙️ Joining VC…\n🎵 <b>{title}</b>")
            except Exception:
                pass
        ok, info = await vcmod.play_file(client, chat.id, path, title=title)
        vc_note = f"\n🎙️ VC: {'✅ ' + info if ok else '⚠️ ' + info + ' — chat audio bhej diya'}"

    try:
        if mode == "vplay":
            vpath = await shruti_download(track.get("id") or track.get("url"), "video")
            if vpath:
                await message.reply_video(str(vpath), caption=caption + vc_note)
            else:
                await message.reply_audio(str(path), caption=caption + vc_note, title=title[:64])
        else:
            await message.reply_audio(str(path), caption=caption + vc_note, title=title[:64])
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
    msg = await vcmod.stop(message.chat.id)
    await _out(message, f"⏹ {msg}")


@app.on_message(filters.command(["skip"], prefixes=P))
async def skip_cmd(client, message: Message):
    msg = await vcmod.skip(message.chat.id)
    await _out(message, f"⏭ {msg}")


@app.on_message(filters.command(["joinvc"], prefixes=P))
async def joinvc_cmd(client, message: Message):
    ok, info = await vcmod.ensure_group_call(client, message.chat.id)
    await _out(message, f"{'✅' if ok else '❌'} {info}")


@app.on_message(filters.command(["leavevc"], prefixes=P))
async def leavevc_cmd(client, message: Message):
    msg = await vcmod.stop(message.chat.id)
    await _out(message, f"🚪 {msg}")


@app.on_message(filters.command(["musichelp", "mhelp"], prefixes=P))
async def musichelp_cmd(client, message: Message):
    await _out(
        message,
        f"🎵 <b>Music</b> — <u>sab members, all groups</u>\n"
        f"Baaki commands sirf Owner.\n\n"
        f"<code>{P}play</code> <code>{P}vplay</code> <code>{P}cplay</code>\n"
        f"<code>{P}songsearch</code> <code>{P}stop</code> <code>{P}skip</code>\n"
        f"<code>{P}joinvc</code> <code>{P}leavevc</code>\n\n"
        f"🎙️ Group me play = auto VC join try\n"
        f"API: <code>{'✅' if API_KEY else '❌ set SHRUTI_API_KEY'}</code>",
    )
