from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime

class DiceScraper:
    def __init__(self, job_storage):
        self.job_storage = job_storage
        self.first_run = True
    
    def build_dice_url(self, keyword, location, page=1):
        return (
            f"https://www.dice.com/jobs?"
            f"q={keyword}"
            f"&location={location}"
            f"&countryCode=US"
            f"&radius=30"
            f"&radiusUnit=mi"
            f"&page={page}"
            f"&pageSize=40"
            f"&filters.postedDate=ONE"
            f"&language=en"
        )


    def get_jobs(self, keyword, location, max_results=20):
        jobs = []

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        service = Service(ChromeDriverManager().install())
        with webdriver.Chrome(service=service, options=chrome_options) as driver:
            print(f"{keyword}")
            url = self.build_dice_url(keyword, location)
            print(f"[INFO] Scraping Dice URL: {url}")
            driver.get(url)
            time.sleep(20)  # Let the page load fully
            job_cards = driver.find_elements(By.CSS_SELECTOR, "dhi-search-card")
            print(f"Found {len(job_cards)} job cards on page.")  # Debug output

            for idx, card in enumerate(job_cards[:max_results]):
                try:
                    # print(f"\n--- Card {idx+1} ---")
                    # print(card.text)
                    # print("-------------------\n")

                    lines = card.text.strip().split("\n")
                    print(f"Title: {lines[0]}")
                    print(f"Company: {lines[1]}")
                    print(f"Location: {lines[2]}")

                    title = lines[0] if len(lines) > 0 else "Unknown Title"
                    company = lines[1] if len(lines) > 1 else "Unknown Company"
                    location = lines[2] if len(lines) > 2 else "Remote"

                    # Skip if not enough info
                    if not title or not company:
                        continue

                    try:
                        job_id = card.get_attribute('data-cy-value')
                        if job_id:
                            link = f"https://www.dice.com/job-detail/{job_id}"
                        else:
                            link = "https://www.dice.com"
                    except:
                        link = "https://www.dice.com"

                    print(f"Job Link {link}")
                    # Note: no direct clickable link available, maybe build it manually later

                    job_id = str(hash(title + company + location))
                    job_signature = f"{job_id}_{keyword}_dice"

                    if self.job_storage.is_job_seen(job_signature):
                        continue

                    self.job_storage.mark_job_seen(job_signature)

                    if self.first_run:
                        continue
                    
                    print("appending")
                    jobs.append({
                        'id': job_id,
                        'signature': job_signature,
                        'title': title,
                        'company': company,
                        'location': location,
                        'link': link,
                        'posted_time': "Recently",
                        'keyword': keyword,
                        'timestamp': datetime.datetime.now(),
                        'source': "Dice"
                    })

                except Exception as e:
                    print(f"Error parsing job card: {e}")


        if self.first_run:
            print(f"First run: Marked {len(jobs)} Dice {keyword} jobs as seen")
            return []
        else:
            print(f"Found {len(jobs)} new Dice {keyword} jobs")
            return jobs
