import logging
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace these with your actual credentials
API_ID = "22420997"
API_HASH = "d7fbe2036e9ed2a1468fad5a5584a255"
BOT_TOKEN = "7513058089:AAHAPtJbHEPbRMbV8rv-gAZ8KVL0ykAM2pE"

# Function to handle errors
def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred. Please try again.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me a YouTube or XVideos link.")

async def get_formats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = context.args[0] if context.args else None
    if not url:
        await update.message.reply_text("Please provide a valid URL.")
        return

    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }],
        'progress_hooks': [progress_hook]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)

            # Check for video formats
            formats = info_dict.get('formats', [])
            if not formats:
                await update.message.reply_text("No formats found.")
                return

            # Create a message listing available formats
            format_messages = []
            for f in formats:
                if 'vcodec' in f and f['vcodec'] != 'none':
                    format_messages.append(f"Format: {f['format']} - Resolution: {f['height']}p - Codec: {f['vcodec']}")

            if format_messages:
                await update.message.reply_text("\n".join(format_messages))
            else:
                await update.message.reply_text("No valid video formats available.")

    except KeyError as e:
        logger.error(f"KeyError: {str(e)}")
        await update.message.reply_text("An error occurred while processing the URL.")
    except yt_dlp.utils.ExtractorError as e:
        logger.error(f"ExtractorError: {str(e)}")
        await update.message.reply_text(f"Failed to extract information from the video. Error: {str(e)}")
    except Exception as e:
        logger.error(f"General Error: {str(e)}")
        await update.message.reply_text("An unexpected error occurred. Please try again later.")

def progress_hook(d):
    if d['status'] == 'downloading':
        logger.info(f"Downloading: {d['filename']} - {d['_percent_str']}")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("get_formats", get_formats))
    application.add_error_handler(handle_error)

    application.run_polling()

if __name__ == "__main__":
    main()
