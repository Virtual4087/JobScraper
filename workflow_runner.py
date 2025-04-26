import os
import sys
import time
import threading
import signal
import subprocess

def run_application():
    """Run the application in a subprocess"""
    print("Starting the LinkedIn Job Scraper application...")
    
    # Run the application
    process = subprocess.Popen(
        ["python", "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Print output in real-time
    for line in iter(process.stdout.readline, ""):
        print(line, end="")
        sys.stdout.flush()
    
    # Wait for process to terminate
    process.wait()
    print(f"Application exited with code {process.returncode}")

def signal_handler(sig, frame):
    print("Terminating application...")
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the application
    run_application()