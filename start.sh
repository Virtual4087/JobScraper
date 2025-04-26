#!/bin/bash
# Script to start the LinkedIn Job Scraper in the background

# Check if the application is already running
if pgrep -f "python run_bot.py" > /dev/null; then
    echo "LinkedIn Job Scraper is already running."
    echo "Process ID: $(pgrep -f 'python run_bot.py')"
    exit 0
fi

# Start the application in the background
echo "Starting LinkedIn Job Scraper..."
nohup python run_bot.py > app.log 2>&1 &
PID=$!

# Sleep for a moment to ensure the process starts correctly
sleep 2

# Check if the process is still running
if ps -p $PID > /dev/null; then
    echo "LinkedIn Job Scraper started successfully."
    echo "Process ID: $PID"
    echo "View the web interface at: https://${REPL_SLUG}.${REPL_OWNER}.repl.co"
    echo "Logs are being saved to: app.log"
else
    echo "Failed to start LinkedIn Job Scraper. Check app.log for details."
fi