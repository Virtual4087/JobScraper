from flask import Flask, render_template, request, redirect, url_for
from job_checker import JobChecker
from app_state import app_state
from config import CHECK_INTERVAL, KEYWORDS, LOCATION



app = Flask(__name__)
job_checker = None  # ✅ Just define it, don't create yet!

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    global job_checker
    if request.method == 'POST':
        user_input = request.form.get('keywords')
        user_location = request.form.get('location')

        keywords = [kw.strip() for kw in user_input.split(',') if kw.strip()]
        location = user_location.strip() if user_location else "United States"

        print(f"User entered keywords: {keywords}")
        print(f"User entered location: {location}")


        job_checker = JobChecker(keywords, location)
        job_checker.start()

        app_state["keywords"] = keywords
        app_state["location"] = location

        return redirect(url_for('index'))
    
    return render_template('setup.html')


@app.route('/')
def index():
    global job_checker

    next_check = "Unknown"  # or calculate
    uptime = "Unknown"      # or calculate
    keywords = app_state["keywords"] if "keywords" in app_state else KEYWORDS
    location = app_state["location"] if "location" in app_state else "United States"
    
    print(f"keywords: {keywords}")
    print(f"location: {location}")

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
    print("Starting Web Server...")
    app.run(debug=True, port=5000)
