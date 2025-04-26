
from flask import Flask
app = Flask('')

@app.route('/')
def home():
    return 'Bot is alive!'

def keep_alive():
    from threading import Thread
    t = Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8080})
    t.start()
