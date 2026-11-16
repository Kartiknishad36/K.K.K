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


def patch_dispatcher_sync():
    """
    Pyrogram 2.x dispatcher.add_handler uses loop.create_task(async fn).
    Before app.start() the task often never runs → 0 handlers.
    Patch to synchronous append so decorators + add_handler work immediately.
    """
    dispatcher = app.dispatcher

    def sync_add_handler(handler, group: int = 0):
        if group not in dispatcher.groups:
            dispatcher.groups[group] = []
            dispatcher.groups = OrderedDict(sorted(dispatcher.groups.items()))
        dispatcher.groups[group].append(handler)

    def sync_remove_handler(handler, group: int = 0):
        if group not in dispatcher.groups:
            raise ValueError(f"Group {group} does not exist. Handler was not removed.")
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


async def cmd_ping(client, message: Message):
    t0 = time.time()
    try:
        m = await message.edit_text("🏓 Pinging...")
        ms = round((time.time() - t0) * 1000, 2)
        await m.edit_text(f"🏓 **Pong!** `{ms} ms`")
    except Exception:
        try:
            await message.reply_text("🏓 **Pong!**")
        except Exception as e:
            logger.error(f"ping failed: {e}")


async def cmd_alive(client, message: Message):
    me = await client.get_me()
    text = (
        f"**✅ UserBot Alive**\n"
        f"**User:** {me.first_name}\n"
        f"**ID:** `{me.id}`\n"
        f"**Username:** @{me.username or 'None'}\n"
        f"**Prefix:** `{P}`\n"
        f"**Handlers:** `{count_handlers()}`"
    )
    try:
        await message.edit_text(text)
    except Exception:
        try:
            await message.reply_text(text)
        except Exception as e:
            logger.error(f"alive failed: {e}")


async def cmd_help(client, message: Message):
    text = (
        f"**🤖 UserBot Help**\n"
        f"**Prefix:** `{P}`\n\n"
        f"`{P}ping` — latency\n"
        f"`{P}alive` — status + handler count\n"
        f"`{P}help` — this menu\n"
        f"`{P}id` — chat/user id\n"
        f"`{P}tagall` — tag members\n"
        f"`{P}cat` `{P}rose` — fun arts\n"
        f"`{P}afk` `{P}notes` `{P}filter`\n"
        f"\n_Plugins load with sync dispatcher patch._"
    )
    try:
        await message.edit_text(text)
    except Exception:
        try:
            await message.reply_text(text)
        except Exception as e:
            logger.error(f"help failed: {e}")


def register_core_handlers():
    me_cmd = filters.me
    app.add_handler(MessageHandler(cmd_ping, filters.command(["ping", "p"], prefixes=P) & me_cmd), 0)
    app.add_handler(MessageHandler(cmd_alive, filters.command("alive", prefixes=P) & me_cmd), 0)
    app.add_handler(MessageHandler(cmd_help, filters.command(["help", "start", "menu"], prefixes=P) & me_cmd), 0)
    logger.info("Core handlers registered (ping/alive/help)")


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

    # CRITICAL: patch BEFORE any handler registration / plugin import
    patch_dispatcher_sync()

    await db.connect()
    logger.info("Database connected.")

    load_plugins()
    register_core_handlers()

    n = count_handlers()
    logger.info(f"Handlers registered: {n}")
    if n <= 0:
        logger.error("Still 0 handlers after sync patch — something is very wrong")
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

    logger.info(
        "READY | prefix=%s | account=%s id=%s | type .ping from THIS account",
        P, me.first_name, me.id,
    )
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped.")
