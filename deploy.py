"""
Deploy script for running the LinkedIn Job Scraper permanently
This script starts the application and keeps it running indefinitely
"""

import os
import time
import logging
from logger import setup_logger
from job_checker import start_job_checker, stop_job_checker
from app_state import update_state

# Set up logging
logger = setup_logger()
logger.setLevel(logging.INFO)

def main():
    """
    Main function to run the application permanently
    """
    logger.info("Starting LinkedIn Job Scraper in deployment mode")
    
    # Initialize application state
    update_state()
    
    # Start the job checker
    job_checker = start_job_checker()
    logger.info("Job checker started in deployment mode")
    
    # Keep the main thread alive
    try:
        logger.info("Application is now running permanently")
        logger.info("Configure Uptime Robot to ping /ping every 5 minutes to keep the application alive")
        
        # Print deployment information
        logger.info("=============================================================")
        logger.info("DEPLOYMENT INSTRUCTIONS:")
        logger.info("1. Click the 'Deploy' button in Replit to get a permanent URL")
        logger.info("2. Set up Uptime Robot to ping your-url.replit.app/ping every 5 minutes")
        logger.info("3. Your app will continue checking for jobs and sending notifications")
        logger.info("   even when you close your browser")
        logger.info("=============================================================")
        
        while True:
            # Sleep to keep the main thread alive
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