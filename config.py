import os
import logging

# Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_IDS = os.getenv('TELEGRAM_CHAT_IDS', '').split(',')

# Job Search Configuration
KEYWORDS = os.getenv('KEYWORDS', 'qa,java').split(',')
LOCATION = os.getenv('LOCATION', 'United States')
REMOTE_ONLY = os.getenv('REMOTE_ONLY', 'true').lower() == 'true'
DAYS_RECENT = int(os.getenv('DAYS_RECENT', '1'))  # Jobs posted in last X days

# Time intervals
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))  # 5 minutes between checks

# LinkedIn search parameters
LINKEDIN_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Seen jobs storage
STORAGE_FILE = os.getenv('STORAGE_FILE', 'seen_jobs.txt')

# Application settings
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
LOG_LEVEL = logging.DEBUG if DEBUG_MODE else logging.INFO
