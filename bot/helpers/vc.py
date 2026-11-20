"""Voice Chat helper — fixed random_id OverflowError."""
from __future__ import annotations

import logging
import random
from pathlib import Path
from typing import Any

log = logging.getLogger("vc")

ACTIVE: dict[int, Any] = {}
QUEUES: dict[int, list[dict]] = {}
_CLIENT_CALLS: dict[int, Any] = {}


def _rnd() -> int:
    # pyrogram rnd_id() sometimes OverflowError on CreateGroupCall
    return random.randint(1, 2**31 - 1)


async def ensure_group_call(client, chat_id: int) -> tuple[bool, str]:
    try:
        from pyrogram.raw import functions

        peer = await client.resolve_peer(chat_id)
        try:
            await client.invoke(
                functions.phone.CreateGroupCall(
                    peer=peer,
                    random_id=_rnd(),
                    title="🎵 Music",
                )
            )
            return True, "VC created"
        except Exception as e:
            err = f"{type(e).__name__}: {e}".lower()
            if "group_call_already" in err or "already" in err:
                return True, "VC already open"
            if "overflow" in err:
                return False, "VC random_id overflow (fixed in new build — redeploy)"
            # still try stream later
            return True, f"VC exists/try ({type(e).__name__})"
    except Exception as e:
        return False, f"VC fail: {type(e).__name__}: {e}"


async def _get_pytgcalls(client):
    cid = id(client)
    if cid in _CLIENT_CALLS:
        return _CLIENT_CALLS[cid]
    from pytgcalls import PyTgCalls

    call = PyTgCalls(client)
    await call.start()
    _CLIENT_CALLS[cid] = call
    return call


async def play_file(client, chat_id: int, file_path: str | Path, title: str = "") -> tuple[bool, str]:
    path = Path(file_path)
    if not path.exists() or path.stat().st_size < 1000:
        return False, "audio file missing"

    ok, msg = await ensure_group_call(client, chat_id)
    if not ok:
        log.warning("ensure_group_call: %s", msg)

    try:
        from pytgcalls.types import MediaStream

        call = await _get_pytgcalls(client)
        try:
            await call.leave_call(chat_id)
        except Exception:
            pass
        try:
            await call.play(
                chat_id,
                MediaStream(str(path), video_flags=MediaStream.Flags.IGNORE),
            )
        except TypeError:
            await call.play(chat_id, MediaStream(str(path)))
        ACTIVE[chat_id] = call
        return True, f"VC playing — {title or path.name}"
    except Exception as e:
        log.warning("pytgcalls: %s", e)

    try:
        from pytgcalls import GroupCallFactory

        if chat_id in ACTIVE:
            try:
                old = ACTIVE[chat_id]
                if hasattr(old, "stop"):
                    await old.stop()
            except Exception:
                pass
        gc = GroupCallFactory(client).get_file_group_call(str(path))
        await gc.start(chat_id)
        ACTIVE[chat_id] = gc
        return True, f"VC legacy — {title or path.name}"
    except Exception as e:
        return False, f"VC stream fail ({type(e).__name__}) — audio chat me"


async def stop(chat_id: int) -> str:
    call = ACTIVE.pop(chat_id, None)
    QUEUES.pop(chat_id, None)
    if not call:
        return "Kuch play nahi"
    try:
        if hasattr(call, "leave_call"):
            await call.leave_call(chat_id)
        elif hasattr(call, "stop"):
            await call.stop()
    except Exception as e:
        return f"Stop: {e}"
    return "VC stopped"


async def skip(chat_id: int) -> str:
    q = QUEUES.get(chat_id) or []
    if not q:
        await stop(chat_id)
        return "Queue empty"
    q.pop(0)
    return f"Skip — left {len(q)}"
