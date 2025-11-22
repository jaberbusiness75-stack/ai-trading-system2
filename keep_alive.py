from flask import Flask
from threading import Thread
import time
import logging

app = Flask('')

@app.route('/')
def home():
    return "🤖 بوت التداول يعمل بنجاح! 🚀"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

if __name__ == "__main__":
    keep_alive()
    print("🟢 خادم Keep-Alive يعمل...")
    
    # إبقاء السكريبت نشطاً
    while True:
        time.sleep(60)