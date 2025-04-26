#!/usr/bin/env python3
"""
Service wrapper for LinkedIn Job Scraper
This script creates a simple service that runs the bot and monitors it
"""

import logging
import os
import signal
import subprocess
import sys
import time
from logger import setup_logger

# Set up logging
logger = setup_logger()

def write_pid_file():
    """Write the current PID to a file for monitoring"""
    pid = os.getpid()
    with open("service.pid", "w") as f:
        f.write(str(pid))
    logger.info(f"Service started with PID {pid}")

def run_service():
    """Run the bot as a service with automatic restart"""
    # Handle termination signals gracefully
    def signal_handler(sig, frame):
        logger.info(f"Service received signal {sig}, shutting down...")
        if bot_process:
            logger.info(f"Terminating bot process {bot_process.pid}")
            bot_process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Write PID file
    write_pid_file()
    
    # Run the bot in a loop
    bot_process = None
    consecutive_failures = 0
    
    logger.info("Starting LinkedIn Job Scraper service")
    
    while True:
        try:
            # Start the bot process
            logger.info("Starting LinkedIn Job Scraper process")
            bot_process = subprocess.Popen([sys.executable, "run_bot.py"])
            
            # Wait for the process to exit
            exit_code = bot_process.wait()
            
            # Check if the process exited normally
            if exit_code == 0:
                logger.info("LinkedIn Job Scraper process exited normally")
                consecutive_failures = 0
            else:
                logger.warning(f"LinkedIn Job Scraper process exited with code {exit_code}")
                consecutive_failures += 1
                
            # Delay before restarting to prevent rapid restarts
            if consecutive_failures >= 3:
                logger.error(f"LinkedIn Job Scraper failed {consecutive_failures} times in a row, waiting 60 seconds before restarting")
                time.sleep(60)
            else:
                logger.info("Waiting 5 seconds before restarting LinkedIn Job Scraper")
                time.sleep(5)
                
        except Exception as e:
            logger.error(f"Error running LinkedIn Job Scraper: {e}")
            consecutive_failures += 1
            time.sleep(10)

if __name__ == "__main__":
    run_service()