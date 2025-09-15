from flask import Flask, request
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import *
from datetime import datetime

app = Flask(__name__)

def send_query(query: str) -> tuple[bool, any]:
    """Send a query to the database and return the result, if any error occurred return False and the error message."""
    try:
        conn = engine.connect()
        result = conn.execute(text(query))
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err.__cause__}")
        return False, str(err.__cause__)
    return True, result

@app.route("/login", methods=["GET"])
def login():
    email = request.args.get("email")
    password = request.args.get("password")
    query = f"SELECT * FROM `users` WHERE email='{email}' and password='{password}';"
    success, result = send_query(query)
    if not success:
        return False, result
    return result.rowcount > 0, "OK"



if __name__ == "__main__":
    app.run("0.0.0.0", API_PORT, debug=DEBUG=="True")