#!/bin/bash
# Script to stop the LinkedIn Job Scraper

# Find and kill any running instances of the application
if pgrep -f "python run_bot.py" > /dev/null; then
    echo "Stopping LinkedIn Job Scraper..."
    pkill -f "python run_bot.py"
    
    # Give it a moment to shut down
    sleep 2
    
    # Check if it's still running
    if pgrep -f "python run_bot.py" > /dev/null; then
        echo "Warning: Application still running. Forcing termination..."
        pkill -9 -f "python run_bot.py"
    fi
    
    echo "LinkedIn Job Scraper stopped successfully."
else
    echo "LinkedIn Job Scraper is not currently running."
fi