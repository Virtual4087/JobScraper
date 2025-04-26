"""
Service wrapper for LinkedIn Job Scraper
This script creates a simple service that restarts if it crashes
"""

import logging
import time
import subprocess
import os
import signal
import sys
from logger import setup_logger

# Set up logging
logger = setup_logger()
logger.setLevel(logging.INFO)

def write_pid_file():
    """Write the current PID to a file for monitoring"""
    with open('app.pid', 'w') as f:
        f.write(str(os.getpid()))
    logger.info(f"Service PID written to app.pid: {os.getpid()}")

def run_service():
    """Run the bot as a service with automatic restart"""
    write_pid_file()
    
    logger.info("Starting LinkedIn Job Scraper Service")
    
    # Function to handle signals
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down")
        if bot_process and bot_process.poll() is None:
            logger.info("Terminating bot process")
            try:
                bot_process.terminate()
                bot_process.wait(timeout=5)
            except Exception as e:
                logger.error(f"Error terminating bot process: {e}")
                try:
                    bot_process.kill()
                except:
                    pass
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    restart_count = 0
    bot_process = None
    
    while True:
        try:
            if bot_process and bot_process.poll() is None:
                # Process is still running
                time.sleep(10)
                continue
                
            # Start or restart the bot process
            logger.info(f"Starting bot process (restart count: {restart_count})")
            bot_process = subprocess.Popen(
                ["python", "run_bot.py"],
                stdout=open("app.log", "a"),
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid
            )
            
            # Wait for a while to see if it crashes immediately
            time.sleep(5)
            
            if bot_process.poll() is not None:
                # Process ended quickly, might indicate an error
                returncode = bot_process.returncode
                logger.error(f"Bot process exited quickly with code {returncode}")
                
                # Increase restart count and delay longer if we're having issues
                restart_count += 1
                if restart_count > 5:
                    logger.error("Too many restart attempts, waiting longer")
                    time.sleep(60)  # Wait a minute before trying again
                else:
                    time.sleep(5)
            else:
                # Process is running, reset restart count
                restart_count = 0
                
                # Monitor the process
                while bot_process.poll() is None:
                    time.sleep(10)
                
                # Process ended, log the exit code
                returncode = bot_process.returncode
                logger.info(f"Bot process exited with code {returncode}")
                
        except Exception as e:
            logger.error(f"Error in service loop: {e}")
            time.sleep(10)  # Wait before trying again

if __name__ == "__main__":
    run_service()