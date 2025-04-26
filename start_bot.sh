#!/bin/bash
# Start the LinkedIn job scraper in the background
nohup python run_bot.py > bot.log 2>&1 &
echo $! > bot.pid
echo "LinkedIn Job Scraper started with PID $(cat bot.pid)"
echo "Log file: bot.log"