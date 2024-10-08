import os
import re
import subprocess
from dotenv import load_dotenv
from pyrogram import Client, filters
import aiohttp

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

@app.on_message(filters.command("upload") & filters.private)
async def upload_file(client, message):
    if len(message.command) < 2:
        await message.reply("Please provide a URL.")
        return
    
    url = message.command[1]
    await message.reply("Downloading your file...")

    # Download the file
    filename = await download_file(url)
    
    if filename:
        # Check if the file is a video and generate a thumbnail
        if re.search(r'\.mp4|\.mkv|\.avi', filename):
            thumbnail = generate_thumbnail(filename)
            await message.reply_photo(photo=thumbnail, caption="Here's the thumbnail of your video.")

        await message.reply_document(document=filename)
        os.remove(filename)  # Remove the file after sending
        
        if 'thumbnail' in locals():
            os.remove(thumbnail)  # Remove thumbnail after sending
    else:
        await message.reply("Failed to download the file.")

if __name__ == "__main__":
    app.run()
