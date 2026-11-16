import asyncio
import importlib
import time
from collections import OrderedDict
from pathlib import Path

from pyrogram import filters, idle
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from bot.client import app, logger
from bot.database import db
import config

PLUGINS_DIR = Path(__file__).parent / "bot" / "plugins"
P = (config.COMMAND_PREFIX or ".").strip() or "."


def patch_dispatcher_sync():
    """Pyrogram 2.x: add_handler uses create_task — fails before loop is running."""
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
    logger.info("Dispatcher patched: sync add_handler")


def load_plugins():
    loaded, failed = 0, []
    for file in sorted(PLUGINS_DIR.glob("*.py")):
        if file.name.startswith("_"):
            continue
        try:
            importlib.import_module(f"bot.plugins.{file.stem}")
            logger.info(f"Loaded plugin: {file.stem}")
            loaded += 1
        except Exception as e:
            failed.append(file.stem)
            logger.error(f"Failed plugin {file.stem}: {type(e).__name__}: {e}")
    logger.info(f"Plugins loaded: {loaded} | failed: {len(failed)}")
    if failed:
        logger.warning(f"Failed: {', '.join(failed)}")
    return loaded


def count_handlers() -> int:
    try:
        groups = getattr(app.dispatcher, "groups", {}) or {}
        return sum(len(g) if hasattr(g, "__len__") else 1 for g in groups.values())
    except Exception:
        return -1


async def safe_reply(message: Message, text: str):
    try:
        return await message.reply_text(text)
    except Exception as e1:
        try:
            return await message.edit_text(text)
        except Exception as e2:
            logger.error(f"reply/edit failed: {e1} | {e2}")
            try:
                return await app.send_message(message.chat.id, text)
            except Exception as e3:
                logger.error(f"send_message also failed: {e3}")
                return None


async def cmd_ping(client, message: Message):
    logger.info(f"PING fired | chat={message.chat.id} out={message.outgoing} text={message.text!r}")
    t0 = time.time()
    await asyncio.sleep(0.01)
    ms = round((time.time() - t0) * 1000, 2)
    await safe_reply(message, f"🏓 **Pong!** `{ms} ms`\nHandlers: `{count_handlers()}`")


async def cmd_alive(client, message: Message):
    logger.info("ALIVE fired")
    me = await client.get_me()
    await safe_reply(
        message,
        f"**✅ UserBot Alive**\n"
        f"**User:** {me.first_name}\n"
        f"**ID:** `{me.id}`\n"
        f"**Prefix:** `{P}`\n"
        f"**Handlers:** `{count_handlers()}`",
    )


async def cmd_help(client, message: Message):
    logger.info("HELP fired")
    await safe_reply(
        message,
        f"**🤖 UserBot Help**\n"
        f"**Prefix:** `{P}`\n\n"
        f"`{P}ping` — latency\n"
        f"`{P}alive` — status\n"
        f"`{P}help` — this menu\n"
        f"`{P}id` — ids\n"
        f"`{P}tagall` — tag all\n"
        f"`{P}cat` `{P}rose` — arts\n",
    )


async def cmd_id(client, message: Message):
    logger.info("ID fired")
    chat = message.chat
    user = message.from_user
    reply = message.reply_to_message
    lines = [
        f"**Chat:** `{chat.id}` ({chat.type})",
        f"**Title:** {getattr(chat, 'title', None) or getattr(chat, 'first_name', '')}",
    ]
    if user:
        lines.append(f"**From:** `{user.id}` {user.mention}")
    if reply and reply.from_user:
        lines.append(f"**Reply user:** `{reply.from_user.id}` {reply.from_user.mention}")
    await safe_reply(message, "\n".join(lines))


async def on_any_message(client, message: Message):
    text = message.text or message.caption
    if not text:
        return
    logger.info(
        f"MSG chat={message.chat.id} out={message.outgoing} "
        f"from={getattr(message.from_user, 'id', None)} text={text[:60]!r}"
    )


def register_core():
    # Open filters: respond to .ping from anyone (proves pipeline works)
    app.add_handler(
        MessageHandler(cmd_ping, filters.command(["ping", "p"], prefixes=[P, "!", "/"])),
        group=-2,
    )
    app.add_handler(
        MessageHandler(cmd_alive, filters.command(["alive"], prefixes=[P, "!", "/"])),
        group=-2,
    )
    app.add_handler(
        MessageHandler(cmd_help, filters.command(["help", "menu"], prefixes=[P, "!", "/"])),
        group=-2,
    )
    app.add_handler(
        MessageHandler(cmd_id, filters.command(["id"], prefixes=[P, "!", "/"])),
        group=-2,
    )
    app.add_handler(MessageHandler(on_any_message, filters.text), group=99)
    logger.info("Core handlers registered (open ping/alive/help/id + msg logger)")


async def scheduler_worker():
    while True:
        try:
            pending = await db.get_pending_schedules()
            for schedule in pending:
                try:
                    await app.send_message(
                        schedule["chat_id"],
                        f"⏰ **Scheduled**\n\n{schedule['message']}",
                    )
                    await db.mark_schedule_done(schedule["id"])
                except Exception as e:
                    logger.error(f"schedule: {e}")
                    try:
                        await db.mark_schedule_done(schedule["id"])
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"scheduler: {e}")
        await asyncio.sleep(20)


async def main():
    if not config.API_ID or not config.API_HASH:
        logger.error("API_ID / API_HASH missing")
        return

    patch_dispatcher_sync()

    await db.connect()
    logger.info("Database connected")

    load_plugins()
    register_core()

    n = count_handlers()
    logger.info(f"Handlers before start: {n}")
    if n <= 0:
        logger.error("No handlers registered!")

    await app.start()
    me = await app.get_me()
    logger.info(f"Started as {me.first_name} (@{me.username}) [{me.id}]")
    logger.info(f"Handlers after start: {count_handlers()}")

    register_core()
    logger.info(f"Handlers after re-bind: {count_handlers()}")

    try:
        async for _ in app.get_dialogs():
            pass
        logger.info("Dialogs cached")
    except Exception as e:
        logger.warning(f"Dialog cache: {e}")

    if config.ENABLE_SCHEDULER:
        asyncio.create_task(scheduler_worker())

    try:
        msg = await app.send_message(
            "me",
            f"✅ **UserBot ONLINE**\n"
            f"Account: **{me.first_name}**\n"
            f"ID: `{me.id}`\n"
            f"Handlers: `{count_handlers()}`\n\n"
            f"Yahan type karo: `{P}ping`",
        )
        logger.info(f"Saved Messages notify OK id={msg.id}")
    except Exception as e:
        logger.error(f"Saved Messages send FAILED: {e}")

    logger.info(f"READY | prefix={P} | id={me.id} | try {P}ping in Saved Messages")
    await idle()
    await app.stop()


if __name__ == "__main__":
    app.run(main())
