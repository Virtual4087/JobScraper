import os
import sys
import logging
import traceback

# Configure logging to output to both console and file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("app_launcher")

try:
    logger.info("Starting application...")
    
    # Import the necessary modules for the application
    logger.info("Importing modules...")
    import flask
    import requests
    from bs4 import BeautifulSoup
    import telegram
    
    # Import local modules
    logger.info("Importing application modules...")
    import app_state
    import config
    import logger as app_logger
    import job_storage
    import linkedin_scraper
    import telegram_notifier
    
    # Import main module
    logger.info("Importing main application...")
    import main
    
    # Run the application
    logger.info("Running application...")
    
    # Use a function from main.py to run the application
    if __name__ == "__main__":
        logger.info("Starting Flask application...")
        main.app.run(host='0.0.0.0', port=8080, debug=True)
        
except Exception as e:
    logger.error(f"Error starting application: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)