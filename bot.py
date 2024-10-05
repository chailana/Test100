
import yt_dlp
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

BOT_TOKEN = "YOUR_BOT_TOKEN"

# Function to start the bot
async def start(update: Update, context):
    await update.message.reply_text("Send me a YouTube URL to download the video!")

# Function to fetch available formats and display them as inline buttons
async def get_formats(update: Update, context):
    url = update.message.text

    # Using yt-dlp to get available formats
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = info_dict.get('formats', [])

    # Create inline buttons for each format
    keyboard = []
    for f in formats:
        if f['vcodec'] != 'none':  # Exclude audio-only formats
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

    # Extract format ID and URL from callback data
    format_id, url = query.data.split('|')

    # Download the video in the selected format
    ydl_opts = {'format': format_id, 'outtmpl': 'video.%(ext)s'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Send the video file to the user
    with open("video.mp4", "rb") as video_file:
        await query.message.reply_video(video=video_file)

if __name__ == "__main__":
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_formats))
    application.add_handler(CallbackQueryHandler(download_video))

    application.run_polling()
