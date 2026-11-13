import logging
from pathlib import Path

from pyrogram import Client
import config

Path(config.DATA_DIR).mkdir(parents=True, exist_ok=True)
Path(config.LOGS_DIR).mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("UserBot")

_kwargs = dict(
    name=config.SESSION_NAME or "mybot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    workdir=str(config.DATA_DIR),
    in_memory=False,
)

if config.SESSION_STRING and config.SESSION_STRING.strip():
    _kwargs["session_string"] = config.SESSION_STRING.strip()
    _kwargs["in_memory"] = True

app = Client(**_kwargs)
