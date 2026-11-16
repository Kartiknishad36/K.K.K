import asyncio
import importlib
from pathlib import Path

from pyrogram import filters
from pyrogram.types import Message

from bot.client import app, logger
from bot.database import db
import config

PLUGINS_DIR = Path(__file__).parent / "bot" / "plugins"


def load_plugins():
    loaded = 0
    failed = []
    for file in sorted(PLUGINS_DIR.glob("*.py")):
        if file.name.startswith("_"):
            continue
        module_name = f"bot.plugins.{file.stem}"
        try:
            importlib.import_module(module_name)
            logger.info(f"Loaded plugin: {file.stem}")
            loaded += 1
        except Exception as e:
            failed.append(file.stem)
            logger.error(f"Failed to load plugin {file.stem}: {type(e).__name__}: {e}")
    logger.info(f"Plugins loaded: {loaded} | failed: {len(failed)}")
    if failed:
        logger.warning(f"Failed plugins: {', '.join(failed)}")
    return loaded


# Built-in so reply ALWAYS works even if some plugins break
@app.on_message(filters.command(["ping", "p"], prefixes=config.COMMAND_PREFIX) & filters.me)
async def builtin_ping(client, message: Message):
    import time
    t = time.time()
    try:
        m = await message.edit_text("🏓 Pinging...")
        ms = round((time.time() - t) * 1000, 2)
        await m.edit_text(f"🏓 **Pong!** `{ms} ms`")
    except Exception:
        try:
            await message.reply_text("🏓 **Pong!**")
        except Exception:
            pass


@app.on_message(filters.command(["alive"], prefixes=config.COMMAND_PREFIX) & filters.me)
async def builtin_alive(client, message: Message):
    me = await client.get_me()
    text = (
        f"**✅ UserBot Alive**\n"
        f"**User:** {me.first_name}\n"
        f"**ID:** `{me.id}`\n"
        f"**Prefix:** `{config.COMMAND_PREFIX}`"
    )
    try:
        await message.edit_text(text)
    except Exception:
        try:
            await message.reply_text(text)
        except Exception:
            pass


async def scheduler_worker():
    while True:
        try:
            pending = await db.get_pending_schedules()
            for schedule in pending:
                try:
                    await app.send_message(
                        chat_id=schedule["chat_id"],
                        text=f"⏰ **Scheduled Message**\n\n{schedule['message']}",
                    )
                    await db.mark_schedule_done(schedule["id"])
                except Exception as e:
                    logger.error(f"Schedule #{schedule['id']}: {e}")
                    await db.mark_schedule_done(schedule["id"])
        except Exception as e:
            logger.error(f"Scheduler: {e}")
        await asyncio.sleep(20)


async def main():
    if not config.API_ID or not config.API_HASH:
        logger.error("API_ID and API_HASH required — https://my.telegram.org")
        return
    if not config.SESSION_STRING and not (config.DATA_DIR / f"{config.SESSION_NAME}.session").exists():
        logger.warning("No SESSION_STRING / session file. Set SESSION_STRING in env.")
    if not config.OWNER_ID:
        logger.warning("OWNER_ID not set.")

    await db.connect()
    logger.info("Database connected.")

    load_plugins()

    await app.start()
    me = await app.get_me()
    logger.info(f"UserBot started as {me.first_name} (@{me.username}) [{me.id}]")

    try:
        total = sum(len(g) for g in app.dispatcher.groups.values())
        logger.info(f"Registered handlers: {total}")
        if total < 3:
            logger.error("TOO FEW HANDLERS — check @app.on_message in plugins")
    except Exception as e:
        logger.warning(f"Handler count failed: {e}")

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

    logger.info("Ready. Prefix=%s | Try .ping from THIS account only", config.COMMAND_PREFIX)
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped.")
