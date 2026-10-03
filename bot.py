import os
import asyncio
import threading
import nest_asyncio
import pymongo
import secrets
from flask import Flask
from urllib.parse import urlparse

# --- Python 3.14 + Pyrogram Event Loop Fix ---
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

nest_asyncio.apply()

from pyrogram import Client, filters
from pyrogram.types import Message

# --- Flask Setup (To keep the bot alive on Render) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "ZFLiXNet File Store Bot is active!"

# --- Bot Configurations ---
API_ID = 34505015
API_HASH = "4842676c7e27556093bf3eef1d46f072"
BOT_TOKEN = "7313000494:AAHcGeE4tMuvJ4IoBSzBRjtC-f5-o2zwygE"
ADMIN_ID = 7091081785 

# ✅ MongoDB কানেকশন লিংক (ইউজারনেম ও পাসওয়ার্ড বসানো)
MONGO_URI = "mongodb+srv://53820132:53820132@cluster0.m9wwy0y.mongodb.net/?appName=Cluster0"

app = Client("ZFLiXNetBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- Database Setup ---
db_client = pymongo.MongoClient(MONGO_URI)
db = db_client["ZFLiXNet"]
links_col = db["links"]

# --- Helper Function to Extract Link Info (Fixed Version) ---
def parse_telegram_link(link):
    try:
        path = urlparse(link).path.strip("/")
        parts = path.split("/")
        
        # প্রাইভেট চ্যানেলের লিংক (যেমন: https://t.me/c/123456789/123)
        if len(parts) == 3 and parts[0] == 'c':
            chat_id = int("-100" + parts[1])
            msg_id = int(parts[2])
            return chat_id, msg_id
            
        # পাবলিক চ্যানেলের লিংক (যেমন: https://t.me/ZFLixNetEntertainment/1075)
        elif len(parts) == 2:
            chat_id = parts[0]
            msg_id = int(parts[1])
            return chat_id, msg_id
            
    except Exception as e:
        print(f"Error parsing link: {e}")
    return None, None

# --- Main Handlers ---

@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    # ইউজার শেয়ারেবল লিংকে ক্লিক করলে
    if len(message.command) > 1:
        token = message.command[1]
        data = links_col.find_one({"_id": token})
        
        if data:
            await message.reply_text("⏳ Please wait, fetching your file...")
            try:
                # চ্যানেল থেকে ফাইল কপি করে ইউজারকে পাঠানো
                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=data["chat_id"],
                    message_id=data["msg_id"]
                )
            except Exception as e:
                await message.reply_text(f"❌ Error: Could not send the file. Make sure I am an Admin in your channel.\n\n`{e}`")
        else:
            await message.reply_text("❌ Invalid or expired link!")
    else:
        await message.reply_text(
            "Welcome! I am a File Store Bot. 🗂\n\n"
            "Admin can use `/genlink <Telegram Message Link>` to generate a shareable link."
        )

@app.on_message(filters.command("genlink") & filters.user(ADMIN_ID))
async def gen_link_handler(client, message: Message):
    text = message.text or message.caption
    if len(text.split()) < 2:
        await message.reply_text("❌ Please provide a Telegram message link.\n\nExample: `/genlink https://t.me/c/123456789/123`")
        return

    link = text.split(" ")[1]
    chat_id, msg_id = parse_telegram_link(link)
    
    if not chat_id or not msg_id:
        await message.reply_text("❌ Invalid link format! Please send a valid Telegram message link.")
        return
    
    # ইউনিক টোকেন তৈরি
    token = secrets.token_urlsafe(8)
    
    # MongoDB তে সেভ করা
    links_col.insert_one({
        "_id": token,
        "chat_id": chat_id,
        "msg_id": msg_id
    })
    
    # শেয়ারেবল লিংক তৈরি
    shareable_link = f"https://t.me/{app.me.username}?start={token}"
    
    await message.reply_text(
        f"✅ **Link Generated Successfully!**\n\n"
        f"🔗 **Share this link:**\n`{shareable_link}`\n\n"
        f"Anyone who clicks this link will get the file.",
        disable_web_page_preview=True
    )

# --- Flask Run Function ---
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# --- Main Execution ---
if __name__ == "__main__":
    print("ZFLiXNet File Store Bot is starting...")
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    app.run()
