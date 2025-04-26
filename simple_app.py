import os
import time
import threading
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_IDS = os.environ.get('TELEGRAM_CHAT_IDS', '').split(',') if os.environ.get('TELEGRAM_CHAT_IDS') else []
KEYWORDS = ['qa', 'java']
CHECK_INTERVAL = 300  # 5 minutes

# Global state
app_state = {
    "start_time": datetime.now(),
    "job_count": 0,
    "last_check": None,
    "seen_jobs": set(),
    "new_jobs_found": 0
}

# Create Flask app
app = Flask(__name__)

def send_telegram_message(message):
    """Send a message to all configured Telegram chat IDs"""
    if not TELEGRAM_BOT_TOKEN:
        print("Telegram bot token not configured. Cannot send message.")
        return False
    
    success = True
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    for chat_id in TELEGRAM_CHAT_IDS:
        payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
        try:
            response = requests.post(url, data=payload)
            if not response.json().get('ok'):
                print(f"Failed to send message to {chat_id}: {response.json()}")
                success = False
        except Exception as e:
            print(f"Error sending message to {chat_id}: {e}")
            success = False
    
    return success

def get_latest_jobs(keyword):
    """Get the latest jobs for a keyword from LinkedIn"""
    encoded_keyword = keyword.replace(' ', '%20')
    search_url = f'https://www.linkedin.com/jobs/search/?keywords={encoded_keyword}&location=United%20States&f_WT=2&f_TPR=r86400&sortBy=DD'
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        jobs = []
        for job_card in soup.find_all('a', {'class': 'base-card__full-link'}):
            job_title = job_card.text.strip()
            job_link = job_card['href']
            job_id = job_link.split('/')[-1].split('?')[0]
            
            if job_id not in app_state["seen_jobs"]:
                app_state["seen_jobs"].add(job_id)
                jobs.append({
                    "id": job_id,
                    "title": job_title,
                    "link": job_link,
                    "keyword": keyword,
                    "found_at": datetime.now().isoformat()
                })
        
        print(f"Found {len(jobs)} new jobs for keyword '{keyword}'")
        return jobs
    
    except Exception as e:
        print(f"Error scraping jobs for '{keyword}': {e}")
        return []

def check_jobs():
    """Check for new jobs across all keywords"""
    print(f"Checking for new jobs at {datetime.now().isoformat()}...")
    app_state["last_check"] = datetime.now()
    
    all_new_jobs = []
    for keyword in KEYWORDS:
        new_jobs = get_latest_jobs(keyword)
        all_new_jobs.extend(new_jobs)
    
    # Don't send notifications on first run to avoid spamming
    if app_state["job_count"] > 0:
        for job in all_new_jobs:
            clean_title = job["title"].encode('utf-16', 'surrogatepass').decode('utf-16', 'ignore')
            message = f"🚀 <b>New {job['keyword'].upper()} Job Posted</b>\n<b>Title:</b> {clean_title}\n<b>Link:</b> {job['link']}"
            send_telegram_message(message)
            print(f"Sent alert for {job['keyword']} job: {clean_title}")
    else:
        print(f"First run, marked {len(all_new_jobs)} jobs as seen without sending notifications")
    
    app_state["job_count"] += len(all_new_jobs)
    app_state["new_jobs_found"] = len(all_new_jobs)
    
    return all_new_jobs

def job_check_loop():
    """Main loop to periodically check for jobs"""
    while True:
        try:
            check_jobs()
        except Exception as e:
            print(f"Error in job checking: {e}")
        
        # Sleep until the next check
        time.sleep(CHECK_INTERVAL)

# Flask routes
@app.route('/')
def home():
    """Display application status and configuration"""
    uptime = datetime.now() - app_state["start_time"]
    uptime_str = f"{uptime.days} days, {uptime.seconds // 3600} hours, {(uptime.seconds // 60) % 60} minutes"
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>LinkedIn Job Scraper</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { padding: 20px; }
            .status-card { margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="mb-4">LinkedIn Job Scraper</h1>
            
            <div class="card status-card">
                <div class="card-header bg-primary text-white">
                    Status
                </div>
                <div class="card-body">
                    <p><strong>Bot Status:</strong> <span class="badge bg-success">Running</span></p>
                    <p><strong>Uptime:</strong> {{ uptime }}</p>
                    <p><strong>Last Check:</strong> {{ last_check }}</p>
                    <p><strong>Total Jobs Found:</strong> {{ job_count }}</p>
                    <p><strong>New Jobs (Last Check):</strong> {{ new_jobs_found }}</p>
                </div>
            </div>
            
            <div class="card status-card">
                <div class="card-header bg-primary text-white">
                    Configuration
                </div>
                <div class="card-body">
                    <p><strong>Telegram Bot:</strong> 
                        {% if telegram_configured %}
                        <span class="badge bg-success">Configured</span>
                        {% else %}
                        <span class="badge bg-danger">Not Configured</span>
                        {% endif %}
                    </p>
                    <p><strong>Chat IDs:</strong> {{ chat_ids }}</p>
                    <p><strong>Keywords:</strong> {{ keywords|join(', ') }}</p>
                    <p><strong>Check Interval:</strong> {{ check_interval // 60 }} minutes</p>
                </div>
            </div>
            
            <div class="mt-4">
                <a href="/send-test" class="btn btn-primary">Send Test Message</a>
            </div>
        </div>
    </body>
    </html>
    """, 
    uptime=uptime_str,
    last_check=app_state["last_check"].isoformat() if app_state["last_check"] else "Never",
    job_count=app_state["job_count"],
    new_jobs_found=app_state["new_jobs_found"],
    telegram_configured=bool(TELEGRAM_BOT_TOKEN),
    chat_ids=TELEGRAM_CHAT_IDS if TELEGRAM_CHAT_IDS else "None configured",
    keywords=KEYWORDS,
    check_interval=CHECK_INTERVAL
    )

@app.route('/send-test')
def send_test():
    """Send a test message to all Telegram users"""
    if not TELEGRAM_BOT_TOKEN:
        return jsonify({
            "success": False,
            "message": "Telegram bot token not configured"
        })
    
    message = "🧪 <b>Test Message</b>\n\nThis is a test message from your LinkedIn Job Scraper bot. If you're seeing this, your notifications are working correctly! 👍"
    success = send_telegram_message(message)
    
    return jsonify({
        "success": success,
        "message": "Test message sent successfully" if success else "Failed to send test message"
    })

@app.route('/ping')
def ping():
    """Simple endpoint for uptime monitoring services to ping"""
    # Calculate uptime
    uptime = datetime.now() - app_state["start_time"]
    uptime_str = f"{uptime.days} days, {uptime.seconds // 3600} hours, {(uptime.seconds // 60) % 60} minutes"
    
    # Update the status with the ping time
    app_state["last_ping"] = datetime.now()
    app_state["ping_count"] = app_state.get("ping_count", 0) + 1
    
    # Return a simple response with some basic status info
    return f"OK - Up for {uptime_str} - Last check: {app_state['last_check'].isoformat() if app_state['last_check'] else 'Never'} - Ping count: {app_state.get('ping_count', 0)}", 200

def render_template_string(template_string, **context):
    """Simple template renderer as a placeholder for Flask's render_template_string"""
    # This is a very basic implementation
    result = template_string
    for key, value in context.items():
        placeholder = "{{ " + key + " }}"
        if isinstance(value, list):
            result = result.replace("{{ " + key + "|join(', ') }}", ", ".join(value))
        elif value is None:
            result = result.replace(placeholder, "None")
        else:
            result = result.replace(placeholder, str(value))
    
    # Handle simple conditionals
    lines = result.split('\n')
    output_lines = []
    skip_until_endblock = False
    skip_until_else = False
    for line in lines:
        if "{% if " in line:
            condition = line.split("{% if ")[1].split(" %}")[0]
            condition_value = False
            
            for key, value in context.items():
                if key in condition:
                    if "not " + key in condition:
                        condition_value = not value
                    else:
                        condition_value = bool(value)
            
            if condition_value:
                skip_until_else = False
                skip_until_endblock = False
            else:
                skip_until_else = True
                skip_until_endblock = True
            continue
        
        if "{% else %}" in line:
            skip_until_else = not skip_until_else
            skip_until_endblock = not skip_until_endblock
            continue
        
        if "{% endif %}" in line:
            skip_until_else = False
            skip_until_endblock = False
            continue
        
        if skip_until_else or skip_until_endblock:
            continue
        
        output_lines.append(line)
    
    return '\n'.join(output_lines)

def start_job_checker():
    """Start the job checking thread"""
    thread = threading.Thread(target=job_check_loop)
    thread.daemon = True
    thread.start()
    return thread

if __name__ == "__main__":
    # Start the job checker in a background thread
    check_jobs()  # Run once immediately to mark existing jobs
    start_job_checker()
    
    # Start the Flask server
    app.run(host='0.0.0.0', port=5000, debug=True)