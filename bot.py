import asyncio
import logging
from pytube import YouTube
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from tqdm import tqdm
import aiofiles
import os

# Your API credentials
API_ID = 22420997
API_HASH = "d7fbe2036e9ed2a1468fad5a5584a255"
TOKEN = "7513058089:AAHAPtJbHEPbRMbV8rv-gAZ8KVL0ykAM2pE"

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me a YouTube URL to download.")

async def download_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text(f"Downloading video from {url}...")

    try:
        yt = YouTube(url)
        video_stream = yt.streams.get_highest_resolution()

        await update.message.reply_text(f"Downloading {video_stream.title}...")

        # Create download folder if it doesn't exist
        os.makedirs("downloads", exist_ok=True)

        # Using tqdm for progress bar
        with tqdm(total=100, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}', unit='%', unit_scale=True, dynamic_ncols=True) as pbar:
            def progress_callback(stream, chunk: bytes, bytes_remaining: int):
                # Calculate the percentage completed
                percentage = (1 - bytes_remaining / stream.filesize) * 100
                pbar.n = percentage
                pbar.refresh()

            video_stream.download(output_path="downloads", on_progress_callback=progress_callback)

        video_file_path = f'downloads/{video_stream.default_filename}'
        
        async with aiofiles.open(video_file_path, 'rb') as video_file:
            await update.message.reply_video(video_file, caption=yt.title)

        await update.message.reply_text("Download complete!")
    except Exception as e:
        logging.error(f"Error downloading video: {str(e)}")
        await update.message.reply_text(f"Error: {str(e)}")

async def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_youtube))

    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
