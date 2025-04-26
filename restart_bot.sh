#!/bin/bash
# Restart script for LinkedIn Job Scraper Bot

echo "Stopping any existing bot processes..."
pkill -f "python run_bot.py" || echo "No existing bot process found"

echo "Starting LinkedIn Job Scraper Bot..."
nohup python run_bot.py > bot.log 2>&1 &

echo "Bot started with PID $!"
echo "Check bot.log for output"