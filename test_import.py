import sys
print("Python version:", sys.version)

print("\nImporting modules...")
try:
    import flask
    print("✓ flask imported successfully")
except ImportError as e:
    print("✗ Failed to import flask:", e)

try:
    import requests
    print("✓ requests imported successfully")
except ImportError as e:
    print("✗ Failed to import requests:", e)

try:
    from bs4 import BeautifulSoup
    print("✓ BeautifulSoup imported successfully")
except ImportError as e:
    print("✗ Failed to import BeautifulSoup:", e)

try:
    import telegram
    print("✓ python-telegram-bot imported successfully")
except ImportError as e:
    print("✗ Failed to import python-telegram-bot:", e)

try:
    import gunicorn
    print("✓ gunicorn imported successfully")
except ImportError as e:
    print("✗ Failed to import gunicorn:", e)

try:
    import trafilatura
    print("✓ trafilatura imported successfully")
except ImportError as e:
    print("✗ Failed to import trafilatura:", e)

print("\nChecking project imports...")
try:
    import app_state
    print("✓ app_state imported successfully")
except ImportError as e:
    print("✗ Failed to import app_state:", e)

try:
    import config
    print("✓ config imported successfully")
except ImportError as e:
    print("✗ Failed to import config:", e)

try:
    import logger
    print("✓ logger imported successfully")
except ImportError as e:
    print("✗ Failed to import logger:", e)

try:
    import job_storage
    print("✓ job_storage imported successfully")
except ImportError as e:
    print("✗ Failed to import job_storage:", e)

try:
    import linkedin_scraper
    print("✓ linkedin_scraper imported successfully")
except ImportError as e:
    print("✗ Failed to import linkedin_scraper:", e)

try:
    import telegram_notifier
    print("✓ telegram_notifier imported successfully")
except ImportError as e:
    print("✗ Failed to import telegram_notifier:", e)