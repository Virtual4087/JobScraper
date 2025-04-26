"""
Service script for LinkedIn Job Scraper
This script sets up the application to run continuously and restart if it crashes
"""

import os
import sys
import time
import signal
import logging
import subprocess
from logger import setup_logger

# Set up logging
logger = setup_logger()
logger.setLevel(logging.INFO)

def run_service():
    """Run the bot as a service with automatic restart"""
    logger.info("Starting LinkedIn Job Scraper service wrapper")
    
    # Handle termination signals
    def signal_handler(sig, frame):
        logger.info("Service received termination signal, shutting down")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    while True:
        try:
            logger.info("Starting LinkedIn Job Scraper process")
            # Start the main application process
            process = subprocess.Popen([sys.executable, "run_bot.py"])
            
            # Wait for the process to complete
            process.wait()
            
            # If we get here, the process has exited
            exit_code = process.returncode
            logger.warning(f"LinkedIn Job Scraper process exited with code {exit_code}")
            
            # If it was a clean exit (code 0), we can exit as well
            if exit_code == 0:
                logger.info("Clean exit detected, shutting down service")
                break
                
            # Otherwise wait a bit and restart
            logger.info("Restarting application in 10 seconds...")
            time.sleep(10)
            
        except Exception as e:
            logger.error(f"Error in service wrapper: {e}")
            logger.info("Restarting application in 30 seconds...")
            time.sleep(30)

if __name__ == "__main__":
    run_service()