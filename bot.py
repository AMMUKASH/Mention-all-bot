import os
import asyncio
from threading import Thread
from pyrogram import Client, filters, enums
from flask import Flask
from pymongo import MongoClient

# -------- CONFIG (Use Environment Variables for Safety) ---------
API_ID = int(os.environ.get("API_ID", 34135757))
API_HASH = os.environ.get("API_HASH", "d3d5548fe0d98eb1fb793c2c37c9e5c8")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8752567586:AAG04Z6vLXVLXZZkQAy_ra7w6Z8suLmD3a8")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://misssqn:VICTOR01@cluster0.3otqmso.mongodb.net/?appName=Cluster0")

# -------- DATABASE ---------
try:
    mongo = MongoClient(MONGO_URL)
    db = mongo.MentionBot
    users_db = db.users
except Exception as e:
    print(f"DB Error: {e}")

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
    return "Bot is running alive!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web.run(host="0.0.0.0", port=port)

# -------- HELPERS ---------
TAGGING_CHATS = [] # To keep track of active tagging

# -------- BOT COMMANDS ---------
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 Hello! I am a Mention All Bot.\n\nUse /all [text] to tag everyone.")

@app.on_message(filters.command(["all", "tagall"]) & filters.group)
async def tag_all(client, message):
    # Admin Check
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if not (user.status == enums.ChatMemberStatus.ADMINISTRATOR or user.status == enums.ChatMemberStatus.OWNER):
        return await message.reply_text("❌ Sirf Admins hi ye command use kar sakte hain!")

    if message.chat.id in TAGGING_CHATS:
        return await message.reply_text("⚠️ Pehle se ek tagging process chal rahi hai. /stop use karein.")

    TAGGING_CHATS.append(message.chat.id)
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else "Ghabrana nahi hai, sabko bula lo!"
    
    mentions = []
    async for member in client.get_chat_members(message.chat.id):
        if message.chat.id not in TAGGING_CHATS:
            break
        if not member.user.is_bot:
            mentions.append(member.user.mention)
    
    # Send in batches of 5 to avoid spam filters
    for i in range(0, len(mentions), 5):
        if message.chat.id not in TAGGING_CHATS:
            break
        
        batch = " ".join(mentions[i:i+5])
        await client.send_message(message.chat.id, f"{text}\n\n{batch}")
        await asyncio.sleep(2) # Flood wait protection

    if message.chat.id in TAGGING_CHATS:
        TAGGING_CHATS.remove(message.chat.id)
    await message.reply_text("✅ Tagging complete!")

@app.on_message(filters.command("stop") & filters.group)
async def stop_tagging(client, message):
    if message.chat.id in TAGGING_CHATS:
        TAGGING_CHATS.remove(message.chat.id)
        await message.reply_text("🛑 Tagging rok di gayi hai.")
    else:
        await message.reply_text("Koi tagging process nahi chal rahi.")

# -------- MAIN RUNNER ---------
if __name__ == "__main__":
    # Start Flask in background
    Thread(target=run_web, daemon=True).start()
    
    # Run Pyrogram
    print("Bot Starting...")
    app.run()
