from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def main():
    return "BOT IS ONLINE"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()