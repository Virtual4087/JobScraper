import threading
import time
import datetime
from logger import logger
from config import CHECK_INTERVAL, KEYWORDS, LOCATION
from linkedin_scraper import LinkedInScraper
from dice_scraper import DiceScraper  
#from telegram_notifier import TelegramNotifier
from job_storage import JobStorage
from app_state import update_state

class JobChecker:
    """Class to periodically check for new jobs and send notifications"""
    
    def __init__(self, keywords=None, location=None):
        self.keywords = keywords or KEYWORDS
        self.location = location or LOCATION
        self.job_storage = JobStorage()
        self.linkedin_scraper = LinkedInScraper(self.job_storage)
        self.dice_scraper = DiceScraper(self.job_storage)
        # self.telegram_notifier = TelegramNotifier()
        self.running = False
        self.thread = None
    
    def check_jobs(self):
        """Check for new jobs for all keywords"""
        logger.info("Checking for new jobs...")
        all_new_jobs = []
        first_run = self.linkedin_scraper.first_run
        
        try:
            for keyword in self.keywords:
                try:
                    linkedin_jobs = []  # if not scraping LinkedIn now
                    dice_jobs = self.dice_scraper.get_jobs(keyword, self.location)

                    all_new_jobs.extend(dice_jobs)
                    
                    if not first_run:
                        logger.info(f"Found {len(linkedin_jobs)} LinkedIn and {len(dice_jobs)} Dice jobs for keyword {keyword} jobs")
                except Exception as e:
                    logger.error(f"Error checking {keyword} jobs: {e}", exc_info=True)
                    continue
            
            if first_run:
                self.linkedin_scraper.first_run = False
                self.dice_scraper.first_run = False
                logger.info("First run completed - future jobs will trigger notifications")
            else:
                try:
                    self.job_storage._save_seen_jobs()
                except Exception as e:
                    logger.error(f"Error saving seen jobs: {e}", exc_info=True)
                    
                update_state(len(all_new_jobs), all_new_jobs)
            return len(all_new_jobs)
            
        except Exception as e:
            logger.error(f"Critical error in job checking process: {e}", exc_info=True)
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
            
            logger.info(f"Next check in {CHECK_INTERVAL} seconds")
            
            sleep_interval = 5
            for _ in range(CHECK_INTERVAL // sleep_interval):
                if not self.running:
                    break
                time.sleep(sleep_interval)
            
            if self.running and CHECK_INTERVAL % sleep_interval > 0:
                time.sleep(CHECK_INTERVAL % sleep_interval)
    
    def start(self):
        """Start the job checking thread"""
        if self.thread and self.thread.is_alive():
            logger.warning("Job checker is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self.job_check_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Job checker started")
    
    def stop(self):
        """Stop the job checking thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
            logger.info("Job checker stopped")
