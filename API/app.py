from flask import Flask, request
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import *
from datetime import datetime

app = Flask(__name__)
engine = create_engine(f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

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

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    query = "SELECT * FROM users WHERE email=:email AND password=:password"

    try:
        conn = engine.connect()
        result = conn.execute(text(query), {"email": email, "password": password})
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err.__cause__}")
        return {"error": str(err.__cause__)}, 500

    if result.rowcount > 0:
        return {"message": "OK"}, 200
    else:
        return {"error": "Credenciales incorrectas"}, 401



if __name__ == "__main__":
    app.run("0.0.0.0", API_PORT, debug=DEBUG=="True")