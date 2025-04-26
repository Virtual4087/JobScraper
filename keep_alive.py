from flask import Flask, render_template, jsonify
import os
import datetime
import threading
import time
from logger import logger
from config import CHECK_INTERVAL, KEYWORDS, TELEGRAM_BOT_TOKEN
from send_test_message import send_welcome_messages_to_new_users
from app_state import app_state, update_state

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "linkedin-job-scraper")

@app.route('/')
def home():
    """Display application status and configuration"""
    # Calculate uptime
    uptime = datetime.datetime.now() - app_state["start_time"]
    uptime_str = f"{uptime.days} days, {uptime.seconds // 3600} hours, {(uptime.seconds // 60) % 60} minutes"
    
    # Format next check time
    next_check = app_state["next_check"]
    if next_check:
        time_until = next_check - datetime.datetime.now()
        seconds_until = max(0, int(time_until.total_seconds()))
        next_check_str = f"in {seconds_until // 60} minutes, {seconds_until % 60} seconds"
    else:
        next_check_str = "soon"
    
    return render_template('index.html', 
                          app_state=app_state,
                          uptime=uptime_str,
                          next_check=next_check_str,
                          keywords=KEYWORDS,
                          check_interval=CHECK_INTERVAL)

@app.route('/api/status')
def status():
    """Return application status as JSON for API clients"""
    return jsonify({
        "status": "online" if app_state["running"] else "paused",
        "last_check": app_state["last_check"].isoformat() if app_state["last_check"] else None,
        "next_check": app_state["next_check"].isoformat() if app_state["next_check"] else None,
        "jobs_found": app_state["jobs_found"],
        "uptime_seconds": (datetime.datetime.now() - app_state["start_time"]).total_seconds(),
        "keywords": KEYWORDS
    })

@app.route('/ping')
def ping():
    """Simple endpoint for uptime monitoring services to ping"""
    # Calculate uptime
    uptime = datetime.datetime.now() - app_state["start_time"]
    uptime_str = f"{uptime.days} days, {uptime.seconds // 3600} hours, {(uptime.seconds // 60) % 60} minutes"
    
    # Update the status with the ping time
    app_state["last_ping"] = datetime.datetime.now()
    app_state["ping_count"] = app_state.get("ping_count", 0) + 1
    
    # Return a simple response with some basic status info
    return f"OK - Up for {uptime_str} - Last check: {app_state['last_check'].isoformat() if app_state['last_check'] else 'Never'} - Ping count: {app_state['ping_count']}", 200

@app.route('/api/send-test')
def send_test():
    """Send a test message to all Telegram users"""
    from job_checker import job_checker
    success = job_checker.send_test_message()
    return jsonify({
        "success": success,
        "message": "Test message sent successfully" if success else "Failed to send test message"
    })

def telegram_welcome_checker():
    """Periodically check for new Telegram users and send welcome messages"""
    # Only run if Telegram is configured
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram bot token not configured, welcome checker not started")
        return
        
    logger.info("Starting Telegram welcome message checker")
    
    # Run this check every 10 minutes
    WELCOME_CHECK_INTERVAL = 600  # 10 minutes in seconds
    
    while True:
        try:
            # Check for new users and send welcome messages
            logger.info("Checking for new Telegram users...")
            send_welcome_messages_to_new_users()
            
            # Sleep until next check
            time.sleep(WELCOME_CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Error in Telegram welcome checker: {e}")
            # Still sleep before retrying to avoid spamming logs
            time.sleep(60)  # Wait 1 minute before retrying after error

def keep_alive():
    """Start the Flask server in a background thread"""
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting keep-alive server on port {port}")
    t = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': port, 'debug': False})
    t.daemon = True  # Set as daemon so it doesn't block program exit
    t.start()
    
    # Update initial state
    update_state()
    
    # Start the Telegram welcome checker in a separate thread
    welcome_thread = threading.Thread(target=telegram_welcome_checker)
    welcome_thread.daemon = True
    welcome_thread.start()
    
    # Start the job checker
    from job_checker import start_job_checker
    job_checker = start_job_checker()
    logger.info("Job checker started")
    
    return t
