from pyrogram import Client, filters
from bot.client import app
from pyrogram.types import Message
import config

openai_client = None

if config.ENABLE_AI and config.OPENAI_API_KEY:
    try:
        from openai import AsyncOpenAI
        openai_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
    except Exception:
        openai_client = None


@app.on_message(filters.command("ai", prefixes=config.COMMAND_PREFIX) & filters.me)
async def ai_chat(client: Client, message: Message):
    if not config.ENABLE_AI or not openai_client:
        await message.edit_text(
            "AI is disabled.\nSet `ENABLE_AI=true` and `OPENAI_API_KEY` in `.env`"
        )
        return

    if len(message.command) < 2 and not message.reply_to_message:
        await message.edit_text(f"Usage: `{config.COMMAND_PREFIX}ai <your question>`")
        return

    if message.reply_to_message:
        prompt = message.reply_to_message.text or message.reply_to_message.caption or ""
        if len(message.command) > 1:
            prompt = " ".join(message.command[1:]) + "\n\n" + prompt
    else:
        prompt = " ".join(message.command[1:])

    status = await message.edit_text("🤖 Thinking...")

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant integrated into a Telegram userbot. Keep answers concise and useful."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        answer = response.choices[0].message.content
        await status.edit_text(f"**🤖 AI Response:**\n\n{answer}")
    except Exception as e:
        await status.edit_text(f"❌ AI Error: `{e}`")
