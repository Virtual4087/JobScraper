from flask import Flask
import os
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return 'Basic Server is running!'

def run_app():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    print("Starting basic server on port 8080")
    server_thread = Thread(target=run_app)
    server_thread.daemon = True
    server_thread.start()
    
    # Keep the main thread alive
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server shutting down")