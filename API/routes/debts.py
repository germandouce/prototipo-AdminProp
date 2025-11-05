from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import *
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine, DEBUG

debts_bp = Blueprint("debts", __name__)

@debts_bp.route("/debts", methods=["GET"])
@jwt_required()
def get_debts():
    user_id = int(get_jwt_identity())
    tenant_name = request.args.get("tenant_name", type=str)
    id_unit = request.args.get("id_unit", type=int)
    consortium_id = request.args.get("consortium_id", type=int)

    if tenant_name is None or id_unit is None or consortium_id is None:
        return {"error": "tenant_name, id_unit and consortium_id are required"}, 400

    query = """
        SELECT d.id, d.amount, d.date, d.description
        FROM debts d
        JOIN consortiums c ON d.consortium = c.id
        WHERE d.tenant = :tenant_name AND d.functional_unit = :id_unit AND d.consortium = :consortium_id AND c.user_id = :user_id
        ORDER BY d.date DESC
    """

    params = {"tenant_name": tenant_name, "id_unit": id_unit, "consortium_id": consortium_id, "user_id": user_id}

    try:
        conn = engine.connect()
        result = conn.execute(text(query), params)
        rows = result.fetchall()
        conn.close()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    debts = []
    latest_payment = 0
    for i, row in enumerate(rows):
        debts.append({
            "id": row.id,
            "amount": float(row.amount),
            "date": str(row.date),
            "description": str(row.description)
        })
        if i == 0:
            latest_payment = float(row.amount)

    response = {
        "tenant": tenant_name,
        "debts": debts,
        "latest_payment": latest_payment,
    }

    return jsonify(response), 200

@debts_bp.route("/debts_total", methods=["GET"])
@jwt_required()
def get_total_debts():
    user_id = int(get_jwt_identity())

    query = """
        SELECT SUM(d.amount) AS total
        FROM debts d
        JOIN consortiums c ON d.consortium = c.id
        WHERE c.user_id = :user_id
    """

    try:
        conn = engine.connect()
        result = conn.execute(text(query), {"user_id": user_id})
        row = result.fetchone()
        conn.close()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    response = {
        "total": row.total,
    }

    return response, 200

@debts_bp.route("/debts/<int:payment_id>", methods=["DELETE"])
@jwt_required()
def delete_debts(payment_id):
    user_id = int(get_jwt_identity())

    query_register_payment = """
                             INSERT INTO payments (consortium, amount, functional_unit, date, tenant, description)
                             SELECT consortium, amount, functional_unit, NOW(), tenant, description
                             FROM debts
                             WHERE id = :payment_id
                               AND consortium IN (SELECT id FROM consortiums WHERE user_id = :user_id) \
                             """

    query = """
        DELETE FROM debts
        WHERE id = :payment_id
        AND consortium IN (SELECT id FROM consortiums WHERE user_id = :user_id)
    """

    params = {"payment_id": payment_id, "user_id": user_id}

    try:
        with engine.begin() as conn:
            result_payment = conn.execute(text(query_register_payment), params)

            if result_payment.rowcount == 0:
                return {"error": "Payment not found or permission denied"}, 404

            result = conn.execute(text(query), params)
            if result.rowcount == 0:
                return {"error": "Debt not found or permission denied"}, 404
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": f"Debt {payment_id} deleted"}, 200

@debts_bp.route("/debts", methods=["POST"])
@jwt_required()
def post_debts():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    tenant_name = data.get("tenant_name")
    id_unit = data.get("id_unit")
    date = data.get("date")
    amount = data.get("amount")
    consortium_id = data.get("consortium_id")

    query = """
            INSERT INTO debts (consortium, tenant, functional_unit, date, amount)
            VALUES (:consortium, :tenant_name, :id_unit, :date, :amount)
            """

    query_consortium = """
                       SELECT id \
                       FROM consortiums \
                       WHERE id = :consortium_id \
                         AND user_id = :user_id \
                       """

    params = {}
    params["tenant_name"] = tenant_name
    params["id_unit"] = id_unit
    params["date"] = date
    params["amount"] = amount
    params["consortium"] = consortium_id

    try:
        with engine.begin() as conn:
            result_consortium = conn.execute(
                text(query_consortium),
                {"consortium_id": consortium_id, "user_id": user_id}
            )

            if result_consortium.fetchone() is None:
                return {"error": "Consortium not found or permission denied"}, 404

            conn.execute(text(query), params)
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": f"payment for unit {id_unit} created"}, 201

@debts_bp.route("/debts/<int:id>", methods=["PATCH"])
@jwt_required()
def patch_debts(id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    optional_data = ["tenant", "date", "amount"]
    received_data = {key: data.get(key) for key in optional_data if key in data}
    if not received_data:
        return {"error": "No fields to update"}, 400

    set_clause = ", ".join([f"{key} = :{key}" for key in received_data.keys()])
    query = (f"UPDATE debts SET {set_clause} "
             f"WHERE id = :id"
             f" AND consortium IN (SELECT id FROM consortiums WHERE user_id = :user_id)")

    params = {
        **received_data,
        "id": id,
        "user_id": user_id,
    }

    try:
        with engine.begin() as conn:
            result = conn.execute(text(query), params)
            if result.rowcount == 0:
                return {"error": "Payment not found or permission denied"}, 404

    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": "updated payment"}, 200