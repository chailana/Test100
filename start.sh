#!/bin/bash

# Start Gunicorn for the Flask app
gunicorn app:app &

# Start the Telegram bot
python3 bot.py
