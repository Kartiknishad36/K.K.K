"""
Access control — commands ONLY for:
  1) jis ID par userbot laga hai (filters.me / client.me)
  2) config.OWNER_ID (optional master)

Baaki kisi ka command ignore — koi reply nahi (silent).
"""
from pyrogram import filters
from pyrogram.types import Message
from pyrogram import Client

import config

# runtime allow-list (extra sudo ids) — owner can extend later
SUDO_IDS: set[int] = set()


async def _only_self_or_owner(flt, client: Client, message: Message) -> bool:
    # Own outgoing messages = always allow (userbot typing command)
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

    # Secondary / main client: only the account this client is logged in as
    me = getattr(client, "me", None)
    if me is not None and uid == me.id:
        return True

    # Fallback if me not cached yet
    try:
        if not me:
            me = await client.get_me()
            if me and uid == me.id:
                return True
    except Exception:
        pass

    return False


# Use: filters.command("ping", prefixes=".") & ub
ub = filters.create(_only_self_or_owner)


def allow_sudo(user_id: int):
    SUDO_IDS.add(int(user_id))


def revoke_sudo(user_id: int):
    SUDO_IDS.discard(int(user_id))


def lock_filters_command():
    """
    Monkeypatch pyrogram filters.command so EVERY plugin command
    is auto-restricted to self/owner — no need to edit each file.
    Call ONCE before load_plugins().
    """
    if getattr(filters, "_kkk_cmd_locked", False):
        return

    _orig = filters.command

    def _locked_command(*args, **kwargs):
        return _orig(*args, **kwargs) & ub

    filters.command = _locked_command  # type: ignore
    filters._kkk_cmd_locked = True  # type: ignore
