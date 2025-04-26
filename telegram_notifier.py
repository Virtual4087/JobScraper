import requests
import time
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS
from logger import logger

class TelegramNotifier:
    """Class to send job notifications to Telegram"""
    
    def __init__(self):
        if not TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN is not set in environment variables")
        if not TELEGRAM_CHAT_IDS or TELEGRAM_CHAT_IDS == ['']:
            logger.error("TELEGRAM_CHAT_IDS is not set or is empty in environment variables")
    
    def format_job_message(self, job):
        """Format a job listing for Telegram message"""
        # Clean the title to handle any encoding issues
        clean_title = job['title'].encode('utf-16', 'surrogatepass').decode('utf-16', 'ignore')
        
        message = f"🚀 <b>New {job['keyword'].upper()} Job Posted</b>\n"
        message += f"<b>Title:</b> {clean_title}\n"
        message += f"<b>Company:</b> {job['company']}\n"
        message += f"<b>Location:</b> {job['location']}\n"
        message += f"<b>Link:</b> {job['link']}"
        
        return message
    
    def send_message(self, job):
        """Send a job notification to all configured Telegram chats"""
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_IDS or TELEGRAM_CHAT_IDS == ['']:
            logger.error("Telegram configuration is incomplete, cannot send message")
            return False
            
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        message = self.format_job_message(job)
        
        success_count = 0
        for chat_id in TELEGRAM_CHAT_IDS:
            if not chat_id:  # Skip empty chat IDs
                continue
                
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            try:
                response = requests.post(url, data=payload)
                
                if response.status_code == 200:
                    success_count += 1
                    logger.debug(f"Successfully sent notification to chat {chat_id}")
                else:
                    logger.error(f"Failed to send message to {chat_id}. Status code: {response.status_code}, Response: {response.text}")
                
                # Add a small delay between messages to avoid hitting rate limits
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Failed to send message to {chat_id}: {e}")
        
        return success_count > 0
