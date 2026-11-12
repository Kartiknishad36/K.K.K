import asyncio
import logging
import importlib
from pathlib import Path
from datetime import datetime

from bot.client import app, logger
from bot.database import db
import config

# Load all plugins
PLUGINS_DIR = Path(__file__).parent / "bot" / "plugins"

def load_plugins():
    for file in PLUGINS_DIR.glob("*.py"):
        if file.name.startswith("_"):
            continue
        module_name = f"bot.plugins.{file.stem}"
        try:
            importlib.import_module(module_name)
            logger.info(f"Loaded plugin: {file.stem}")
        except Exception as e:
            logger.error(f"Failed to load plugin {file.stem}: {e}")

async def scheduler_worker():
    """Background task to execute scheduled messages."""
    while True:
        try:
            pending = await db.get_pending_schedules()
            for schedule in pending:
                try:
                    await app.send_message(
                        chat_id=schedule["chat_id"],
                        text=f"⏰ **Scheduled Message**\n\n{schedule['message']}"
                    )
                    await db.mark_schedule_done(schedule["id"])
                    logger.info(f"Executed schedule #{schedule['id']}")
                except Exception as e:
                    logger.error(f"Failed to execute schedule #{schedule['id']}: {e}")
                    await db.mark_schedule_done(schedule["id"])  # Mark done to avoid loop
        except Exception as e:
            logger.error(f"Scheduler worker error: {e}")

        await asyncio.sleep(20)  # Check every 20 seconds

async def main():
    # Validate config
    if not config.API_ID or not config.API_HASH:
        logger.error("API_ID and API_HASH are required. Get them from https://my.telegram.org")
        return
    if not config.OWNER_ID:
        logger.warning("OWNER_ID not set. Some features may not work correctly.")

    # Connect database
    await db.connect()
    logger.info("Database connected.")

    # Load plugins
    load_plugins()

    # Start client
    await app.start()
    me = await app.get_me()
    logger.info(f"UserBot started as {me.first_name} (@{me.username}) [{me.id}]")

    # Cache all dialogs to fix Peer id invalid errors
    try:
        async for _ in app.get_dialogs():
            pass
        logger.info("Dialogs cached.")
    except Exception as e:
        logger.warning(f"Dialog cache failed: {e}")

    # Start background scheduler
    if config.ENABLE_SCHEDULER:
        asyncio.create_task(scheduler_worker())
        logger.info("Scheduler worker started.")

    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("UserBot stopped by user.")
    finally:
        # Cleanup
        async def cleanup():
            await db.close()
            await app.stop()
        try:
            asyncio.run(cleanup())
        except Exception:
            pass
