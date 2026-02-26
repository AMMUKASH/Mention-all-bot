import asyncio
import os
import sys
from threading import Thread

from pyrogram import Client, filters, enums, idle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from flask import Flask
from pymongo import MongoClient


# -------- CONFIG ---------
API_ID = 34135757
API_HASH = "d3d5548fe0d98eb1fb793c2c37c9e5c8"
BOT_TOKEN = "8752567586:AAG04Z6vLXVLXZZkQAy_ra7w6Z8suLmD3a8"
START_IMG = "https://graph.org/file/25cec9c36c9d5997985c8-5208bbc342ec7eac96.jpg"
MONGO_URL = "mongodb+srv://misssqn:VICTOR01@cluster0.3otqmso.mongodb.net/?appName=Cluster0"


# -------- DATABASE ---------
try:
    mongo = MongoClient(MONGO_URL)
    db = mongo.MentionBot
    users_db = db.users
    print("MongoDB Connected Successfully!")
except Exception as e:
    print(f"Mongo ERROR: {e}")


# -------- BOT CLIENT ---------
app = Client(
    "MentionTagBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


# -------- WEB SERVER FOR RENDER ---------
web = Flask(__name__)

@web.route('/')
def home():
    return "Bot Running Successfully!"


def run_web():
    port = int(os.environ.get("PORT", 8080))
    web.run(host="0.0.0.0", port=port)


# -------- BUTTONS ---------
START_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ ADD ME TO GROUP ➕", url="https://t.me/Mentiontagallbot?startgroup=true")],
    [InlineKeyboardButton("📜 HELP MENU", callback_data="help_menu")],
    [
        InlineKeyboardButton("❂ UPDATE ❂", url="https://t.me/radhesupport"),
        InlineKeyboardButton("❂ SUPPORT ❂", url="https://t.me/+OGbh7_kV7SAyYTEx")
    ]
])



# -------- START COMMAND ---------
@app.on_message(filters.command("start"))
async def start_cmd(client, message):

    try:
        if not users_db.find_one({"user_id": message.from_user.id}):
            users_db.insert_one({"user_id": message.from_user.id})
    except:
        pass

    await message.reply_photo(
        photo=START_IMG,
        caption="✨ **Welcome To Mention Tag Bot** ✨\n\nI can mention all group members!",
        reply_markup=START_BUTTONS
    )



# -------- CALLBACK HANDLER ---------
@app.on_callback_query()
async def cb_handler(client, query: CallbackQuery):

    if query.data == "help_menu":
        await query.message.edit_caption(
            caption="🛠 **HELP MENU**\n\n/all - Tag all members\n/cancel - Stop tagging",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ BACK", callback_data="start_menu")]])
        )

    elif query.data == "start_menu":
        await query.message.edit_caption(
            caption="✨ **Welcome Back** ✨",
            reply_markup=START_BUTTONS
        )



# -------- TAGGING SYSTEM ---------
IS_STOPPED = {}

@app.on_message(filters.command(["all", "tagall"]) & filters.group)
async def tag_all(client, message):

    chat_id = message.chat.id

    # Only admin allowed
    try:
        user = await client.get_chat_member(chat_id, message.from_user.id)
        if user.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            return await message.reply_text("❌ Only admins can use this command!")
    except:
        return

    IS_STOPPED[chat_id] = False
    mentions = []

    async for member in client.get_chat_members(chat_id):
        if not member.user.is_bot:
            mention = f"@{member.user.username}" if member.user.username else member.user.mention
            mentions.append(mention)

    await message.reply_text(f"🚀 Tagging {len(mentions)} users…")

    for i in range(0, len(mentions), 5):

        if IS_STOPPED.get(chat_id):
            break

        batch = " ".join(mentions[i:i+5])
        await client.send_message(chat_id, batch)
        await asyncio.sleep(2)



@app.on_message(filters.command("cancel") & filters.group)
async def cancel_tag(client, message):
    IS_STOPPED[message.chat.id] = True
    await message.reply_text("🛑 Tagging Stopped.")



# -------- MAIN FUNCTION FIXED ---------
async def start_bot():
    print("Starting Flask server...")
    Thread(target=run_web, daemon=True).start()

    print("Starting bot...")
    await app.start()
    print("Bot is Online!")
    await idle()  # PYROGRAM SAFE FUNCTION

    await app.stop()
    print("Bot Stopped!")


if __name__ == "__main__":
    asyncio.run(start_bot())
