import threading
import time
import datetime
from logger import logger
from config import CHECK_INTERVAL, KEYWORDS
from linkedin_scraper import LinkedInScraper
from telegram_notifier import TelegramNotifier
from job_storage import JobStorage
from app_state import update_state

class JobChecker:
    """Class to periodically check for new jobs and send notifications"""
    
    def __init__(self):
        self.job_storage = JobStorage()
        self.linkedin_scraper = LinkedInScraper(self.job_storage)
        self.telegram_notifier = TelegramNotifier()
        self.running = False
        self.thread = None
    
    def check_jobs(self):
        """Check for new jobs for all keywords"""
        logger.info("Checking for new jobs...")
        all_new_jobs = []
        first_run = self.linkedin_scraper.first_run
        
        try:
            for keyword in KEYWORDS:
                try:
                    jobs = self.linkedin_scraper.get_jobs(keyword)
                    all_new_jobs.extend(jobs)
                    
                    if not first_run:
                        logger.info(f"Found {len(jobs)} new {keyword} jobs")
                except Exception as e:
                    logger.error(f"Error checking {keyword} jobs: {e}", exc_info=True)
                    # Continue with next keyword instead of stopping completely
                    continue
            
            # If this was the first run, reset the flag for future runs
            if first_run:
                self.linkedin_scraper.first_run = False
                logger.info("First run completed - future jobs will trigger notifications")
            
            # Save all seen jobs to storage after processing all keywords
            # This prevents duplicate notifications from race conditions
            try:
                self.job_storage._save_seen_jobs()
            except Exception as e:
                logger.error(f"Error saving seen jobs: {e}", exc_info=True)
                
            # Update the application state with job count and job data
            update_state(len(all_new_jobs), all_new_jobs)
            
            # Send notifications for new jobs
            notification_count = 0
            for job in all_new_jobs:
                try:
                    if self.telegram_notifier.send_message(job):
                        notification_count += 1
                        logger.info(f"Sent notification for {job['keyword']} job: {job['title']}")
                except Exception as e:
                    logger.error(f"Error sending notification for job {job.get('title', 'Unknown')}: {e}")
            
            logger.info(f"Sent {notification_count} notifications")
            return len(all_new_jobs)
            
        except Exception as e:
            logger.error(f"Critical error in job checking process: {e}", exc_info=True)
            # Still update the state to reflect the check was attempted
            update_state()
            return 0
    
    def job_check_loop(self):
        """Main loop to periodically check for jobs"""
        logger.info(f"Starting job check loop with interval of {CHECK_INTERVAL} seconds")
        
        while self.running:
            try:
                self.check_jobs()
            except Exception as e:
                logger.error(f"Error in job check loop: {e}")
            
            # Sleep until next check time
            logger.info(f"Next check in {CHECK_INTERVAL} seconds")
            
            # Use a loop with shorter sleeps to allow for cleaner shutdown
            sleep_interval = 5  # Sleep in 5-second chunks
            for _ in range(CHECK_INTERVAL // sleep_interval):
                if not self.running:
                    break
                time.sleep(sleep_interval)
            
            # Handle any remainder
            if self.running and CHECK_INTERVAL % sleep_interval > 0:
                time.sleep(CHECK_INTERVAL % sleep_interval)
    
    def start(self):
        """Start the job checking thread"""
        if self.thread and self.thread.is_alive():
            logger.warning("Job checker is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self.job_check_loop)
        self.thread.daemon = True  # Allow the program to exit even if this thread is running
        self.thread.start()
        logger.info("Job checker started")
    
    def stop(self):
        """Stop the job checking thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)  # Wait up to 10 seconds for the thread to finish
            logger.info("Job checker stopped")
    
    def send_test_message(self, chat_id=None):
        """Send a test message to verify Telegram integration"""
        from send_test_message import send_test_message, send_direct_message
        
        if chat_id:
            # Create a dummy message
            message = """🔔 <b>Test Message from LinkedIn Job Scraper</b>

This is a test notification from your LinkedIn Job Scraper. If you're receiving this message, your Telegram notifications are correctly configured!

<b>System Status:</b> Online
<b>Check Interval:</b> 5 minutes
<b>Monitored Keywords:</b> qa, java, python, javascript, remote

Thank you for using the LinkedIn Job Scraper!
"""
            return send_direct_message(chat_id, message)
        else:
            return send_test_message()

# Singleton instance
job_checker = JobChecker()

def start_job_checker():
    """Start the job checker (for use from other modules)"""
    job_checker.start()
    return job_checker

def stop_job_checker():
    """Stop the job checker (for use from other modules)"""
    job_checker.stop()

if __name__ == "__main__":
    # Running as a standalone script
    checker = start_job_checker()
    
    try:
        # If run directly, keep the main thread alive
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("Stopping job checker...")
        stop_job_checker()
        print("Job checker stopped")