import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

API_ID = int(os.getenv("API_ID", "0") or 0)
API_HASH = os.getenv("API_HASH", "") or ""
SESSION_NAME = os.getenv("SESSION_NAME", "mybot") or "mybot"
SESSION_STRING = os.getenv("SESSION_STRING", "") or ""

OWNER_ID = int(os.getenv("OWNER_ID", "0") or 0)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "") or ""

DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "userbot.db"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(LOGS_DIR / "userbot.log"))

ENABLE_AFK = os.getenv("ENABLE_AFK", "true").lower() == "true"
ENABLE_WELCOME = os.getenv("ENABLE_WELCOME", "true").lower() == "true"
ENABLE_AUTODELETE = os.getenv("ENABLE_AUTODELETE", "true").lower() == "true"
ENABLE_SCHEDULER = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"
ENABLE_ANTISPAM = os.getenv("ENABLE_ANTISPAM", "true").lower() == "true"
ENABLE_AI = os.getenv("ENABLE_AI", "false").lower() == "true"
ENABLE_TRANSLATOR = os.getenv("ENABLE_TRANSLATOR", "true").lower() == "true"

COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", ".") or "."

AFK_DEFAULT_REASON = "I am currently AFK. Will reply soon."

ANTISPAM_MAX_MESSAGES = 7
ANTISPAM_TIME_WINDOW = 10
ANTISPAM_WARN_LIMIT = 3

AUTODELETE_DEFAULT = 3600

WELCOME_DEFAULT = "👋 Welcome {mention} to **{chat}**!"

TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
