from flask import Flask, render_template, request, redirect, url_for
from job_checker import JobChecker
from app_state import app_state
from config import CHECK_INTERVAL

app = Flask(__name__)
job_checker = None  # Global job checker

@app.route('/', methods=['GET', 'POST'])
def setup():
    global job_checker
    if request.method == 'POST':
        user_input = request.form.get('keywords')
        user_location = request.form.get('location')

        keywords = [kw.strip() for kw in user_input.split(',') if kw.strip()]
        location = user_location.strip() if user_location else "United States"

        print(f"User entered keywords: {keywords}")
        print(f"User entered location: {location}")

        # Save to app state
        app_state["keywords"] = keywords
        app_state["location"] = location

        # Start the scraper
        job_checker = JobChecker(keywords, location)
        job_checker.start()

        return redirect(url_for('dashboard'))

    return render_template('setup.html')


@app.route('/dashboard')
def dashboard():
    next_check = app_state.get("next_check", "Unknown")
    uptime = "Unknown"  # You can calculate it if needed
    keywords = app_state.get("keywords", [])
    location = app_state.get("location", "Unknown")

    return render_template(
        'index.html',
        app_state=app_state,
        next_check=next_check,
        uptime=uptime,
        check_interval=CHECK_INTERVAL,
        keywords=keywords,
        location=location
    )


@app.route('/stop')
def stop():
    global job_checker
    if job_checker:
        job_checker.stop()
        job_checker = None
    return redirect(url_for('setup'))


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    print("Starting Web Server...")
    app.run(debug=True, host="0.0.0.0", port=port)
