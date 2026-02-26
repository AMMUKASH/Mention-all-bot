import asyncio
import os
import sys
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
try:
    mongo = MongoClient(MONGO_URL)
    db = mongo.MentionBot
    users_db = db.users
except Exception as e:
    print(f"ERROR: Database connect nahi hua - {e}")

# --- BOT CLIENT ---
app = Client("MentionTagBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- WEB SERVER (For Render Uptime) ---
web = Flask(__name__)
@web.route('/')
def home(): return "Bot is Alive!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web.run(host="0.0.0.0", port=port)

# --- BUTTONS ---
START_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ 𝐀ᴅᴅ 𝐌𝝴 𝝸𝝶 𝐘𝞂𝞄𝐑 𝐆𝐑𝞂𝞄𝞀 ➕", url=f"https://t.me/Mentiontagallbot?startgroup=true")],
    [InlineKeyboardButton("📜 𝐇𝝴ʟᴘ & 𝐂𝞂𝐦𝐦𝝰𝝶ᴅ𝐬", callback_data="help_menu")],
    [InlineKeyboardButton("❂ 𝐔𝛒ᴅ𝛂𝛕𝛆 ❂", url="https://t.me/radhesupport"),
     InlineKeyboardButton("❂ 𝐒𝛖𝛒𝛒𝛔ʀ𝛕 ❂", url="https://t.me/+OGbh7_kV7SAyYTEx")]
])

# --- HANDLERS ---
@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    try:
        if not users_db.find_one({"user_id": message.from_user.id}):
            users_db.insert_one({"user_id": message.from_user.id})
    except: pass
    await message.reply_photo(photo=START_IMG, caption="✨ **𝐖𝝴ʟ𝐜𝞂𝐦𝝴 𝐓𝞂 𝐌𝝴𝝶𝛕𝝸𝞂𝝶 𝐁𝞂𝛕** ✨\n\nI can mention all members with stylish quotes! 🚀", reply_markup=START_BUTTONS)

@app.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    if query.data == "help_menu":
        await query.message.edit_caption(caption="🛠 **𝐇𝝴ʟᴘ & 𝐂𝞂𝐦𝐦𝝰𝝶ᴅ𝐬**\n\n/all - Mention all members\n/cancel - Stop process", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 𝐁𝝰𝐜𝐤", callback_data="start_menu")]]))
    elif query.data == "start_menu":
        await query.message.edit_caption(caption="✨ **𝐖𝝴ʟ𝐜𝞂𝐦𝝴 𝐓𝞂 𝐌𝝴𝝶𝛕𝝸𝞂𝝶 𝐁𝞂𝛕** ✨", reply_markup=START_BUTTONS)

# Tagging Logic
IS_STOPPED = {}

@app.on_message(filters.command(["all", "tagall"]) & filters.group)
async def tag_all(client, message):
    chat_id = message.chat.id
    try:
        user = await client.get_chat_member(chat_id, message.from_user.id)
        if not (user.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]):
            return await message.reply_text("❌ **Only Admins can use this!**")
    except: return

    IS_STOPPED[chat_id] = False
    mentions_list = []
    async for member in client.get_chat_members(chat_id):
        if not member.user.is_bot:
            mentions_list.append(f"@{member.user.username}" if member.user.username else member.user.mention)

    await message.reply_text(f"🚀 **Tagging {len(mentions_list)} members in batches...**")
    
    # Batch size 5 to 10 with quotes
    for i in range(0, len(mentions_list), 5):
        if IS_STOPPED.get(chat_id): break
        batch = " ".join(mentions_list[i:i+5])
        await client.send_message(chat_id, f'"{batch}"')
        await asyncio.sleep(3)

@app.on_message(filters.command("cancel") & filters.group)
async def cancel_tag(client, message):
    IS_STOPPED[message.chat.id] = True
    await message.reply_text("🛑 **Stopped.**")

# --- MAIN RUNNER (Fix for Event Loop Error) ---
async def main():
    print("✨ Bot is Starting...")
    Thread(target=run_web, daemon=True).start()
    await app.start()
    print("✅ Bot is Online!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
