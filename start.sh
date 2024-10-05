#!/bin/bash

# Start Gunicorn and log output
gunicorn app:app --bind 0.0.0.0:8000 > gunicorn.log 2>&1 &

# Start the bot and log output
python3 bot.py > bot.log 2>&1
