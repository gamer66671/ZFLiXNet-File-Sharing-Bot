import os
import asyncio
import threading
import nest_asyncio
from flask import Flask

# --- Python 3.14 + Pyrogram Event Loop Fix ---
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

nest_asyncio.apply()

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

# --- Flask Setup (To keep the bot alive on Render) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "ZFLiXNet Bot is active and running!"

# --- Bot Configurations ---
API_ID = 34505015
API_HASH = "4842676c7e27556093bf3eef1d46f072"
BOT_TOKEN = "7313000494:AAHcGeE4tMuvJ4IoBSzBRjtC-f5-o2zwygE"

# ✅ আপনার অ্যাডমিন আইডি এখানে বসানো হয়েছে
ADMIN_ID = 7091081785 

# --- Default Settings (Can be changed from the bot) ---
AUTO_DELETE_TIME = 300  # Default: 5 minutes (300 seconds)
START_TEXT = "Welcome to ZFLiXNet File Sharing Bot!\n\nSend me any file, and I will generate a direct download link for you. The file will be auto-deleted after {time} seconds."
FILE_TEXT = "Your download link is ready! Click the button below to download the file.\n\n⏳ This file and link will be automatically deleted in {time} seconds."

app = Client(
    "ZFLiXNetBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# --- Admin Commands to Control Bot Settings ---

@app.on_message(filters.command("set_menu") & filters.user(ADMIN_ID))
async def set_bot_menu(client, message: Message):
    # এই কমান্ডটি একবার চালালেই বটের মেনুতে start এবং settings বাটন যুক্ত হয়ে যাবে
    await app.set_bot_commands([
        BotCommand("start", "Start the bot"),
        BotCommand("settings", "Admin Settings Panel")
    ])
    await message.reply_text("✅ বটের মেনু সফলভাবে আপডেট করা হয়েছে! টেলিগ্রামের মেনু (Menu) বাটনে ক্লিক করে দেখুন।")

@app.on_message(filters.command("myid") & filters.private)
async def get_id(client, message: Message):
    await message.reply_text(f"Your Telegram ID is: `{message.from_user.id}`")

@app.on_message(filters.command("set_time") & filters.user(ADMIN_ID))
async def set_time(client, message: Message):
    global AUTO_DELETE_TIME
    try:
        time_in_seconds = int(message.text.split()[1])
        AUTO_DELETE_TIME = time_in_seconds
        await message.reply_text(f"✅ Auto-delete time updated to **{AUTO_DELETE_TIME}** seconds.")
    except (IndexError, ValueError):
        await message.reply_text("❌ Usage: `/set_time <seconds>`\nExample: `/set_time 120` (for 2 minutes)")

@app.on_message(filters.command("set_start") & filters.user(ADMIN_ID))
async def set_start_text(client, message: Message):
    global START_TEXT
    new_text = message.text.replace("/set_start ", "")
    if new_text:
        START_TEXT = new_text
        await message.reply_text("✅ Start message updated successfully.")
    else:
        await message.reply_text("❌ Usage: `/set_start Your new welcome message here.`\n(Use {time} to show the delete time)")

@app.on_message(filters.command("set_file") & filters.user(ADMIN_ID))
async def set_file_text(client, message: Message):
    global FILE_TEXT
    new_text = message.text.replace("/set_file ", "")
    if new_text:
        FILE_TEXT = new_text
        await message.reply_text("✅ File link message updated successfully.")
    else:
        await message.reply_text("❌ Usage: `/set_file Your new link message here.`\n(Use {time} to show the delete time)")

@app.on_message(filters.command("settings") & filters.user(ADMIN_ID))
async def show_settings(client, message: Message):
    settings_text = (
        f"⚙️ **Current Bot Settings:**\n\n"
        f"**Auto-Delete Time:** {AUTO_DELETE_TIME} seconds\n\n"
        f"**Start Text:**\n`{START_TEXT}`\n\n"
        f"**File Text:**\n`{FILE_TEXT}`"
    )
    await message.reply_text(settings_text)

# --- Main Handlers ---

@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    # Format the text with the current auto-delete time
    formatted_text = START_TEXT.format(time=AUTO_DELETE_TIME)
    await message.reply_text(formatted_text)

@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(client, message: Message):
    file_id = message.id
    chat_id = message.chat.id
    
    download_link = f"https://t.me/{app.me.username}?start=file_{chat_id}_{file_id}"
    
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📥 Download File Now", url=download_link)]]
    )
    
    formatted_text = FILE_TEXT.format(time=AUTO_DELETE_TIME)
    
    sent_msg = await message.reply_text(
        formatted_text,
        reply_markup=keyboard
    )
    
    # Wait for the custom set time
    await asyncio.sleep(AUTO_DELETE_TIME)
    
    try:
        # Delete the original user's file
        await message.delete()
        # Edit the bot's message to show it's deleted
        await sent_msg.edit_text("⚠️ The file has been deleted for security reasons.")
    except Exception as e:
        print(f"Deletion error: {e}")

# --- Flask Run Function ---
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# --- Main Execution ---
if __name__ == "__main__":
    print("ZFLiXNet Bot is starting...")
    
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    app.run()
