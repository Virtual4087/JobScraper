
from keep_alive import keep_alive
import time
import requests
from bs4 import BeautifulSoup

TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
TELEGRAM_CHAT_IDS = ['5382256407', '482345057', '1477628874', '5804103490']
KEYWORDS = ['qa', 'java']
CHECK_INTERVAL = 600  # 10 minutes

seen_jobs = set()

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    for chat_id in TELEGRAM_CHAT_IDS:
        payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
        try:
            requests.post(url, data=payload)
        except Exception as e:
            print(f"Failed to send message to {chat_id}: {e}")

def get_latest_jobs(keyword):
    encoded_keyword = keyword.replace(' ', '%20')
    search_url = f'https://www.linkedin.com/jobs/search/?keywords={encoded_keyword}&location=United%20States&f_WT=2&f_TPR=r86400&sortBy=DD'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    jobs = []
    for job_card in soup.find_all('a', {'class': 'base-card__full-link'}):
        job_title = job_card.text.strip()
        job_link = job_card['href']
        job_id = job_link.split('/')[-1].split('?')[0]
        if job_id not in seen_jobs:
            seen_jobs.add(job_id)
            jobs.append((job_title, job_link, keyword))

    return jobs

keep_alive()

while True:
    print("Checking for new jobs...")
    all_new_jobs = []
    for keyword in KEYWORDS:
        all_new_jobs.extend(get_latest_jobs(keyword))

    for title, link, keyword in all_new_jobs:
        clean_title = title.encode('utf-16', 'surrogatepass').decode('utf-16', 'ignore')
        message = f"🚀 <b>New {keyword.upper()} Job Posted</b>\n<b>Title:</b> {clean_title}\n<b>Link:</b> {link}"
        send_telegram_message(message)
        print(f"Sent alert for {keyword} job: {clean_title}")

    time.sleep(CHECK_INTERVAL)
