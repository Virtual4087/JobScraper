import datetime
from config import CHECK_INTERVAL
import logging
from collections import defaultdict

# Global state to track application status
app_state = {
    "running": True,
    "last_check": None,
    "jobs_found": 0,
    "start_time": datetime.datetime.now(),
    "next_check": None,
    "recent_jobs": [],  # List of recently found jobs (most recent first)
    "keyword_stats": defaultdict(int),  # Count of jobs by keyword
    "company_stats": defaultdict(int),  # Count of jobs by company
    "location_stats": defaultdict(int),  # Count of jobs by location
    "location":"",
    "keywords":""
}

# Maximum number of recent jobs to store
MAX_RECENT_JOBS = 100

def update_state(jobs_found=None, new_jobs=None):
    """Update the application state
    
    Args:
        jobs_found (int): Number of new jobs found in this check
        new_jobs (list): List of job dictionaries found in this check
    """
    if jobs_found is not None:
        app_state["jobs_found"] += jobs_found
    
    # Update timestamp info
    app_state["last_check"] = datetime.datetime.now()
    app_state["next_check"] = datetime.datetime.now() + datetime.timedelta(seconds=CHECK_INTERVAL)
    
    # Store recent jobs data if provided
    if new_jobs:
        # Add the new jobs to the beginning of the list (newest first)
        app_state["recent_jobs"] = new_jobs + app_state["recent_jobs"]
        
        # Trim the list if it gets too long
        if len(app_state["recent_jobs"]) > MAX_RECENT_JOBS:
            app_state["recent_jobs"] = app_state["recent_jobs"][:MAX_RECENT_JOBS]
        
        # Update statistics
        for job in new_jobs:
            try:
                # Update keyword stats
                keyword = job.get('keyword', 'unknown')
                app_state["keyword_stats"][keyword] += 1
                
                # Update company stats
                company = job.get('company', 'Unknown Company')
                app_state["company_stats"][company] += 1
                
                # Update location stats
                location = job.get('location', 'Unknown Location')
                app_state["location_stats"][location] += 1
            except Exception as e:
                logging.error(f"Error updating job statistics: {e}")