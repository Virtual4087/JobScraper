#!/bin/bash
# Stop the LinkedIn job scraper
if [ -f bot.pid ]; then
  pid=$(cat bot.pid)
  if ps -p $pid > /dev/null; then
    echo "Stopping LinkedIn Job Scraper (PID: $pid)"
    kill $pid
    rm bot.pid
    echo "LinkedIn Job Scraper stopped"
  else
    echo "LinkedIn Job Scraper is not running (PID: $pid not found)"
    rm bot.pid
  fi
else
  echo "LinkedIn Job Scraper is not running (no PID file found)"
fi