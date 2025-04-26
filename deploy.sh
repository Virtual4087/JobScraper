#!/bin/bash
# Deploy script to run the LinkedIn Job Scraper permanently

# Kill any existing processes
pkill -f "python run_bot.py" || true

# Start the application in the background 
nohup python run_bot.py > app.log 2>&1 &

echo "Application started in the background. Check app.log for details."
echo "Process ID: $!"