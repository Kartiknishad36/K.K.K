""".sha / shayari — original lines, one-shot or recurring"""
import asyncio, random
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import config

MIN_MIN = 10
TAG_BATCH = 5
_SHA_O = ["दिल की बात लफ़्ज़ों में कहाँ समाती है","वक़्त बदलता है, हालात बदलते हैं","मंज़िल से ज़्यादा सफ़र का मज़ा है","उम्मीद का दीया कभी बुझने मत देना","अपनों की हँसी में ही असली सुकून है","ज़िंदगी एक किताब है, हर दिन नया पन्ना है","मुश्किलें आती हैं सिखाने के लिए","हर सुबह एक नई शुरुआत लेकर आती है","सपने वही सच होते हैं जो दिल से देखे जाते हैं","रिश्तों की मिठास वक़्त के साथ और बढ़ती है"]
_SHA_C = ["हर खामोशी भी कुछ कह जाती है।","पर अपनों का साथ नहीं बदलता।","हर मोड़ पर एक नई सीख छुपी है।","अंधेरा चाहे कितना भी घना हो।","बाकी सब तो बस दिखावा है।","बस पढ़ने वाला समझदार होना चाहिए।","रुकने के लिए नहीं।","बस उसे पहचानने वाला चाहिए।","और मेहनत से पूरे होते हैं।","बस निभाने वाला सच्चा होना चाहिए।"]
SHAYARI = [f"{o},\n{c}" for o in _SHA_O for c in _SHA_C]
SHA_TASKS = {}

async def _members(client, chat_id):
    out = []
    try:
        async for m in client.get_chat_members(chat_id):
            if m.user and not m.user.is_bot and not m.user.is_deleted: out.append(m.user)
    except Exception: pass
    return out

async def _handle(client, message, lines, tasks, label, cmd):
    chat_id = message.chat.id
    if message.chat.type.name not in ["GROUP", "SUPERGROUP"]:
        await message.edit_text("Sirf groups me."); return
    if len(message.command) > 1 and message.command[1].lower() == "stop":
        t = tasks.pop(chat_id, None)
        if t: t.cancel(); await message.edit_text(f"🛑 {label} stopped.")
        else: await message.edit_text("Koi recurring nahi chal raha.")
        return
    if len(message.command) > 1:
        try: minutes = max(int(message.command[1]), MIN_MIN)
        except ValueError: minutes = None
        if minutes is not None:
            if chat_id in tasks:
                await message.edit_text(f"Already running. `{config.COMMAND_PREFIX}{cmd} stop`"); return
            async def loop():
                try:
                    while True:
                        line = random.choice(lines)
                        mems = await _members(client, chat_id)
                        text = f"{line}\n\n{' '.join(u.mention for u in random.sample(mems, min(TAG_BATCH, len(mems))))}" if mems else line
                        try: await client.send_message(chat_id, text)
                        except FloodWait as e: await asyncio.sleep(e.value)
                        except Exception: pass
                        await asyncio.sleep(minutes * 60)
                except asyncio.CancelledError: pass
            tasks[chat_id] = asyncio.create_task(loop())
            await message.edit_text(f"📜 Recurring {label} every **{minutes}** min."); return
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        await message.edit_text(f"{random.choice(lines)}\n\n{u.mention}"); return
    await message.edit_text("📜 Sending…")
    mems = await _members(client, chat_id)
    line = random.choice(lines)
    if not mems:
        await client.send_message(chat_id, line); return
    for i in range(0, len(mems), TAG_BATCH):
        batch = mems[i:i+TAG_BATCH]
        try: await client.send_message(chat_id, f"{line}\n\n{' '.join(u.mention for u in batch)}")
        except Exception: pass
        await asyncio.sleep(1.5)

@Client.on_message(filters.command(["sha", "shayari"], prefixes=config.COMMAND_PREFIX) & filters.me)
async def sha_cmd(client: Client, message: Message):
    await _handle(client, message, SHAYARI, SHA_TASKS, "shayari", "sha")
