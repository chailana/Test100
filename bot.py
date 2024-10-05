import yt_dlp
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from pyrogram import Client

# Add your API ID, API Hash, and Bot Token
API_ID = '22420997'
API_HASH = 'd7fbe2036e9ed2a1468fad5a5584a255'
BOT_TOKEN = '7513058089:AAHAPtJbHEPbRMbV8rv-gAZ8KVL0ykAM2pE'

# Initialize Pyrogram client for larger file uploads
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to start the bot
async def start(update: Update, context):
    await update.message.reply_text("Send me a YouTube URL to download the video!")

# Function to fetch available formats and display them as inline buttons
async def get_formats(update: Update, context):
    url = update.message.text
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = info_dict.get('formats', [])

    keyboard = []
    for f in formats:
        if f['vcodec'] != 'none':
            format_id = f['format_id']
            resolution = f.get('resolution', 'Unknown')
            button = InlineKeyboardButton(f"{resolution} - {f['ext']}", callback_data=f"{format_id}|{url}")
            keyboard.append([button])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a format:", reply_markup=reply_markup)

# Function to handle format selection
async def download_video(update: Update, context):
    query = update.callback_query
    await query.answer()

    format_id, url = query.data.split('|')
    ydl_opts = {'format': format_id, 'outtmpl': 'video.%(ext)s'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Send the video using Pyrogram for large files
    async with app:
        await app.send_video(chat_id=query.message.chat_id, video="video.mp4")

if __name__ == "__main__":
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_formats))
    application.add_handler(CallbackQueryHandler(download_video))

    application.run_polling()
