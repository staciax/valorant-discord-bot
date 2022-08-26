from bot import run_bot

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def main():
  return 'Keep Alive!'

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()

if __name__ == '__main__':
    keep_alive()
    run_bot()
