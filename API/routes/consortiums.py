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
    user_id = int(get_jwt_identity())
    query = """
            SELECT c.id, c.address, c.name, c.owner_name, c.admin_commission, c.surface, COUNT(f.id) AS ufs_amount
            FROM consortiums c
                     LEFT JOIN functional_units f ON f.consortium = c.id
            WHERE c.user_id = :user_id
            GROUP BY c.id, c.address, c.admin_commission
            """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), {"user_id": user_id})
            rows = result.mappings().all()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    consortiums = [
        {"id": row["id"], "address": row["address"], "ufs_amount": int(row["ufs_amount"] or 0),"admin_commission": int(row["admin_commission"])}
        for row in rows
    ]
    return jsonify({"consortiums": consortiums}), 200

@consortiums_bp.route("/consortium", methods=["GET"])
@jwt_required()
def get_consortium():
    user_id = int(get_jwt_identity())
    consortium_id = request.args.get("consortium_id", type=int)

    if not consortium_id:
        return {"error": "consortium_id is required"}, 400

    query = """
            SELECT c.id, c.address, c.name, c.owner_name, c.admin_commission, c.surface, COUNT(f.id) AS ufs_amount
            FROM consortiums c
                     LEFT JOIN functional_units f ON f.consortium = c.id
            WHERE c.user_id = :user_id AND c.id = :consortium_id
            GROUP BY c.id, c.address
            """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), {"user_id": user_id, "consortium_id": consortium_id})
            row = result.fetchone()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    if row:
        consortium = {
            "id": row.id,
            "address": row.address,
            "name": row.name,
            "owner_name": row.owner_name,
            "admin_commission": row.admin_commission,
            "surface": row.surface,
        }
    else:
        consortium = {}

    return consortium, 200

@consortiums_bp.route("/consortiums/addresses", methods=["GET"])
@jwt_required()
def get_addresses():
    user_id = int(get_jwt_identity())
    query = """
            SELECT c.address
            FROM consortiums c
            WHERE c.user_id = :user_id 
            """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), {"user_id": user_id})
            rows = result.mappings().all()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    addresses = set()

    for row in rows:
        addresses.add(row["address"])

    return jsonify({"addresses": list(addresses)})

#Deletes a consortium and its debts, expenses and functional units
@consortiums_bp.route("/consortiums/<int:consortium_id>", methods=["DELETE"])
@jwt_required()
def delete_consortium(consortium_id):
    user_id = int(get_jwt_identity())
    query = """
        DELETE FROM consortiums
        WHERE id = :consortium_id AND user_id = :user_id
    """

    delete_debts_q = "DELETE FROM debts WHERE consortium = :consortium_id"
    delete_expenses_q = "DELETE FROM common_expenses WHERE consortium = :consortium_id"
    delete_expenses_record_q = "DELETE FROM common_expenses_record WHERE consortium = :consortium_id"
    delete_units_q = "DELETE FROM functional_units WHERE consortium = :consortium_id"

    params = {"consortium_id": consortium_id, "user_id": user_id}

    try:
        with engine.begin() as conn:
            conn.execute(text(delete_expenses_record_q), {"consortium_id": consortium_id})
            conn.execute(text(delete_debts_q), {"consortium_id": consortium_id})
            conn.execute(text(delete_expenses_q), {"consortium_id": consortium_id})
            conn.execute(text(delete_units_q), {"consortium_id": consortium_id})
            result = conn.execute(text(query), params)
            if result.rowcount == 0:
                return {"error": "Consortium not found or permission denied"}, 404
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": f"Consortium {consortium_id} and all its related data deleted"}, 200

@consortiums_bp.route("/consortiums", methods=["POST"])
@jwt_required()
def post_consortiums():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    name = data.get("name")
    address = data.get("address")
    admin_commission = data.get("admin_commission")
    owner_name = data.get("owner_name")
    surface = data.get("surface")

    query = """
            INSERT INTO consortiums (name, address, owner_name, admin_commission, user_id, surface)
            VALUES (:name, :address, :owner_name, :admin_commission, :user_id, :surface)
            """

    params = {}
    params["name"] = name
    params["address"] = address
    params["owner_name"] = owner_name
    params["admin_commission"] = admin_commission
    params["user_id"] = user_id
    params["surface"] = surface

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
    user_id = int(get_jwt_identity())
    data = request.get_json()
    optional_data = ["address", "surface", "admin_commission"]
    received_data = {key: data[key] for key in optional_data if key in data}

    if not received_data:
        return {"error": "No fields to update"}, 400
    
    set_clause = ", ".join([f"{key} = :{key}" for key in received_data.keys()])
    query = f"UPDATE consortiums SET {set_clause} WHERE id = :id AND user_id = :user_id"
    received_data["id"] = id
    received_data["user_id"] = user_id

    try:
        with engine.begin() as conn:
            exists = conn.execute(text("SELECT 1 FROM consortiums WHERE id = :id"), {"id": id}).fetchone()
            if not exists:
                return {"error":f"consortium with id {id} not found"}, 404

            result = conn.execute(text(query), received_data)
            if result.rowcount == 0:
                return {"error": "Consortium not found or permission denied"}, 404
            
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return jsonify({"msg": "Comisión actualizada correctamente"}), 200
