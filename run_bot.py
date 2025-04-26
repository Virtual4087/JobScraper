"""
Run script for LinkedIn Job Scraper
This script is optimized for Replit and ensures the application runs persistently
"""

import logging
import time
import threading
from keep_alive import keep_alive
from job_checker import start_job_checker, stop_job_checker
from app_state import update_state
from logger import setup_logger

# Set up logging
logger = setup_logger()
logger.setLevel(logging.INFO)

def main():
    """
    Main function to run the application
    This is the entry point for the Replit run button
    """
    logger.info("Starting LinkedIn Job Scraper in persistent mode")
    
    # Initialize application state
    update_state()
    
    # Start the web server for keep-alive pings
    # Note: keep_alive() already starts the job checker
    keep_alive_thread = keep_alive()
    logger.info("Keep-alive web server started")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        stop_job_checker()
    except Exception as e:
        logger.error(f"Error in main thread: {e}")
        stop_job_checker()
        raise

if __name__ == "__main__":
    main()