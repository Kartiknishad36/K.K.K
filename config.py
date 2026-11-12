import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if not exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Telegram credentials
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
SESSION_NAME = os.getenv("SESSION_NAME", "userbot")

# Owner
OWNER_ID = int(os.getenv("OWNER_ID", 0))

# OpenAI (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "userbot.db"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(LOGS_DIR / "userbot.log"))

# Feature toggles
ENABLE_AFK = os.getenv("ENABLE_AFK", "true").lower() == "true"
ENABLE_WELCOME = os.getenv("ENABLE_WELCOME", "true").lower() == "true"
ENABLE_AUTODELETE = os.getenv("ENABLE_AUTODELETE", "true").lower() == "true"
ENABLE_SCHEDULER = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"
ENABLE_ANTISPAM = os.getenv("ENABLE_ANTISPAM", "true").lower() == "true"
ENABLE_AI = os.getenv("ENABLE_AI", "false").lower() == "true"
ENABLE_TRANSLATOR = os.getenv("ENABLE_TRANSLATOR", "true").lower() == "true"

# Prefix for commands (can be changed)
COMMAND_PREFIX = "."

# AFK defaults
AFK_DEFAULT_REASON = "I am currently AFK. Will reply soon."

# Anti-spam settings
ANTISPAM_MAX_MESSAGES = 7          # messages
ANTISPAM_TIME_WINDOW = 10          # seconds
ANTISPAM_WARN_LIMIT = 3

# Auto-delete default time (seconds)
AUTODELETE_DEFAULT = 3600  # 1 hour

# Welcome message default
WELCOME_DEFAULT = "👋 Welcome {mention} to **{chat}**!"

# Scheduler timezone
TIMEZONE = "Asia/Kolkata"
