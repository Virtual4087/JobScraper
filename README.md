# LinkedIn Job Scraper Bot

## Overview
This application automatically checks LinkedIn for new job postings matching specific keywords and sends notifications via Telegram when new jobs are found.

## Features
- Automatically checks LinkedIn for new job postings at regular intervals (every 5 minutes)
- Sends notifications via Telegram when new jobs are found
- Web interface to monitor status and configuration
- Marks jobs as seen to prevent duplicate notifications

## How to Run
There are several ways to run this application:

### Method 1: Run Directly
```
python run_bot.py
```
This will start the application in the foreground. The application will continue running as long as your Replit session is active.

### Method 2: Run as Background Process
```
nohup python run_bot.py > app.log 2>&1 &
```
This starts the application in the background and saves output to app.log.

### Method 3: Use the deploy.sh Script
```
chmod +x deploy.sh
./deploy.sh
```
This script will stop any existing instances of the application and start a new one in the background.

## Configuration
The application is configured to search for jobs with the keywords "qa" and "java". 

## Telegram Integration
The application uses a Telegram bot to send notifications. The bot token and chat IDs are configured as environment variables.

## Web Interface
The application includes a web interface that shows:
- Current status
- Keywords being monitored
- Recent activity
- Option to send test messages

Access the web interface at port 5000 when the application is running.

## Files and Structure
- `run_bot.py`: Main entry point for the application
- `main.py`: Core application logic
- `linkedin_scraper.py`: Functions for scraping LinkedIn job postings
- `telegram_notifier.py`: Functions for sending Telegram notifications
- `job_storage.py`: Functions for storing and retrieving job information
- `keep_alive.py`: Web interface and status monitoring
- `job_checker.py`: Periodic job checking functionality
- `config.py`: Application configuration
- `deploy.sh`: Deployment script

## Logs
Check `app.log` for application logs when running in the background.