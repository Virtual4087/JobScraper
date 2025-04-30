from flask import Flask, render_template, request, redirect, url_for
from job_checker import JobChecker
from app_state import app_state
from config import CHECK_INTERVAL, KEYWORDS, LOCATION
import threading
import os
from playwright.sync_api import sync_playwright


app = Flask(__name__)
job_checker = None  # Define but don't start yet


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    global job_checker
    if request.method == 'POST':
        user_input = request.form.get('keywords')
        user_location = request.form.get('location')

        keywords = [kw.strip() for kw in user_input.split(',') if kw.strip()]
        location = user_location.strip() if user_location else "United States"

        print(f"[SETUP] User entered keywords: {keywords}")
        print(f"[SETUP] User entered location: {location}")

        # Save to global app state
        app_state["keywords"] = keywords
        app_state["location"] = location

        # Start scraping in a background thread
        threading.Thread(
            target=start_job_checker_in_background,
            args=(keywords, location),
            daemon=True
        ).start()

        return redirect(url_for('index'))

    return render_template('setup.html')


def start_job_checker_in_background(keywords, location):
    global job_checker
    if job_checker:
        job_checker.stop()
    job_checker = JobChecker(keywords, location)
    job_checker.start()


@app.route('/')
def index():
    # next_check = app_state.get("next_check", "Unknown")
    # uptime = "Unknown"
    # keywords = app_state.get("keywords", KEYWORDS)
    # location = app_state.get("location", LOCATION)

    # print(f"[INDEX] keywords: {keywords}")
    # print(f"[INDEX] location: {location}")

    # return render_template(
    #     'index.html',
    #     app_state=app_state,
    #     next_check=next_check,
    #     uptime=uptime,
    #     check_interval=CHECK_INTERVAL,
    #     keywords=keywords,
    #     location=location
    # )
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://dice.com")
        title = page.title()
        browser.close()
        return f"Page title is: {title}"


@app.route('/stop')
def stop():
    global job_checker
    if job_checker:
        job_checker.stop()
        job_checker = None
    return redirect(url_for('setup'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("Starting Web Server...")
    app.run(host='0.0.0.0', port=port, debug=False)
