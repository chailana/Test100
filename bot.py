import os
import re
import subprocess
import aiohttp
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Load environment variables from .env file
load_dotenv()

API_ID = os.getenv("API_ID")  # Your API ID
API_HASH = os.getenv("API_HASH")  # Your API HASH
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Your Bot Token

app = Client("url_uploader_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

async def download_file(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                filename = url.split("/")[-1]  # Get the file name from the URL
                with open(filename, 'wb') as f:
                    f.write(await response.read())
                return filename
            else:
                return None

def generate_thumbnail(video_path):
    thumbnail_path = "thumbnail.jpg"
    # Generate a thumbnail using FFmpeg
    command = [
        'ffmpeg',
        '-i', video_path,
        '-ss', '00:00:01.000',  # Take a snapshot at 1 second
        '-vframes', '1',
        thumbnail_path
    ]
    subprocess.run(command)
    return thumbnail_path

async def get_video_quality_options(video_url):
    # This function simulates fetching video quality options.
    # Replace this with actual logic to retrieve quality options from your video source.
    return ["360p", "480p", "720p", "1080p"]

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    await message.reply("Hello! I am your URL uploader bot. Use the /upload command followed by the URL to upload files.")

@app.on_message(filters.command("upload") & filters.private)
async def upload_file(client, message):
    if len(message.command) < 2:
        await message.reply("Please provide a URL.")
        return
    
    url = message.command[1]
    await message.reply("Downloading your file...")

    # Download the file to check if it's a video
    filename = await download_file(url)
    
    if filename:
        # Check if the file is a video and generate a thumbnail
        if re.search(r'\.mp4|\.mkv|\.avi', filename):
            thumbnail = generate_thumbnail(filename)
            await message.reply_photo(photo=thumbnail, caption="Here's the thumbnail of your video.")
            
            # Fetch available quality options
            qualities = await get_video_quality_options(url)
            buttons = [[InlineKeyboardButton(q, callback_data=f"quality_{q}") for q in qualities]]
            await message.reply("Select the video quality:", reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await message.reply("The uploaded file is not a supported video format.")
        os.remove(filename)  # Remove the downloaded file
    else:
        await message.reply("Failed to download the file.")

@app.on_callback_query(filters.regex(r"quality_"))
async def handle_quality_selection(client, callback_query):
    quality = callback_query.data.split("_")[1]  # Extract quality from callback data
    await callback_query.answer(f"You selected {quality} quality.")
    
    # Logic to download the video in the selected quality
    original_url = ...  # You will need to store the original URL in context or handle it accordingly
    quality_url = f"{original_url}?quality={quality}"  # Modify based on how the source works
    
    await callback_query.message.reply("Downloading your video...")
    filename = await download_file(quality_url)

    if filename:
        await callback_query.message.reply_document(document=filename)
        os.remove(filename)  # Clean up the downloaded file
    else:
        await callback_query.message.reply("Failed to download the selected quality.")

if __name__ == "__main__":
    app.run()
