"""
Web server for the LinkedIn Job Scraper application
This is the main entry point for the web interface
"""
import os
from keep_alive import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)