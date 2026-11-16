"""Fun ASCII animations — rose/cat/moon/heart + text banners (K.K.K)"""
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from bot.client import app
import config

P = config.COMMAND_PREFIX

def _cmd(*names):
    return filters.command(list(names), prefixes=P)

CAT_ANIMATION = ["🐈", "🐈\nWalking...", "╱|、\n( .. )\n |、˜〵\nじしˍ,)ノ", "╱|、\n(˚ˎ 。7  < Meow! 🎵\n |、˜〵\nじしˍ,)ノ"]
FLOWER_BLOOM = ["🌱", "🌿\n🌿\n🌿", "🌷\n🌷\n🌷", "🌹\n🌹\n🌹"]
ROSE_ART = "ROSE\n  @\n \\|/\n  |"
HACKER_ART = "[>] connecting...\n[>] access granted\n[✓] HACKED"
ERROR_ART = "FATAL ERROR"
FUCK_ART = "🖕"
BUTTERFLY_ART = "🦋"
YOURMOM_ART = "(mom)"
MYSON_ART = "(bunny)"
MOON_PHASES = ["🌑", "🌒", "🌓", "🌔", "🌕", "✨"]
MOON_ART = "FULL MOON"
HEART_BUILD = ["❤️", "❤️ ❤️", "❤️ LOVE ❤️"]
HEART_ART = "<3"
OK_ART = "  ___  _  __\n / _ \\| |/ /\n| |_| |   <\n \\___/|_|\\_\\"
VIP_ART = "VIP"
BOSS_ART = "BOSS"
PRO_ART = "PRO"
KING_ART = "KING"
YASHIKA_ART = "YASHIKA"
WIN_ART = "WIN"
GG_ART = "GG"
HI_ART = "HI"
BYE_ART = "BYE"

async def smart_edit(message: Message, text: str, sleep_time: float = 0.5):
    try:
        await message.edit_text(text)
        await asyncio.sleep(sleep_time)
    except FloodWait as e:
        if e.value < 8:
            await asyncio.sleep(e.value)
            try:
                await message.edit_text(text)
            except Exception:
                pass
    except Exception:
        pass

async def draw_art(message: Message, art_var: str, header: str = "", footer: str = ""):
    display = f"<code>{art_var}</code>"
    if header:
        display = f"<b>{header}</b>\n" + display
    if footer:
        display += f"\n\n<b>{footer}</b>"
    await smart_edit(message, display, 0.3)

@app.on_message(_cmd("cat"), group=-8)
async def cat_cmd(client, message: Message):
    m = await message.reply_text("🐈")
    for frame in CAT_ANIMATION:
        await smart_edit(m, f"<code>{frame}</code>", 0.4)

@app.on_message(_cmd("rose"), group=-8)
async def rose_cmd(client, message: Message):
    m = await message.reply_text("🌱")
    for frame in FLOWER_BLOOM:
        await smart_edit(m, f"<code>{frame}</code>", 0.55)
    await draw_art(m, ROSE_ART, footer="🌹 FOR YOU!")

@app.on_message(_cmd("hacker", "hack"), group=-8)
async def hacker_cmd(client, message: Message):
    m = await message.reply_text("💻 Hacking...")
    await draw_art(m, HACKER_ART, footer="💻 SYSTEM HACKED!")

@app.on_message(_cmd("error"), group=-8)
async def error_cmd(client, message: Message):
    m = await message.reply_text("⚠️")
    await draw_art(m, ERROR_ART, footer="⚠️ FATAL ERROR")

@app.on_message(_cmd("fuck"), group=-8)
async def fuck_cmd(client, message: Message):
    m = await message.reply_text("🖕")
    await draw_art(m, FUCK_ART, footer="🖕")

@app.on_message(_cmd("butterfly"), group=-8)
async def butterfly_cmd(client, message: Message):
    m = await message.reply_text("🦋")
    await draw_art(m, BUTTERFLY_ART, footer="🦋 Fly High!")

@app.on_message(_cmd("love"), group=-8)
async def love_cmd(client, message: Message):
    m = await message.reply_text("❤️")
    await smart_edit(m, "<b>I LOVE YOU ❤️</b>", 0.5)

@app.on_message(_cmd("moon", "chand"), group=-8)
async def moon_cmd(client, message: Message):
    m = await message.reply_text("🌑")
    for frame in MOON_PHASES:
        await smart_edit(m, frame, 0.4)
    await draw_art(m, MOON_ART, footer="✨ Good night")

@app.on_message(_cmd("heart", "heartart"), group=-8)
async def heartart_cmd(client, message: Message):
    m = await message.reply_text("❤️")
    for frame in HEART_BUILD:
        await smart_edit(m, f"<code>{frame}</code>", 0.4)
    await draw_art(m, HEART_ART, footer="❤️ FOR YOU")

@app.on_message(_cmd("yourmom"), group=-8)
async def yourmom_cmd(client, message: Message):
    m = await message.reply_text("...")
    await draw_art(m, YOURMOM_ART)

@app.on_message(_cmd("myson"), group=-8)
async def myson_cmd(client, message: Message):
    m = await message.reply_text("🐰")
    await draw_art(m, MYSON_ART, footer="🐰 Me & My Son")

@app.on_message(_cmd("ok"), group=-8)
async def ok_cmd(client, message: Message):
    m = await message.reply_text("✅")
    await draw_art(m, OK_ART, footer="✅ OK")

@app.on_message(_cmd("vip"), group=-8)
async def vip_cmd(client, message: Message):
    m = await message.reply_text("💎")
    await draw_art(m, VIP_ART, footer="💎 VIP")

@app.on_message(_cmd("boss"), group=-8)
async def boss_cmd(client, message: Message):
    m = await message.reply_text("👑")
    await draw_art(m, BOSS_ART, footer="👑 BOSS")

@app.on_message(_cmd("pro"), group=-8)
async def pro_cmd(client, message: Message):
    m = await message.reply_text("⚡")
    await draw_art(m, PRO_ART, footer="⚡ PRO")

@app.on_message(_cmd("king"), group=-8)
async def king_cmd(client, message: Message):
    m = await message.reply_text("👑")
    await draw_art(m, KING_ART, footer="👑 KING")

@app.on_message(_cmd("yashika"), group=-8)
async def yashika_cmd(client, message: Message):
    m = await message.reply_text("✨")
    await draw_art(m, YASHIKA_ART, footer="✨ YASHIKA")

@app.on_message(_cmd("win"), group=-8)
async def win_cmd(client, message: Message):
    m = await message.reply_text("🏆")
    await draw_art(m, WIN_ART, footer="🏆 WIN")

@app.on_message(_cmd("gg"), group=-8)
async def gg_cmd(client, message: Message):
    m = await message.reply_text("🔥")
    await draw_art(m, GG_ART, footer="🔥 GG")

@app.on_message(_cmd("hi"), group=-8)
async def hi_cmd(client, message: Message):
    m = await message.reply_text("👋")
    await draw_art(m, HI_ART, footer="👋 HI")

@app.on_message(_cmd("bye"), group=-8)
async def bye_cmd(client, message: Message):
    m = await message.reply_text("👋")
    await draw_art(m, BYE_ART, footer="👋 BYE")

@app.on_message(_cmd("funhelp", "arts"), group=-8)
async def funhelp_cmd(client, message: Message):
    await message.reply_text(
        "🎨 <b>FUN ARTS</b>\n"
        "<code>.cat</code> <code>.rose</code> <code>.hacker</code>\n"
        "<code>.error</code> <code>.fuck</code> <code>.butterfly</code>\n"
        "<code>.love</code> <code>.moon</code> <code>.heart</code>\n"
        "<code>.ok</code> <code>.vip</code> <code>.boss</code> <code>.pro</code>\n"
        "<code>.king</code> <code>.yashika</code> <code>.win</code>\n"
        "<code>.gg</code> <code>.hi</code> <code>.bye</code>"
    )
