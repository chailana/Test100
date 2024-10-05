import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from pytube import YouTube
import aiohttp
from tqdm import tqdm

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Your API ID, API hash, and bot token
API_ID = '22420997'
API_HASH = 'd7fbe2036e9ed2a1468fad5a5584a255'
BOT_TOKEN = '7513058089:AAHAPtJbHEPbRMbV8rv-gAZ8KVL0ykAM2pE'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome to the URL Uploader Bot! Send me a YouTube video URL to download.")

async def download_video(url: str, quality: str):
    yt = YouTube(url)
    video_stream = yt.streams.get_by_itag(quality) if quality else yt.streams.get_highest_resolution()
    
    if not video_stream:
        raise ValueError("No video stream found for the given quality.")
    
    # Download video
    video_path = video_stream.download(output_path='downloads')
    return video_path

async def progress_bar(current: int, total: int):
    bar_length = 30  # Length of the progress bar
    percent = (current / total) * 100
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(f'\r|{bar}| {percent:.2f}% Complete', end='\r')

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    await update.message.reply_text("Downloading video... Please wait.")
    
    try:
        quality = '22'  # Default quality (720p)
        await update.message.reply_text("Available quality options: 18 (360p), 22 (720p), 137 (1080p). Reply with your choice or leave blank for default.")
        
        # Wait for user response with quality
        quality_response = await context.bot.wait_for('message', chat_id=update.message.chat_id)
        if quality_response.text.strip():
            quality = quality_response.text.strip()

        video_path = await download_video(url, quality)
        await update.message.reply_text("Upload starting...")
        
        with open(video_path, 'rb') as video:
            await context.bot.send_video(chat_id=update.message.chat_id, video=video, progress=progress_bar)
        
        os.remove(video_path)  # Clean up the downloaded file
        await update.message.reply_text("Upload complete!")
    
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text(f"An error occurred: {str(e)}")

async def main() -> None:
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))

    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
