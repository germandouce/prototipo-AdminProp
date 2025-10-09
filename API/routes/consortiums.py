from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import *
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine, DEBUG
consortiums_bp = Blueprint("consortiums", __name__)

@consortiums_bp.route("/consortiums", methods=["GET"])
@jwt_required()
def get_consortiums():
    user_id = int(get_jwt_identity())  # <-- convertir a int
    query = """
            SELECT c.id, c.address, COUNT(f.id) AS ufs_amount
            FROM consortiums c
                     LEFT JOIN functional_units f ON f.consortium = c.id
            WHERE c.user_id = :user_id
            GROUP BY c.id, c.address
            """
    try:
        with engine.connect() as conn:
            conn = engine.connect()
            result = conn.execute(text(query), {"user_id": user_id})
            rows = result.mappings().all()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    consortiums = [
        {"id": row["id"], "address": row["address"], "ufs_amount": int(row["ufs_amount"] or 0)}
        for row in rows
    ]
    return jsonify({"consortiums": consortiums}), 200

@consortiums_bp.route("/consortiums/<int:consortium_id>", methods=["DELETE"])
def delete_consortium(consortium_id):
    query = """
        DELETE FROM consortiums
        WHERE id = :consortium_id 
    """

    try:
        with engine.begin() as conn:
            result = conn.execute(text(query), {"consortium_id": consortium_id})
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": f"Consortium {consortium_id} deleted"}, 200

@consortiums_bp.route("/consortiums", methods=["POST"])
@jwt_required()
def post_consortiums():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    name = data.get("name")
    address = data.get("address")
    admin_commission = data.get("admin_commission")
    owner_name = data.get("owner_name")

    query = """
            INSERT INTO consortiums (name, address, owner_name, admin_commission, user_id)
            VALUES (:name, :address, :owner_name, :admin_commission, :user_id)
            """

    params = {}
    params["name"] = name
    params["address"] = address
    params["owner_name"] = owner_name
    params["admin_commission"] = admin_commission
    params["user_id"] = user_id

    try:
        with engine.begin() as conn:
            result = conn.execute(text(query), params)
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": f"consortium {name} created"}, 201


@consortiums_bp.route("/consortiums/<int:id>", methods=["PATCH"])
@jwt_required()
def patch_consortiums(id):
    data = request.get_json()

    optional_data = ["address"]
    received_data = {key: data.get(key) for key in optional_data if key in data}
    if not received_data:
        return {"error": "No fields to update"}, 400
    
    set_clause = ", ".join([f"{key} = :{key}" for key in received_data.keys()])
    query = f"UPDATE consortiums SET {set_clause} WHERE id = :id"
    received_data["id"] = id

    try:
        with engine.begin() as conn:
            exists = conn.execute(text("SELECT 1 FROM consortiums WHERE id = :id"), {"id": id}).fetchone()
            if not exists:
                return {"error":f"consortium with id {id} not found"}, 404

            result = conn.execute(text(query), received_data)
            if result.rowcount == 0:
                return {"error": "Consortium not found"}, 404
            
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": "updated consortium"}, 200