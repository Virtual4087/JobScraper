#!/bin/bash

# This script runs the LinkedIn Job Scraper in a continuous loop
# It will restart the application if it crashes

echo "Starting LinkedIn Job Scraper in persistent mode..."

# Keep track of crashes to avoid restarting too frequently
CRASH_COUNT=0
MAX_CRASHES=5
CRASH_TIMEOUT=300 # 5 minutes

while true; do
  echo "Starting bot process..."
  
  # Run the bot
  python run_bot.py
  
  # Check exit code
  EXIT_CODE=$?
  
  if [ $EXIT_CODE -eq 0 ]; then
    echo "Bot exited cleanly, shutting down."
    break
  else
    echo "Bot crashed with exit code $EXIT_CODE"
    CRASH_COUNT=$((CRASH_COUNT + 1))
    
    if [ $CRASH_COUNT -ge $MAX_CRASHES ]; then
      echo "Too many crashes ($CRASH_COUNT), waiting for $CRASH_TIMEOUT seconds before continuing..."
      sleep $CRASH_TIMEOUT
      CRASH_COUNT=0
    else
      echo "Restarting in 10 seconds..."
      sleep 10
    fi
  fi
done