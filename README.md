# K.K.K UserBot

Pyrogram userbot — **fixed handlers**, session string, enums, tagall.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# API_ID API_HASH OWNER_ID SESSION_STRING
python main.py
```

## Session string

```python
from pyrogram import Client
api_id = int(input("API_ID: "))
api_hash = input("API_HASH: ")
with Client("gen", api_id=api_id, api_hash=api_hash, in_memory=True) as app:
    print(app.export_session_string())
```

## Deploy

Railway / Render **Worker**: `python main.py`

## Fixes

- All critical handlers on `@app.on_message` (not class `@Client`)
- `fun.py` imports fixed (`bot.client`)
- Enums for chat type / admin status
- Tagall: full member list + `.tagallstop`
- Profile clone: `.pclone` (no clash with message `.clone`)
- `SESSION_STRING` for cloud deploys

Prefix: `.` — try `.help` `.ping` `.tagall`
