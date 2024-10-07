import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from asyncio import Queue
import threading

# Global variable to control the running state
is_running = False

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome! Use /batch <start>-<end> to start uploading files.')

def download_file(message_id: int) -> str:
    """Download file from the given message ID and return the local file path."""
    try:
        url = f"https://api.telegram.org/bot7490926656:AAHG-oUUzGPony9xfyApSI0EbbymhneDU1k/getFile?file_id={message_id}"
        response = requests.get(url).json()
        file_path = response['result']['file_path']
        file_url = f"https://api.telegram.org/file/bot7490926656:AAHG-oUUzGPony9xfyApSI0EbbymhneDU1k/{file_path}"
        
        local_file_name = f"{message_id}.jpg"  # Change extension based on expected file type
        with open(local_file_name, 'wb') as f:
            f.write(requests.get(file_url).content)
        return local_file_name
    
    except Exception as e:
        print(f"Error downloading message {message_id}: {e}")
        return None

def upload_file(update: Update, file_path: str) -> None:
    """Upload the downloaded file to Telegram."""
    try:
        with open(file_path, 'rb') as f:
            update.message.reply_document(f)
        os.remove(file_path)  # Remove the file after uploading
    
    except Exception as e:
        update.message.reply_text(f"Error uploading {file_path}: {e}")

def process_links(start: int, end: int, update: Update) -> None:
    """Process each message ID for download and upload."""
    global is_running
    
    for message_id in range(start, end + 1):
        if not is_running:
            break
        
        update.message.reply_text(f'Processing message ID {message_id}...')
        
        # Download the file
        file_path = download_file(message_id)
        
        if file_path:
            # Upload the downloaded file
            upload_file(update, file_path)
    
    if is_running:
        update.message.reply_text('Batch upload completed.')

def batch(update: Update, context: CallbackContext) -> None:
    """Start batch upload process."""
    global is_running
    
    try:
        start_end = context.args[0].split('-')
        
        if len(start_end) != 2:
            raise ValueError("Invalid range format. Please use /batch <start>-<end>.")
        
        start = int(start_end[0])
        end = int(start_end[1])
        
        update.message.reply_text(f'Starting batch upload from {start} to {end}...')
        
        # Start processing in a new thread to avoid blocking
        threading.Thread(target=process_links, args=(start, end, update)).start()
    
    except (IndexError, ValueError):
        update.message.reply_text('Please provide a valid range like /batch 347-3003.')

def stop(update: Update, context: CallbackContext) -> None:
    """Stop the ongoing process."""
    global is_running
    
    is_running = False
    
    update.message.reply_text('Stopping ongoing processes...')

def main() -> None:
    """Run the bot."""
    
    my_queue = Queue()  # Create an update queue
    updater = Updater("7490926656:AAHG-oUUzGPony9xfyApSI0EbbymhneDU1k", update_queue=my_queue)
    
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("batch", batch))
    updater.dispatcher.add_handler(CommandHandler("stop", stop))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
