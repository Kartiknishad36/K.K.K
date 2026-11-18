"""
🌐 Translate | 🎮 Games
.tr hi <text> | .truth .dare .riddle .quiz
"""
import random
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX
TRUTHS = ["Sabse embarrassing moment?", "Last lie kab boli?", "Crush ka naam?"]
DARES = ["Funny voice note bhejo", "Random member ko compliment do"]
RIDDLES = [("Hamesha aata hai par kabhi nahi?", "Kal"), ("Bina pair chalta?", "Clock")]
QUIZ = [("Bharat capital?", "delhi"), ("2+2*2?", "6")]

async def _out(m, t):
    try:
        return await m.reply_text(t)
    except Exception:
        try:
            return await m.edit_text(t)
        except Exception:
            return None

@app.on_message(filters.command(["tr", "translate"], prefixes=P))
async def tr_cmd(client, message: Message):
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
        dest = message.command[1] if len(message.command) > 1 else "hi"
    elif len(message.command) >= 3:
        dest = message.command[1]
        text = message.text.split(None, 2)[2]
    else:
        await _out(message, f"Usage: <code>{P}tr hi Hello</code>")
        return
    try:
        from deep_translator import GoogleTranslator
        out = GoogleTranslator(source="auto", target=dest).translate(text)
        await _out(message, f"🌐 <b>{dest}</b>\n{out}")
    except Exception:
        try:
            from googletrans import Translator
            out = Translator().translate(text, dest=dest).text
            await _out(message, f"🌐 <b>{dest}</b>\n{out}")
        except Exception as e:
            await _out(message, f"❌ <code>{e}</code>")

@app.on_message(filters.command(["truth"], prefixes=P))
async def truth_cmd(client, message: Message):
    await _out(message, f"🎯 <b>Truth</b>\n{random.choice(TRUTHS)}")

@app.on_message(filters.command(["dare"], prefixes=P))
async def dare_cmd(client, message: Message):
    await _out(message, f"🔥 <b>Dare</b>\n{random.choice(DARES)}")

@app.on_message(filters.command(["riddle"], prefixes=P))
async def riddle_cmd(client, message: Message):
    q, a = random.choice(RIDDLES)
    await _out(message, f"🧩 <b>Riddle</b>\n{q}\n<code>{a}</code>")

@app.on_message(filters.command(["quiz"], prefixes=P))
async def quiz_cmd(client, message: Message):
    q, a = random.choice(QUIZ)
    await _out(message, f"❓ <b>Quiz</b>\n{q}\n(answer: <code>{a}</code>)")
