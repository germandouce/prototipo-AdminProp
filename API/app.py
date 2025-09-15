from flask import Flask, request
import sql
from config import *
from datetime import datetime

app = Flask(__name__)

@app.route("/login")
def login():
    return 0

if __name__ == "__main__":
    app.run("0.0.0.0", API_PORT, debug=DEBUG=="True")