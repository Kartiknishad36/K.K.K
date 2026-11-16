"""AI — OPENAI_API_KEY for live answers"""
from pyrogram import filters
from pyrogram.types import Message
from bot.client import app
import config
import os

P = config.COMMAND_PREFIX

async def out(message: Message, text: str):
    try:
        return await message.reply_text(text)
    except Exception:
        try:
            return await message.edit_text(text)
        except Exception:
            return None

@app.on_message(filters.command(["ai", "ask", "gpt"], prefixes=P))
async def ai_cmd(client, message: Message):
    if len(message.command) < 2:
        await out(message, f"Usage: `{P}ai <prompt>`")
        return
    prompt = " ".join(message.command[1:])
    key = os.getenv("OPENAI_API_KEY") or getattr(config, "OPENAI_API_KEY", None)
    if not key:
        await out(message, f"🤖 **AI**\nPrompt: {prompt}\n\n_OPENAI_API_KEY not set — add env to enable live GPT._")
        return
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "max_tokens": 500},
                timeout=60,
            ) as resp:
                data = await resp.json()
                text = data["choices"][0]["message"]["content"]
                await out(message, f"🤖 {text}")
    except Exception as e:
        await out(message, f"❌ `{e}`")
