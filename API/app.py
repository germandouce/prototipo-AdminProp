from flask import Flask, request
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import *
from datetime import datetime
import os

app = Flask(__name__)

# Lógica para conexión con o sin SSL
connect_args = {}
if USE_SSL == "True":
    # Permite configurar la ruta del CA por variable de entorno, o usa una por defecto
    ssl_ca = os.environ.get("MYSQL_SSL_CA", "/etc/secrets/ca.pem")
    connect_args["ssl_ca"] = ssl_ca

engine = create_engine(
    f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    connect_args=connect_args
)

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

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    name = data.get("name")
    surname = data.get("surname")
    email = data.get("email")
    password = data.get("password")
    if not all([name, surname, email, password]):
        return {"error": "Faltan campos obligatorios"}, 400

    query = """
        INSERT INTO users (name, surname, email, password)
        VALUES (:name, :surname, :email, :password)
    """
    try:
        conn = engine.connect()
        conn.execute(text(query), {
            "name": name,
            "surname": surname,
            "email": email,
            "password": password
        })
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err.__cause__}")
        return {"error": str(err.__cause__)}, 500

    return {"message": "Usuario creado"}, 201


# Endpoint para consultar todos los usuarios
@app.route("/users", methods=["GET"])
def get_users():
    query = "SELECT * FROM users"
    try:
        conn = engine.connect()
        result = conn.execute(text(query))
        users = [dict(row) for row in result.mappings()]
        conn.close()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err.__cause__}")
        return {"error": str(err.__cause__)}, 500
    return {"users": users}, 200



if __name__ == "__main__":
    app.run("0.0.0.0", API_PORT, debug=DEBUG=="True")