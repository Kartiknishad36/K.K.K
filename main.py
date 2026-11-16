import asyncio
import importlib
import time
from collections import OrderedDict
from pathlib import Path

from pyrogram import filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from bot.client import app, logger
from bot.database import db
import config

PLUGINS_DIR = Path(__file__).parent / "bot" / "plugins"
P = config.COMMAND_PREFIX or "."

# Own messages: outgoing is more reliable for userbots across multi-session
OWN = filters.outgoing | filters.me


def patch_dispatcher_sync():
    """Pyrogram 2.x add_handler is async create_task — patch to sync before start."""
    dispatcher = app.dispatcher

    def sync_add_handler(handler, group: int = 0):
        if group not in dispatcher.groups:
            dispatcher.groups[group] = []
            dispatcher.groups = OrderedDict(sorted(dispatcher.groups.items()))
        dispatcher.groups[group].append(handler)

    def sync_remove_handler(handler, group: int = 0):
        if group not in dispatcher.groups:
            raise ValueError(f"Group {group} does not exist.")
        dispatcher.groups[group].remove(handler)

    dispatcher.add_handler = sync_add_handler
    dispatcher.remove_handler = sync_remove_handler
    logger.info("Dispatcher patched: sync add_handler (Pyrogram 2.x fix)")


def load_plugins():
    loaded, failed = 0, []
    for file in sorted(PLUGINS_DIR.glob("*.py")):
        if file.name.startswith("_"):
            continue
        name = f"bot.plugins.{file.stem}"
        try:
            importlib.import_module(name)
            logger.info(f"Loaded plugin: {file.stem}")
            loaded += 1
        except Exception as e:
            failed.append(file.stem)
            logger.error(f"Failed plugin {file.stem}: {type(e).__name__}: {e}")
    logger.info(f"Plugins loaded: {loaded} | failed: {len(failed)}")
    if failed:
        logger.warning(f"Failed plugins: {', '.join(failed)}")
    return loaded


def count_handlers() -> int:
    try:
        groups = getattr(app.dispatcher, "groups", {}) or {}
        total = 0
        for g in groups.values():
            try:
                total += len(g)
            except TypeError:
                total += 1
        return total
    except Exception as e:
        logger.warning(f"count error: {e}")
        return -1


async def safe_reply(message: Message, text: str):
    """Prefer reply; fall back to edit. Never silent-fail."""
    try:
        return await message.reply_text(text)
    except Exception as e1:
        try:
            return await message.edit_text(text)
        except Exception as e2:
            logger.error(f"safe_reply failed: reply={e1} edit={e2}")
            return None


async def cmd_ping(client, message: Message):
    logger.info(f"PING handler fired chat={message.chat.id} text={message.text!r}")
    t0 = time.time()
    ms = round((time.time() - t0) * 1000, 2)
    await safe_reply(message, f"🏓 **Pong!** `{ms} ms`\nHandlers: `{count_handlers()}`")


async def cmd_alive(client, message: Message):
    logger.info("ALIVE handler fired")
    me = await client.get_me()
    text = (
        f"**✅ UserBot Alive**\n"
        f"**User:** {me.first_name}\n"
        f"**ID:** `{me.id}`\n"
        f"**Username:** @{me.username or 'None'}\n"
        f"**Prefix:** `{P}`\n"
        f"**Handlers:** `{count_handlers()}`"
    )
    await safe_reply(message, text)


async def cmd_help(client, message: Message):
    logger.info("HELP handler fired")
    text = (
        f"**🤖 UserBot Help**\n"
        f"**Prefix:** `{P}`\n\n"
        f"`{P}ping` — latency\n"
        f"`{P}alive` — status\n"
        f"`{P}help` — this menu\n"
        f"`{P}id` — chat/user id\n"
        f"`{P}tagall` — tag members\n"
        f"`{P}cat` `{P}rose` — fun\n"
        f"`{P}afk` `{P}notes` `{P}filter`\n"
    )
    await safe_reply(message, text)


async def debug_outgoing(client, message: Message):
    """Log every own text message so we can see if updates arrive."""
    text = message.text or message.caption or ""
    if text:
        logger.info(
            f"OUTGOING msg chat={getattr(message.chat, 'id', None)} "
            f"out={message.outgoing} text={text[:80]!r}"
        )


def register_core_handlers():
    # group=-1 so core runs with high priority
    app.add_handler(
        MessageHandler(cmd_ping, filters.command(["ping", "p"], prefixes=P) & OWN),
        group=-1,
    )
    app.add_handler(
        MessageHandler(cmd_alive, filters.command("alive", prefixes=P) & OWN),
        group=-1,
    )
    app.add_handler(
        MessageHandler(cmd_help, filters.command(["help", "start", "menu"], prefixes=P) & OWN),
        group=-1,
    )
    # Debug: see if ANY outgoing text reaches the client
    app.add_handler(
        MessageHandler(debug_outgoing, filters.outgoing & filters.text),
        group=99,
    )
    logger.info("Core handlers registered (ping/alive/help + debug outgoing)")


async def scheduler_worker():
    while True:
        try:
            pending = await db.get_pending_schedules()
            for schedule in pending:
                try:
                    await app.send_message(
                        chat_id=schedule["chat_id"],
                        text=f"⏰ **Scheduled**\n\n{schedule['message']}",
                    )
                    await db.mark_schedule_done(schedule["id"])
                except Exception as e:
                    logger.error(f"schedule: {e}")
                    await db.mark_schedule_done(schedule["id"])
        except Exception as e:
            logger.error(f"scheduler: {e}")
        await asyncio.sleep(20)


async def main():
    if not config.API_ID or not config.API_HASH:
        logger.error("API_ID and API_HASH required")
        return

    if not config.SESSION_STRING and not (config.DATA_DIR / f"{config.SESSION_NAME}.session").exists():
        logger.warning("No SESSION_STRING — set it in env")

    patch_dispatcher_sync()

    await db.connect()
    logger.info("Database connected.")

    load_plugins()
    register_core_handlers()

    n = count_handlers()
    logger.info(f"Handlers registered: {n}")
    if n <= 0:
        logger.error("Still 0 handlers after sync patch")
    else:
        logger.info(f"OK — {n} handlers ready BEFORE start")

    await app.start()
    me = await app.get_me()
    logger.info(f"UserBot started as {me.first_name} (@{me.username}) [{me.id}]")
    logger.info(f"Handlers after start: {count_handlers()}")

    if config.OWNER_ID and me.id != config.OWNER_ID:
        logger.warning(f"Session {me.id} != OWNER_ID {config.OWNER_ID}")

    try:
        async for _ in app.get_dialogs():
            pass
        logger.info("Dialogs cached.")
    except Exception as e:
        logger.warning(f"Dialog cache: {e}")

    if config.ENABLE_SCHEDULER:
        asyncio.create_task(scheduler_worker())
        logger.info("Scheduler started.")

    # Prove live session can send
    try:
        await app.send_message("me", f"✅ UserBot online\nID: `{me.id}`\nHandlers: `{count_handlers()}`\nTry `.ping` here or any chat.")
        logger.info("Startup message sent to Saved Messages")
    except Exception as e:
        logger.error(f"Could not send to Saved Messages: {e}")

    logger.info(
        "READY | prefix=%s | account=%s id=%s | send .ping from Kamyar account",
        P, me.first_name, me.id,
    )
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped.")
