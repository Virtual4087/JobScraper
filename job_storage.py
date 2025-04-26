import os
import json
from config import STORAGE_FILE
from logger import logger

class JobStorage:
    """Class to manage seen jobs and prevent duplicate notifications"""
    
    def __init__(self, storage_file=STORAGE_FILE):
        self.storage_file = storage_file
        self.seen_jobs = set()
        self._load_seen_jobs()
    
    def _load_seen_jobs(self):
        """Load seen jobs from storage file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    self.seen_jobs = set(json.load(f))
                logger.info(f"Loaded {len(self.seen_jobs)} seen jobs from storage")
            else:
                logger.info("No existing job storage found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading seen jobs: {e}")
    
    def _save_seen_jobs(self):
        """Save seen jobs to storage file"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(list(self.seen_jobs), f)
            logger.debug(f"Saved {len(self.seen_jobs)} jobs to storage")
        except Exception as e:
            logger.error(f"Error saving seen jobs: {e}")
    
    def is_job_seen(self, job_id):
        """Check if a job has been seen before"""
        return job_id in self.seen_jobs
    
    def mark_job_seen(self, job_id):
        """Mark a job as seen"""
        if job_id not in self.seen_jobs:
            self.seen_jobs.add(job_id)
            # We'll save at the end of the job check cycle instead of after each job
            # This reduces file I/O and prevents race conditions
    
    def get_seen_count(self):
        """Return the number of seen jobs"""
        return len(self.seen_jobs)
    
    def clear_old_jobs(self, max_jobs=1000):
        """Clear out old jobs if we're storing too many"""
        if len(self.seen_jobs) > max_jobs:
            # Convert to list, sort by job ID (which often contains timestamps) and keep the newest
            jobs_list = list(self.seen_jobs)
            # Try to keep the newest jobs based on numeric sorting
            try:
                sorted_jobs = sorted(jobs_list, key=lambda x: int(x) if x.isdigit() else 0, reverse=True)
                self.seen_jobs = set(sorted_jobs[:max_jobs])
                self._save_seen_jobs()
                logger.info(f"Cleaned job storage, keeping {max_jobs} most recent jobs")
            except Exception as e:
                logger.error(f"Error cleaning job storage: {e}")
