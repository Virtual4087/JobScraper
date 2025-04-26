"""
Main application for the LinkedIn Job Scraper
This is a permanent, standalone application that:
1. Checks LinkedIn for new jobs matching configured keywords
2. Sends notifications via Telegram when new jobs are found
3. Provides a web interface to monitor status and configuration
"""

import os
import datetime
import time
from flask import jsonify, render_template
from keep_alive import app, keep_alive
from app_state import app_state, update_state
from config import CHECK_INTERVAL, KEYWORDS, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS
from logger import logger

@app.route('/api/telegram-status')
def telegram_status():
    """Check Telegram configuration status"""
    return jsonify({
        "configured": bool(TELEGRAM_BOT_TOKEN),
        "chat_ids": len(TELEGRAM_CHAT_IDS),
        "status": "Ready" if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_IDS else "Not Configured"
    })

def main():
    """
    Main function to run the application permanently
    """
    logger.info("Starting LinkedIn Job Scraper")
    
    # Initialize app state
    if not app_state.get("start_time"):
        app_state["start_time"] = datetime.datetime.now()
    
    # Start the keep-alive web server
    keep_alive()
    
    # Print deployment information
    logger.info("=============================================================")
    logger.info("LinkedIn Job Scraper is running")
    logger.info("The web interface is available at http://localhost:8080")
    logger.info("The application will continue running in the background")
    logger.info("=============================================================")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Error in main thread: {e}")
        raise

if __name__ == "__main__":
    main()