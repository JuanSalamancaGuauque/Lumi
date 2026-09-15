import os

from dotenv import load_dotenv
from flask import Flask, send_from_directory

from routes.assistant import assistant

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave-temporal-solo-para-desarrollo")

app.register_blueprint(assistant)


@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")


@app.route("/css/<path:filename>")
def css(filename):
    return send_from_directory("frontend/css", filename)


@app.route("/js/<path:filename>")
def js(filename):
    return send_from_directory("frontend/js", filename)


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory("frontend/assets", filename)


if __name__ == "__main__":
    app.run(debug=True)