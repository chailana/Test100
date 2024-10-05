#!/bin/bash

# Start Gunicorn in the background
gunicorn app:app --bind 0.0.0.0:8000 &

# Wait for Gunicorn to start
sleep 3

# Start the bot
python3 bot.py
