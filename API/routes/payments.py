from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import *
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine, DEBUG

payments_bp = Blueprint("payments", __name__)

@payments_bp.route("/payments", methods=["GET"])
def get_payments():
    tenant_name = request.args.get("tenant_name", type=str)
    id_unit = request.args.get("id_unit", type=int)

    if tenant_name is None or id_unit is None:
        return {"error": "tenant_name and id_unit are required"}, 400

    query = """
        SELECT p.id, p.amount, p.date
        FROM payments p
        WHERE p.tenant = :tenant_name AND p.functional_unit = :id_unit
        ORDER BY p.date DESC
    """

    params = {"tenant_name": tenant_name, "id_unit": id_unit}

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
        "tenant": tenant_name,
        "payments": payments,
        "latest_payment": latest_payment,
    }

    return jsonify(response), 200

@payments_bp.route("/payments/<int:payment_id>", methods=["DELETE"])
def delete_payment(payment_id):
    query = """
        DELETE FROM payments
        WHERE id = :payment_id 
    """

    try:
        with engine.begin() as conn:
            result = conn.execute(text(query), {"payment_id": payment_id})
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": f"Payment {payment_id} deleted"}, 200

@payments_bp.route("/payments", methods=["POST"])
@jwt_required()
def post_payments():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    tenant_name = data.get("tenant_name")
    id_unit = data.get("id_unit")
    date = data.get("date")
    amount = data.get("amount")

    query = """
            INSERT INTO payments (consortium, tenant, functional_unit, date, amount)
            VALUES (:consortium_id, :tenant_name, :id_unit, :date, :amount)
            """

    query_get_consortium = """
                            SELECT c.id
                            FROM consortiums c
                            WHERE c.user_id = :user_id
                           """

    params = {}
    params["tenant_name"] = tenant_name
    params["id_unit"] = id_unit
    params["date"] = date
    params["amount"] = amount

    try:
        with engine.begin() as conn:
            result_consortium_id = conn.execute(text(query_get_consortium), {"user_id": user_id})
            consortium_id = result_consortium_id.mappings().first()
            params["consortium_id"] = consortium_id["id"]
            result = conn.execute(text(query), params)
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": f"payment for unit {id_unit} created"}, 201


@payments_bp.route("/payments/<int:id>", methods=["PATCH"])
@jwt_required()
def patch_payments(id):
    data = request.get_json()

    optional_data = ["tenant", "date", "amount"]
    received_data = {key: data.get(key) for key in optional_data if key in data}
    if not received_data:
        return {"error": "No fields to update"}, 400

    set_clause = ", ".join([f"{key} = :{key}" for key in received_data.keys()])
    query = f"UPDATE payments SET {set_clause} WHERE id = :id"
    received_data["id"] = id

    try:
        with engine.begin() as conn:
            exists = conn.execute(text("SELECT 1 FROM payments WHERE id = :id"), {"id": id}).fetchone()
            if not exists:
                return {"error": f"Payment with id {id} not found"}, 404

            result = conn.execute(text(query), received_data)
            if result.rowcount == 0:
                return {"error": "Payment not found"}, 404

    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": "updated payment"}, 200