from flask import Flask, request
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import *
from flask import jsonify
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

@app.route("/consortiums", methods=["GET"])
def get_consortiums():
    query = """
        SELECT c.id, c.address, COUNT(f.id) AS ufs_amount
        FROM consortiums c
        LEFT JOIN functional_units f ON f.consortium = c.id
        GROUP BY c.id, c.address
    """
    try:
        conn = engine.connect()
        result = conn.execute(text(query))
        rows = result.fetchall()
        conn.close()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err.__cause__}")
        return {"error": str(err.__cause__)}, 500

    consortiums = []
    for row in rows:
        consortiums.append({
            "id": row.id,
            "address": row.address,
            "ufs_amount": int(row.ufs_amount) if row.ufs_amount is not None else 0
        })

    return jsonify({"consortiums": consortiums}), 200


@app.route("/functional_units", methods=["GET"])
def get_functional_units():
    consortium_id = request.args.get("consortium_id", type=int)

    query = """
        SELECT f.id, f.unit_number, f.unit_name, f.surface, f.surface_percentage,
               f.tentan, f.debt, c.address AS consortium_address
        FROM functional_units f
        JOIN consortiums c ON f.consortium = c.id
    """

    params = {}
    if consortium_id is not None:
        query += " WHERE f.consortium = :consortium_id"
        params["consortium_id"] = consortium_id

    try:
        conn = engine.connect()
        if params:
            result = conn.execute(text(query), params)
        else:
            result = conn.execute(text(query))
        rows = result.fetchall()
        conn.close()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err.__cause__}")
        return {"error": str(err.__cause__)}, 500

    functional_units = []
    for row in rows:
        functional_units.append({
            "id": row.id,
            "unit_number": str(row.unit_number).zfill(3),
            "unit_name": row.unit_name,
            "occupation_status": True if row.tentan else False,
            "tenant": row.tentan,
            "consortium_address": row.consortium_address,
            "surface": float(row.surface),
            "debt": float(row.debt)
        })

    return jsonify({"functional_units": functional_units}), 200

@app.route("/payments", methods=["GET"])
def get_payments():
    tentant_name = request.args.get("tentant_name", type=str)
    id_unit = request.args.get("id_unit", type=int)

    if tentant_name is None or id_unit is None:
        return {"error": "Se requieren tentant_name e id_unit"}, 400

    query = """
        SELECT p.id, p.amount, p.date
        FROM payments p
        WHERE p.tentant = :tentant_name AND p.functional_unit = :id_unit
        ORDER BY p.date DESC
    """

    params = {"tentant_name": tentant_name, "id_unit": id_unit}

    try:
        conn = engine.connect()
        result = conn.execute(text(query), params)
        rows = result.fetchall()
        conn.close()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    payments = []
    latest_payment = 0
    for i, row in enumerate(rows):
        payments.append({
            "id": row.id,
            "amount": float(row.amount),
            "date": str(row.date)
        })
        if i == 0:
            latest_payment = float(row.amount)

    response = {
        "tentant": tentant_name,
        "payments": payments,
        "latest_payment": latest_payment,
    }

    return jsonify(response), 200

if __name__ == "__main__":
    app.run("0.0.0.0", API_PORT, debug=DEBUG=="True")