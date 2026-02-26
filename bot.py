import os
import asyncio
from threading import Thread
from pyrogram import Client, filters, enums, idle
from flask import Flask
from pymongo import MongoClient

# -------- CONFIG ---------
API_ID = 34135757
API_HASH = "d3d5548fe0d98eb1fb793c2c37c9e5c8"
BOT_TOKEN = "8752567586:AAG04Z6vLXVLXZZkQAy_ra7w6Z8suLmD3a8"
MONGO_URL = "mongodb+srv://misssqn:VICTOR01@cluster0.3otqmso.mongodb.net/?appName=Cluster0"

# -------- DATABASE ---------
mongo = MongoClient(MONGO_URL)
db = mongo.MentionBot
users_db = db.users

# -------- BOT CLIENT ---------
app = Client(
    "MentionTagBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# -------- WEB SERVER ---------
web = Flask(__name__)

@web.route('/')
def home():
    return "Bot is running perfectly!"

def run_web():
    # Render default port 10000 ya environment variable leta hai
    port = int(os.environ.get("PORT", 8080))
    web.run(host="0.0.0.0", port=port)

# -------- TAGGING SYSTEM ---------
IS_STOPPED = {}

@app.on_message(filters.command(["all", "tagall"]) & filters.group)
async def tag_all(client, message):
    chat_id = message.chat.id
    try:
        user = await client.get_chat_member(chat_id, message.from_user.id)
        if user.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            return await message.reply_text("❌ Admin power needed!")
    except: return

    IS_STOPPED[chat_id] = False
    mentions = []
    async for member in client.get_chat_members(chat_id):
        if not member.user.is_bot:
            mentions.append(member.user.mention)

    await message.reply_text(f"🚀 Tagging {len(mentions)} members...")
    for i in range(0, len(mentions), 5):
        if IS_STOPPED.get(chat_id): break
        await client.send_message(chat_id, " ".join(mentions[i:i+5]))
        await asyncio.sleep(2)

@app.on_message(filters.command("cancel") & filters.group)
async def cancel_tag(client, message):
    IS_STOPPED[message.chat.id] = True
    await message.reply_text("🛑 Stopped.")

# -------- STARTING THE BOT ---------
if __name__ == "__main__":
    # 1. Flask ko alag thread mein start karo
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    
    # 2. Pyrogram ka run() method use karo (Ye loop error ko solve karta hai)
    print("Starting bot...")
    app.run()
