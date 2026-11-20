"""
Voice Chat helper — auto join + play local file (pytgcalls if installed).

Fallback: returns False so music.py can send audio in chat.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

log = logging.getLogger("vc")

# chat_id -> call object / flag
ACTIVE: dict[int, Any] = {}
QUEUES: dict[int, list[dict]] = {}


async def ensure_group_call(client, chat_id: int) -> tuple[bool, str]:
    """Try start/join VC in group."""
    try:
        from pyrogram.raw import functions

        peer = await client.resolve_peer(chat_id)
        try:
            await client.invoke(
                functions.phone.CreateGroupCall(
                    peer=peer,
                    random_id=client.rnd_id(),
                    title="Music",
                )
            )
            return True, "VC created"
        except Exception as e:
            # already exists or no permission
            return True, f"VC ready ({type(e).__name__})"
    except Exception as e:
        return False, f"VC join/create fail: {e}"


async def play_file(client, chat_id: int, file_path: str | Path, title: str = "") -> tuple[bool, str]:
    """
    Auto-join group VC and stream audio file if pytgcalls available.
    """
    path = Path(file_path)
    if not path.exists():
        return False, "file missing"

    ok, msg = await ensure_group_call(client, chat_id)
    if not ok:
        log.warning(msg)

    # py-tgcalls 2.x style (best-effort)
    try:
        from pytgcalls import PyTgCalls
        from pytgcalls.types import MediaStream

        if not hasattr(client, "_pytgcalls"):
            call = PyTgCalls(client)
            await call.start()
            client._pytgcalls = call
        else:
            call = client._pytgcalls

        await call.play(chat_id, MediaStream(str(path)))
        ACTIVE[chat_id] = call
        return True, f"VC playing: {title or path.name}"
    except Exception as e1:
        log.info("pytgcalls MediaStream fail: %s", e1)

    # older GroupCallFactory style
    try:
        from pytgcalls import GroupCallFactory

        if chat_id in ACTIVE and hasattr(ACTIVE[chat_id], "stop"):
            try:
                await ACTIVE[chat_id].stop()
            except Exception:
                pass

        gc = GroupCallFactory(client).get_file_group_call(str(path))
        await gc.start(chat_id)
        ACTIVE[chat_id] = gc
        return True, f"VC (legacy) playing: {title or path.name}"
    except Exception as e2:
        return False, f"VC stream unavailable ({type(e2).__name__}: {e2})"


async def stop(chat_id: int) -> str:
    call = ACTIVE.pop(chat_id, None)
    QUEUES.pop(chat_id, None)
    if not call:
        return "Nothing playing"
    try:
        if hasattr(call, "leave_call"):
            await call.leave_call(chat_id)
        elif hasattr(call, "stop"):
            await call.stop()
    except Exception as e:
        return f"Stopped (err: {e})"
    return "Stopped"


async def skip(chat_id: int) -> str:
    q = QUEUES.get(chat_id) or []
    if not q:
        await stop(chat_id)
        return "Queue empty — stopped"
    q.pop(0)
    return f"Skipped — left {len(q)}"
