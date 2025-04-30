from playwright.sync_api import sync_playwright
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

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            url = self.build_dice_url(keyword, location)
            print(f"[INFO] Scraping Dice URL: {url}")
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)

            job_cards = page.query_selector_all("dhi-search-card")
            print(f"Found {len(job_cards)} job cards on page.")

            for card in job_cards[:max_results]:
                try:
                    lines = card.inner_text().split("\n")
                    title = lines[0].strip()
                    company = lines[1].strip()
                    location = lines[2].strip()

                    job_id = card.get_attribute("data-cy-value")
                    link = f"https://www.dice.com/job-detail/{job_id}" if job_id else "https://www.dice.com"

                    job_signature = f"{job_id}_{keyword}_dice"

                    if self.job_storage.is_job_seen(job_signature):
                        continue

                    self.job_storage.mark_job_seen(job_signature)

                    if self.first_run:
                        continue

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
                    print(f"Error parsing card: {e}")

            browser.close()

        if self.first_run:
            print(f"First run: Marked {len(jobs)} Dice {keyword} jobs as seen")
            return []
        else:
            print(f"Found {len(jobs)} new Dice {keyword} jobs")
            return jobs
