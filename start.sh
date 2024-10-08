#!/bin/bash

# Start the HTTP server in the background on port 8000
python3 app.py &

# Start the Telegram bot
python3 bot.py
