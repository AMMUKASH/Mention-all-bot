import asyncio
import os
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from flask import Flask
from threading import Thread
from pymongo import MongoClient

# --- CONFIGURATION ---
API_ID = 34135757
API_HASH = "d3d5548fe0d98eb1fb793c2c37c9e5c8"
BOT_TOKEN = "8752567586:AAG04Z6vLXVLXZZkQAy_ra7w6Z8suLmD3a8"
START_IMG = "https://graph.org/file/25cec9c36c9d5997985c8-5208bbc342ec7eac96.jpg"
MONGO_URL = "mongodb+srv://misssqn:VICTOR01@cluster0.3otqmso.mongodb.net/?appName=Cluster0"

# --- DATABASE ---
mongo = MongoClient(MONGO_URL)
db = mongo.MentionBot
users_db = db.users

# --- BOT CLIENT ---
app = Client("MentionTagBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- WEB SERVER FOR RENDER (Fixes 24/7 & Boot Error) ---
web = Flask(__name__)
@web.route('/')
def home(): return "Bot is Alive!"

def run_web():
    # Render automatically passes a PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    web.run(host="0.0.0.0", port=port)

# --- BUTTONS ---
START_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ 𝐀ᴅᴅ 𝐌𝝴 𝝸𝝶 𝐘𝞂𝞄𝐑 𝐆𝐑𝞂𝞄𝞀 ➕", url=f"https://t.me/Mentiontagallbot?startgroup=true")],
    [InlineKeyboardButton("📜 𝐇𝝴ʟᴘ & 𝐂𝞂𝐦𝐦𝝰𝝶ᴅ𝐬", callback_data="help_menu")],
    [InlineKeyboardButton("❂ 𝐔𝛒ᴅ𝛂𝛕𝛆 ❂", url="https://t.me/radhesupport"),
     InlineKeyboardButton("❂ 𝐒𝛖𝛒𝛒𝛔ʀ𝛕 ❂", url="https://t.me/+OGbh7_kV7SAyYTEx")]
])

HELP_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("📖 𝐆𝞄𝝸ᴅ𝝴", callback_data="guide_menu")],
    [InlineKeyboardButton("🔙 𝐁𝝰𝐜𝐤", callback_data="start_menu")]
])

# --- COMMANDS ---
@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    if not users_db.find_one({"user_id": message.from_user.id}):
        users_db.insert_one({"user_id": message.from_user.id})
    await message.reply_photo(
        photo=START_IMG,
        caption=f"✨ **𝐖𝝴ʟ𝐜𝞂𝐦𝝴 𝐓𝞂 𝐌𝝴𝝶𝛕𝝸𝞂𝝶 𝐁𝞂𝛕** ✨\n\nI can mention all members in your group with stylish quotes! 🚀\n\n👤 **𝐎𝐰𝐧𝐞𝐫:** [𝐏𝐄𝐓𝐄𝐑](t.me/p3ter_x)",
        reply_markup=START_BUTTONS
    )

@app.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    if query.data == "help_menu":
        await query.message.edit_caption(
            caption="🛠 **𝐇𝝴ʟᴘ & 𝐂𝞂𝐦𝐦𝝰𝝶ᴅ𝐬**\n\n/all or /tagall - Mention all members\n/cancel - Stop process\n/start - Refresh bot",
            reply_markup=HELP_BUTTONS
        )
    elif query.data == "guide_menu":
        await query.message.edit_caption(
            caption="📖 **𝐆𝞄𝝸ᴅ𝝴**\n\n1. Add me to group.\n2. Make me Admin.\n3. Type `/all` to tag everyone.\n\nOnly admins can use me!",
            reply_markup=HELP_BUTTONS
        )
    elif query.data == "start_menu":
        await query.message.edit_caption(
            caption="✨ **𝐖𝝴ʟ𝐜𝞂𝐦𝝴 𝐓𝞂 𝐌𝝴𝝶𝛕𝝸𝞂𝝶 𝐁𝞂𝛕** ✨",
            reply_markup=START_BUTTONS
        )

# --- TAG ALL LOGIC ---
IS_STOPPED = {}

@app.on_message(filters.command(["all", "tagall"]) & filters.group)
async def tag_all(client, message):
    chat_id = message.chat.id
    # Admin Check
    try:
        user = await client.get_chat_member(chat_id, message.from_user.id)
        if not (user.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]):
            return await message.reply_text("❌ **Only Admins can use this!**")
    except: return

    IS_STOPPED[chat_id] = False
    mentions_list = []
    
    async for member in client.get_chat_members(chat_id):
        if member.user.is_bot or member.user.is_deleted: continue
        user_link = f"@{member.user.username}" if member.user.username else member.user.mention
        mentions_list.append(user_link)

    await message.reply_text(f"🚀 **𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐌𝐞𝐧𝐭𝐢𝐨𝐧 𝐟𝐨𝐫 {len(mentions_list)} 𝐦𝐞𝐦𝐛𝐞𝐫𝐬...**")

    # 5 members per batch in "Quotes"
    for i in range(0, len(mentions_list), 5):
        if IS_STOPPED.get(chat_id): break
        batch = " ".join(mentions_list[i:i+5])
        # Poora message quotes mein
        await client.send_message(chat_id, f'"{batch}"')
        await asyncio.sleep(3)

@app.on_message(filters.command("cancel") & filters.group)
async def cancel_tag(client, message):
    IS_STOPPED[message.chat.id] = True
    await message.reply_text("🛑 **Stopped.**")

# --- START BOT ---
if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    app.run()
