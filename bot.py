import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import threading

# Global variable to control the running state
is_running = False

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome! Use /batch <link1> <link2> ... to start uploading files.')

def download_file(url: str) -> str:
    """Download file from the given URL and return the local file path."""
    try:
        response = requests.get(url)
        file_name = url.split('/')[-1]  # Extracting file name from URL
        with open(file_name, 'wb') as f:
            f.write(response.content)
        return file_name
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def upload_file(update: Update, file_path: str) -> None:
    """Upload the downloaded file to Telegram."""
    try:
        with open(file_path, 'rb') as f:
            update.message.reply_document(f)
        os.remove(file_path)  # Remove the file after uploading
    except Exception as e:
        update.message.reply_text(f"Error uploading {file_path}: {e}")

def process_links(links: list, update: Update) -> None:
    """Process each link for download and upload."""
    global is_running
    for link in links:
        if not is_running:
            break
        update.message.reply_text(f'Processing {link}...')
        
        # Download the file
        file_path = download_file(link)
        
        if file_path:
            # Upload the downloaded file
            upload_file(update, file_path)
    
    if is_running:
        update.message.reply_text('Batch upload completed.')

def batch(update: Update, context: CallbackContext) -> None:
    """Start batch upload process."""
    global is_running
    is_running = True
    update.message.reply_text('Starting batch upload...')
    
    # Start processing in a new thread to avoid blocking
    threading.Thread(target=process_links, args=(context.args, update)).start()

def stop(update: Update, context: CallbackContext) -> None:
    """Stop the ongoing process."""
    global is_running
    is_running = False
    update.message.reply_text('Stopping ongoing processes...')

def main() -> None:
    """Run the bot."""
    updater = Updater("7490926656:AAHG-oUUzGPony9xfyApSI0EbbymhneDU1k")

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("batch", batch))
    updater.dispatcher.add_handler(CommandHandler("stop", stop))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
