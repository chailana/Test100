from telethon import TelegramClient, events
import asyncio

# Replace with your API ID and API Hash
API_ID = 'YOUR_API_ID'  
API_HASH = 'YOUR_API_HASH'  
BOT_TOKEN = 'YOUR_BOT_TOKEN'  # Replace with your Bot Token

# Initialize the client with the bot token
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.respond("Hello! I'm your forwarding bot. Use /batch to forward messages.")

@client.on(events.NewMessage)
async def handler(event):
    # Check if the message is from a private chat or a group/channel
    if event.is_private or event.chat.type in ['group', 'supergroup']:
        await event.forward_to('target_chat')  # Replace 'target_chat' with your target chat ID or username

async def forward_batch_messages(start_id, end_id, source_chat):
    for message_id in range(start_id, end_id + 1):
        try:
            message = await client.get_messages(source_chat, ids=message_id)
            await message.forward_to('target_chat')  # Forwarding to target chat
            print(f"Forwarded message ID {message_id}")
        except Exception as e:
            print(f"Error forwarding message ID {message_id}: {e}")

@client.on(events.NewMessage(pattern='/batch'))
async def batch_handler(event):
    # Example command: /batch 1-10 source_chat
    command = event.raw_text.split()
    if len(command) != 3:
        await event.respond("Usage: /batch start-end source_chat")
        return
    
    try:
        start_end = command[1].split('-')
        start_id = int(start_end[0])
        end_id = int(start_end[1])
        source_chat = command[2]
        
        await forward_batch_messages(start_id, end_id, source_chat)
    except ValueError:
        await event.respond("Invalid ID range. Please use integers.")

async def main():
    print('Bot is running...')
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
