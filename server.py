from flask import Flask
from threading import Thread

app = Flask("")


@app.route("/")
def home():
    return "Hello. Thank you for visiting me! I'm alright. :)"


def run():
    app.run(host="0.0.0.0", port=8080)


def alive():
    t = Thread(target=run)
    t.start()
