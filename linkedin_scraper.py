import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import quote
from config import LINKEDIN_HEADERS, REMOTE_ONLY, DAYS_RECENT, LOCATION
from logger import logger

class LinkedInScraper:
    """Class to scrape LinkedIn job listings"""
    
    def __init__(self, job_storage):
        self.job_storage = job_storage
        self.first_run = True  # Flag to track first run
    
    def _build_search_url(self, keyword, location):
        """Build LinkedIn job search URL with parameters"""
        # URL encode the keyword
        encoded_keyword = quote(keyword)
        encoded_location = quote(location)
        
        # Base URL
        url = f'https://www.linkedin.com/jobs/search/?keywords={encoded_keyword}&location={encoded_location}'
        
        # Add remote work filter if enabled
        if REMOTE_ONLY:
            url += '&f_WT=2'
        
        # Add time filter based on configuration
        if DAYS_RECENT == 1:
            url += '&f_TPR=r86400'  # Last 24 hours
        elif DAYS_RECENT == 7:
            url += '&f_TPR=r604800'  # Last 7 days
        elif DAYS_RECENT == 30:
            url += '&f_TPR=r2592000'  # Last month
        
        # Sort by most recent
        url += '&sortBy=DD'
        
        return url
    
    def get_jobs(self, keyword, location):
        """Scrape LinkedIn for jobs matching the keyword"""
        search_url = self._build_search_url(keyword, location)
        logger.debug(f"Searching LinkedIn: {search_url}")
        
        try:
            # Add a small random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            # Request the search page
            response = requests.get(search_url, headers=LINKEDIN_HEADERS)
            
            if response.status_code != 200:
                logger.error(f"LinkedIn returned status code {response.status_code}")
                return []
                
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find job listings
            jobs = []
            marked_job_count = 0
            
            # Track job IDs we've already processed in this batch to avoid duplicates
            batch_job_ids = set()
            
            for job_card in soup.find_all('div', {'class': 'base-card'}):
                try:
                    # Find job title link
                    job_link_elem = job_card.find('a', {'class': 'base-card__full-link'})
                    if not job_link_elem:
                        continue
                        
                    job_link = job_link_elem['href'].split('?')[0]  # Remove query parameters
                    job_title = job_link_elem.text.strip()
                    
                    # Extract job ID from the URL - make sure to normalize the ID
                    job_id = job_link.split('/')[-1].strip()
                    
                    # Create a unique job signature for this job and keyword
                    # This prevents the same job from showing up for different keywords
                    job_signature = f"{job_id}_{keyword}"
                    
                    # Skip if we've seen this job before in storage
                    if self.job_storage.is_job_seen(job_signature):
                        logger.debug(f"Skipping already seen job: {job_signature}")
                        continue
                        
                    # Skip if we've already processed this job ID in this batch
                    if job_signature in batch_job_ids:
                        logger.debug(f"Skipping duplicate job ID in current batch: {job_signature}")
                        continue
                    
                    # Add to current batch tracking
                    batch_job_ids.add(job_signature)
                    
                    # Try to get company name
                    company_elem = job_card.find('span', {'class': 'base-search-card__subtitle'})
                    company = company_elem.text.strip() if company_elem else "Unknown Company"
                    
                    # Try to get location
                    location_elem = job_card.find('span', {'class': 'job-search-card__location'})
                    location = location_elem.text.strip() if location_elem else "Remote"
                    
                    # Get posting time
                    time_elem = job_card.find('time', {'class': 'job-search-card__listdate'})
                    if time_elem and 'datetime' in time_elem.attrs:
                        posted_time = time_elem['datetime']
                    else:
                        posted_time = "Recently"
                    
                    # Mark the job as seen using the job signature
                    self.job_storage.mark_job_seen(job_signature)
                    marked_job_count += 1
                    
                    # On first run, we just mark jobs as seen without returning them
                    # This prevents notifications for existing jobs when the app first starts
                    if self.first_run:
                        continue
                    
                    # Add job to results with current timestamp
                    import datetime
                    jobs.append({
                        'id': job_id,
                        'signature': job_signature,
                        'title': job_title,
                        'company': company,
                        'location': location,
                        'link': job_link,
                        'posted_time': posted_time,
                        'keyword': keyword,
                        'timestamp': datetime.datetime.now(),
                        'source':"LinkedIn"
                    })
                    
                except Exception as e:
                    logger.error(f"Error parsing job card: {e}")
            
            if self.first_run:
                logger.info(f"First run: Marked {marked_job_count} existing {keyword} jobs as seen (no notifications sent)")
                # We'll reset first_run flag in the JobChecker after all keywords have been processed
                return []  # Return empty list on first run
            else:
                logger.info(f"Found {len(jobs)} new {keyword} jobs")
                return jobs
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
            return []
