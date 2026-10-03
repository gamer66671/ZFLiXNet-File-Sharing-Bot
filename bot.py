import os
import asyncio
import nest_asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

nest_asyncio.apply()

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "ZFLiXNet Bot is active and running!"

API_ID = 34505015
API_HASH = "4842676c7e27556093bf3eef1d46f072"
BOT_TOKEN = "7313000494:AAHcGeE4tMuvJ4IoBSzBRjtC-f5-o2zwygE"

AUTO_DELETE_TIME = 300

app = Client(
    "ZFLiXNetBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    await message.reply_text(
        "স্বাগতম ZFLiXNet ফাইল শেয়ারিং বটে! যেকোনো ফাইল দিলে আমি ডাউনলোডের সরাসরি লিংক বানিয়ে দিব, আর ৫ মিনিট পর ফাইলটি অটো-ডিলিট হয়ে যাবে।"
    )

@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(client, message: Message):
    file_id = message.id
    chat_id = message.chat.id
    
    download_link = f"https://t.me/{app.me.username}?start=file_{chat_id}_{file_id}"
    
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📥 Download File Now", url=download_link)]]
    )
    
    sent_msg = await message.reply_text(
        "তোর ডাউনলোড লিংক রেডি! নিচের বাটনে ক্লিক করে ফাইলটি ডাউনলোড কর। ঠিক ৫ মিনিট পর ফাইল এবং লিংক অটোমেটিক ডিলিট হয়ে যাবে।",
        reply_markup=keyboard
    )
    
    await asyncio.sleep(AUTO_DELETE_TIME)
    try:
        await message.delete()
        await sent_msg.edit_text("নিরাপত্তার স্বার্থে ফাইলটি মুছে ফেলা হয়েছে।")
    except Exception as e:
        print(f"ডিলিট করতে সমস্যা হয়েছে: {e}")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    print("ZFLiXNet Bot চালু হচ্ছে...")
    import threading
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    app.run()
