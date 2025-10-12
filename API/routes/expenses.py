from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import *
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine, DEBUG

expenses_bp = Blueprint("expenses", __name__)

@expenses_bp.route("/expenses", methods=["GET"])
@jwt_required()
def get_expenses():
    user_id = int(get_jwt_identity())
    consortium_id = request.args.get("consortium_id", type=int)

    if consortium_id is None:
        return {"error": "consortium_id is required"}, 400

    query = """
            SELECT e.id, e.description, e.amount, e.date
            FROM common_expenses e
            JOIN consortiums c ON e.consortium = c.id
            WHERE e.consortium = :consortium_id AND c.user_id = :user_id
            """

    params = {"consortium_id": consortium_id, "user_id": user_id}

    try:
        conn = engine.connect()
        result = conn.execute(text(query), params)
        rows = result.fetchall()
        conn.close()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    expenses = []
    for row in rows:
        expenses.append({
            "id": row.id,
            "description": row.description,
            "amount": float(row.amount),
            "date": str(row.date)
        })

    response = {
        "expenses": expenses,
    }

    return jsonify(response), 200

@expenses_bp.route("/expenses/<int:expense_id>", methods=["DELETE"])
@jwt_required()
def delete_expense(expense_id):
    user_id = int(get_jwt_identity())
    query = """
        DELETE FROM common_expenses
        WHERE id = :expense_id
        AND consortium IN (SELECT id FROM consortiums WHERE user_id = :user_id)
    """

    try:
        with engine.begin() as conn:
            result = conn.execute(text(query), {"expense_id": expense_id, "user_id": user_id})
            if result.rowcount == 0:
                return {"error": "Expense not found or permission denied"}, 404
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": f"Expense {expense_id} deleted"}, 200

@expenses_bp.route("/expenses", methods=["POST"])
@jwt_required()
def post_expenses():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    description = data.get("description")
    amount = data.get("amount")
    date = data.get("date")
    consortium_id = data.get("consortium_id")

    if not all([description, amount, date, consortium_id]):
        return {"error": "description, amount, date, and consortium_id are required"}, 400

    query_consortium = """
                            SELECT id \
                            FROM consortiums \
                            WHERE id = :consortium_id \
                              AND user_id = :user_id \
                            """

    query = """
            INSERT INTO common_expenses (description, amount, date, consortium)
            VALUES (:description, :amount, :date, :consortium)
            """

    params = {}
    params["description"] = description
    params["amount"] = amount
    params["date"] = date
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

    return {"message": f"expense {description} created"}, 201


@expenses_bp.route("/expenses/<int:id>", methods=["PATCH"])
@jwt_required()
def patch_expenses(id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    optional_data = ["description", "amount", "date", "consortium"]
    received_data = {key: data.get(key) for key in optional_data if key in data}
    if not received_data:
        return {"error": "No fields to update"}, 400

    set_clause = ", ".join([f"{key} = :{key}" for key in received_data.keys()])
    query = (f"UPDATE common_expenses SET {set_clause} "
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
                return {"error": "Expense not found or permission denied"}, 404

    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": "updated expenses"}, 200