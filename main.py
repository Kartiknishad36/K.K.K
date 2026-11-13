import asyncio
import importlib
from pathlib import Path

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
                    logger.info(f"Executed schedule #{schedule['id']}")
                except Exception as e:
                    logger.error(f"Failed schedule #{schedule['id']}: {e}")
                    await db.mark_schedule_done(schedule["id"])
        except Exception as e:
            logger.error(f"Scheduler worker error: {e}")
        await asyncio.sleep(20)


async def main():
    if not config.API_ID or not config.API_HASH:
        logger.error("API_ID and API_HASH required — https://my.telegram.org")
        return
    if not config.SESSION_STRING and not (config.DATA_DIR / f"{config.SESSION_NAME}.session").exists():
        logger.warning(
            "No SESSION_STRING and no session file. "
            "Set SESSION_STRING in env or create session interactively."
        )
    if not config.OWNER_ID:
        logger.warning("OWNER_ID not set.")

    await db.connect()
    logger.info("Database connected.")

    load_plugins()

    await app.start()
    me = await app.get_me()
    logger.info(f"UserBot started as {me.first_name} (@{me.username}) [{me.id}]")

    if config.OWNER_ID and me.id != config.OWNER_ID:
        logger.warning(f"Session user {me.id} != OWNER_ID {config.OWNER_ID}")

    try:
        async for _ in app.get_dialogs():
            pass
        logger.info("Dialogs cached.")
    except Exception as e:
        logger.warning(f"Dialog cache failed: {e}")

    if config.ENABLE_SCHEDULER:
        asyncio.create_task(scheduler_worker())
        logger.info("Scheduler worker started.")

    logger.info("Fully operational. Prefix: %s", config.COMMAND_PREFIX)
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("UserBot stopped by user.")
