#!/usr/bin/env python3
"""
Script to check for new Telegram users and send them welcome messages.
This can be set up to run on a schedule (e.g., every few minutes).
"""

import time
from logger import logger
from send_test_message import send_welcome_messages_to_new_users

if __name__ == "__main__":
    try:
        logger.info("Checking for new Telegram users...")
        send_welcome_messages_to_new_users()
        logger.info("Finished checking for new users")
    except Exception as e:
        logger.error(f"Error while checking for new users: {e}")