"""
🎮 Games only
(.tr / translate already in tools.py — not duplicated)

.truth  .dare  .riddle  .quiz
"""
import random
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config

P = config.COMMAND_PREFIX

TRUTHS = [
    "Sabse embarrassing moment kya tha?",
    "Last lie kab boli?",
    "Crush ka naam bata?",
    "Sabse weird food try kiya?",
]
DARES = [
    "Group me funny voice note bhejo",
    "Ek random member ko compliment do",
    "Apna last emoji status pe daalo",
]
RIDDLES = [
    ("Hamesha aata hai par kabhi nahi aata?", "Kal / tomorrow"),
    ("Bina pair ke chalta hai?", "Clock / time"),
]
QUIZ = [
    ("Bharat ki capital?", "delhi"),
    ("2+2*2?", "6"),
]


async def _out(m, t):
    try:
        return await m.reply_text(t)
    except Exception:
        try:
            return await m.edit_text(t)
        except Exception:
            return None


@app.on_message(filters.command(["truth"], prefixes=P))
async def truth_cmd(client, message: Message):
    await _out(message, f"🎯 <b>Truth</b>\n{random.choice(TRUTHS)}")


@app.on_message(filters.command(["dare"], prefixes=P))
async def dare_cmd(client, message: Message):
    await _out(message, f"🔥 <b>Dare</b>\n{random.choice(DARES)}")


@app.on_message(filters.command(["riddle"], prefixes=P))
async def riddle_cmd(client, message: Message):
    q, a = random.choice(RIDDLES)
    await _out(message, f"🧩 <b>Riddle</b>\n{q}\n\n<code>Answer: {a}</code>")


@app.on_message(filters.command(["quiz"], prefixes=P))
async def quiz_cmd(client, message: Message):
    q, a = random.choice(QUIZ)
    await _out(message, f"❓ <b>Quiz</b>\n{q}\n<code>Answer: {a}</code>")
