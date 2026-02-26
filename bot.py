import os
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
    return "Bot is active!"

def run_web():
    # Render default port handle karne ke liye
    port = int(os.environ.get("PORT", 8080))
    web.run(host="0.0.0.0", port=port)

# -------- BOT COMMANDS ---------
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Bot is running! Use /all to tag members.")

@app.on_message(filters.command(["all", "tagall"]) & filters.group)
async def tag_all(client, message):
    # Admin Check logic yahan rahegi
    mentions = []
    async for member in client.get_chat_members(message.chat.id):
        if not member.user.is_bot:
            mentions.append(member.user.mention)
    
    for i in range(0, len(mentions), 5):
        await client.send_message(message.chat.id, " ".join(mentions[i:i+5]))

# -------- MAIN RUNNER ---------
if __name__ == "__main__":
    # Flask ko thread mein start karein
    Thread(target=run_web, daemon=True).start()
    
    # app.run() internal asyncio loop ko manage karta hai
    # Ye Render par 'no current event loop' error ko fix karega
    app.run()
