from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
P = config.COMMAND_PREFIX
AR_PHOTO = False
PHOTO_FILE_ID = None
async def _out(m, t):
    try: return await m.reply_text(t)
    except Exception:
        try: return await m.edit_text(t)
        except Exception: return None
@app.on_message(filters.command(["arphoto"], prefixes=P))
async def arphoto_cmd(client, message: Message):
    global AR_PHOTO, PHOTO_FILE_ID
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    r = message.reply_to_message
    if r and r.photo:
        PHOTO_FILE_ID = r.photo.file_id; AR_PHOTO = True
        await _out(message, "🖼 Photo set + ON"); return
    if arg in ("on", "1"): AR_PHOTO = True
    elif arg in ("off", "0"): AR_PHOTO = False
    else: AR_PHOTO = not AR_PHOTO
    await _out(message, f"🖼 AR Photo: {'ON' if AR_PHOTO else 'OFF'}")
@app.on_message(filters.private & filters.incoming & ~filters.me & filters.text, group=59)
async def arphoto_watch(client, message: Message):
    if not AR_PHOTO or not PHOTO_FILE_ID: return
    if (message.text or "").lower() in ("hi", "hello", "hii", "hey"):
        try: await message.reply_photo(PHOTO_FILE_ID, caption="👋")
        except Exception: pass
