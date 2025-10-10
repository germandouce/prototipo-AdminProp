from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import *
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine, DEBUG

expenses_bp = Blueprint("expenses", __name__)

@expenses_bp.route("/expenses", methods=["GET"])
def get_expenses():
    consortium_id = request.args.get("consortium_id", type=int)

    if consortium_id is None:
        return {"error": "consortium_id is required"}, 400

    query = """
            SELECT e.id, e.description, e.amount, e.date
            FROM common_expenses e
            WHERE e.consortium = :consortium_id
            """

    params = {"consortium_id": consortium_id}

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
def delete_expense(expense_id):
    query = """
        DELETE FROM common_expenses
        WHERE id = :expense_id 
    """

    try:
        with engine.begin() as conn:
            result = conn.execute(text(query), {"expense_id": expense_id})
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

    query = """
            INSERT INTO common_expenses (description, amount, date, consortium)
            VALUES (:description, :amount, :date, :consortium)
            """

    query_get_consortium = """
                           SELECT c.id
                           FROM consortiums c
                           WHERE c.user_id = :user_id
                           """

    params = {}
    params["description"] = description
    params["amount"] = amount
    params["date"] = date

    try:
        with engine.begin() as conn:
            result_consortium_id = conn.execute(text(query_get_consortium), {"user_id": user_id})
            consortium = result_consortium_id.mappings().first()
            params["consortium"] = consortium["id"]
            result = conn.execute(text(query), params)
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": f"expense {description} created"}, 201


@expenses_bp.route("/expenses/<int:id>", methods=["PATCH"])
@jwt_required()
def patch_expenses(id):
    data = request.get_json()

    optional_data = ["description", "amount", "date", "consortium"]
    received_data = {key: data.get(key) for key in optional_data if key in data}
    if not received_data:
        return {"error": "No fields to update"}, 400

    set_clause = ", ".join([f"{key} = :{key}" for key in received_data.keys()])
    query = f"UPDATE common_expenses SET {set_clause} WHERE id = :id"
    received_data["id"] = id

    try:
        with engine.begin() as conn:
            exists = conn.execute(text("SELECT 1 FROM common_expenses WHERE id = :id"), {"id": id}).fetchone()
            if not exists:
                return {"error": f"Common expense with id {id} not found"}, 404

            result = conn.execute(text(query), received_data)
            if result.rowcount == 0:
                return {"error": "Common expense not found"}, 404

    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": "updated expenses"}, 200