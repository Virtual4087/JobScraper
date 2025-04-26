#!/bin/bash
# Debug script for LinkedIn Job Scraper Bot

echo "Stopping any existing bot processes..."
pkill -f "python run_bot.py" || echo "No existing bot process found"

echo "Starting LinkedIn Job Scraper Bot in debug mode..."
python run_bot.py