"""
Access control

- Baaki SAARI commands: sirf userbot ID + OWNER_ID (+ sudo)
- MUSIC commands: ALL group/members use kar sakte (har group me)

Music open list:
  play song vplay cplay songsearch ssearch ys musichelp mhelp
  skip stop pause resume queue joinvc leavevc
"""
from pyrogram import filters
from pyrogram.types import Message
from pyrogram import Client

import config

SUDO_IDS: set[int] = set()

# Commands anyone in any group may use
MUSIC_PUBLIC: set[str] = {
    "play",
    "song",
    "vplay",
    "cplay",
    "songsearch",
    "ssearch",
    "ys",
    "musichelp",
    "mhelp",
    "skip",
    "stop",
    "pause",
    "resume",
    "queue",
    "joinvc",
    "leavevc",
}


async def _only_self_or_owner(flt, client: Client, message: Message) -> bool:
    if getattr(message, "outgoing", False):
        return True

    uid = message.from_user.id if message.from_user else 0
    if not uid:
        return False

    owner = int(getattr(config, "OWNER_ID", 0) or 0)
    if owner and uid == owner:
        return True

    if uid in SUDO_IDS:
        return True

    me = getattr(client, "me", None)
    if me is not None and uid == me.id:
        return True

    try:
        if not me:
            me = await client.get_me()
            if me and uid == me.id:
                return True
    except Exception:
        pass

    return False


ub = filters.create(_only_self_or_owner)


def allow_sudo(user_id: int):
    SUDO_IDS.add(int(user_id))


def revoke_sudo(user_id: int):
    SUDO_IDS.discard(int(user_id))


def _cmd_names(commands) -> set[str]:
    if commands is None:
        return set()
    if isinstance(commands, (list, tuple, set)):
        return {str(c).lower().lstrip(".!/") for c in commands}
    return {str(commands).lower().lstrip(".!/")}


def lock_filters_command():
    """
    Monkeypatch filters.command:
      - music cmds → PUBLIC (no ub lock)
      - everything else → self/owner only
    Call ONCE before load_plugins().
    """
    if getattr(filters, "_kkk_cmd_locked", False):
        return

    _orig = filters.command

    def _locked_command(commands=None, prefixes="/", **kwargs):
        base = _orig(commands, prefixes=prefixes, **kwargs)
        names = _cmd_names(commands)
        if names & MUSIC_PUBLIC:
            return base  # open for all members
        return base & ub

    filters.command = _locked_command  # type: ignore
    filters._kkk_cmd_locked = True  # type: ignore
