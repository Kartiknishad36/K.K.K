# Telegram UserBot

A powerful, modular Telegram UserBot built with **Pyrogram**.

## Features

### Core
- Custom command prefix (default `.`)
- Ping / Alive / Help / ID
- Fully async & modular plugin system

### AFK System
- `.afk [reason]` – Enable AFK
- Auto reply when someone messages/mentions you
- Auto disable when you send any message

### Notes & Filters
- Save/get/delete notes (`.save`, `.get`, `.clear`, `.notes`)
- Quick access with `#notename`
- Keyword filters with auto-reply

### Welcome System
- Custom welcome messages with variables (`{mention}`, `{name}`, `{id}`, `{chat}`)
- Toggle on/off per group

### Auto Delete
- Automatically delete messages after X seconds in groups

### Scheduler
- Schedule messages with relative (`10m`, `2h`, `1d`) or absolute time
- List & delete pending schedules

### Admin Tools
- Ban / Unban / Kick / Mute / Unmute
- Promote / Demote
- Pin / Unpin
- Purge messages
- Global Ban (Gban)

### Tools
- User info / Whois
- Translator (`.tr`)
- Media downloader (`.dl`)
- Invite link generator
- Join / Leave chats
- Account stats

### Message Cloner
- Clone/mirror messages from one chat to another

### PM Permit
- Approve / Disapprove users for private messages

### Broadcast
- Safe broadcast to private chats (with rate limiting)

### Anti-Spam
- Flood detection
- Warning system + auto ban

### AI (Optional)
- OpenAI integration (`.ai`)

---

## Setup

### 1. Clone / Download

```bash
cd telegram-userbot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get API Credentials

1. Go to https://my.telegram.org
2. Login with your phone number
3. Create a new application
4. Copy `API_ID` and `API_HASH`

### 4. Configure

```bash
cp .env.example .env
```

Edit `.env`:

```env
API_ID=12345678
API_HASH=your_api_hash_here
SESSION_NAME=userbot
OWNER_ID=your_telegram_user_id
```

> To get your `OWNER_ID`: Message `@userinfobot` on Telegram.

### 5. Run

```bash
python main.py
```

On first run it will ask for your phone number and login code (OTP). Session will be saved in `data/` folder.

---

## Commands

| Command | Description |
|---------|-------------|
| `.help` | Show help menu |
| `.ping` | Check latency |
| `.afk [reason]` | Set AFK |
| `.save <name> <text>` | Save note |
| `.get <name>` | Get note |
| `#name` | Quick note |
| `.filter <key> <reply>` | Add filter |
| `.setwelcome <msg>` | Set welcome |
| `.autodel <seconds>` | Enable auto-delete |
| `.schedule 10m <msg>` | Schedule message |
| `.ban` / `.kick` / `.mute` | Moderation |
| `.info` | User information |
| `.tr hi <text>` | Translate |
| `.dl` | Download media (reply) |
| `.ai <prompt>` | AI chat (if enabled) |
| `.clone <chat_id>` | Clone messages |
| `.approve` / `.disapprove` | PM Permit |
| `.broadcast <msg>` | Broadcast |
| `.stats` | Account stats |

---

## Important Warnings

1. **Telegram ToS**: Userbots are against Telegram's Terms of Service if used for spam, mass DM, or automation that harms others. Use responsibly.
2. **Ban Risk**: Flooding, mass actions, or joining too many groups quickly can get your account banned/limited.
3. **Session Security**: Never share your session file (`data/*.session`). Anyone with it can control your account.
4. **Owner Only**: Most powerful commands only work from your own account (`filters.me`).

---

## Project Structure

```
telegram-userbot/
├── main.py                 # Entry point
├── config.py               # Configuration
├── requirements.txt
├── .env.example
├── bot/
│   ├── client.py           # Pyrogram client
│   ├── database/
│   │   └── db.py           # SQLite database layer
│   ├── helpers/
│   │   ├── decorators.py
│   │   └── tools.py
│   └── plugins/
│       ├── start.py
│       ├── afk.py
│       ├── notes.py
│       ├── filters.py
│       ├── welcome.py
│       ├── autodelete.py
│       ├── scheduler.py
│       ├── admin.py
│       ├── tools.py
│       ├── antispam.py
│       ├── ai.py
│       ├── clone.py
│       ├── pmpermit.py
│       └── extra.py
├── data/                   # Session + database
└── logs/                   # Log files
```

---

## Adding New Plugins

Create a new file in `bot/plugins/`, for example `bot/plugins/myfeature.py`:

```python
from pyrogram import Client, filters
from pyrogram.types import Message
import config

@Client.on_message(filters.command("hello", prefixes=config.COMMAND_PREFIX) & filters.me)
async def hello(client: Client, message: Message):
    await message.edit_text("Hello World!")
```

It will be auto-loaded on next start.

---

**Made for learning & personal use.**
Use at your own risk.
