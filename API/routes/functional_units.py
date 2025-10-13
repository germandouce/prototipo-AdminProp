from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import *
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine, DEBUG

functional_units_bp = Blueprint("functional_units", __name__)

@functional_units_bp.route("/functional_units", methods=["GET"])
@jwt_required()
def get_functional_units():
    user_id = int(get_jwt_identity())
    consortium_id = request.args.get("consortium_id", type=int)

    if consortium_id is None:
        return {"error": "consortium_id is required"}, 400

    query = """
        SELECT f.id, f.unit_number, f.unit_name, f.surface,
               f.tenant, f.rent_value, f.debt
        FROM functional_units f
        JOIN consortiums c ON f.consortium = c.id
        WHERE f.consortium = :consortium_id AND c.user_id = :user_id
    """

    query_address = """
                    SELECT c.address
                    FROM   consortiums c
                    WHERE c.id = :consortium_id AND c.user_id = :user_id
                    """

    params = {"user_id": user_id, "consortium_id": consortium_id}

    try:
        conn = engine.connect()
        result = conn.execute(text(query), params)
        if result.rowcount == 0:
            return {"error": "No functional units or permission denied"}, 404
        consortium_address_result = conn.execute(text(query_address), params).fetchone()
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
            "occupation_status": True if row.tenant else False,
            "tenant": row.tenant,
            "surface": float(row.surface),
            "debt": float(row.debt),
            "rent_value": float(row.rent_value)
        })

    response = {
        "address": consortium_address_result.address,
        "functional_units": functional_units
    }

    return jsonify(response), 200

@functional_units_bp.route("/functional_unit", methods=["GET"])
@jwt_required()
def get_functional_unit():
    user_id = int(get_jwt_identity())
    consortium_id = request.args.get("consortium_id", type=int)
    unit_id = request.args.get("unit_id", type=int)

    if not all([consortium_id, unit_id]):
        return {"error": "consortium_id and unit_id are required"}, 400

    query = """
        SELECT f.id, f.unit_number, f.unit_name, f.surface,
               f.tenant, f.debt, f.rent_value, c.address AS consortium_address
        FROM functional_units f
        JOIN consortiums c ON f.consortium = c.id
        WHERE f.id = :unit_id AND f.consortium = :consortium_id AND c.user_id = :user_id
    """

    params = {"unit_id": unit_id, "user_id": user_id, "consortium_id": consortium_id}

    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), params).fetchone()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    if not result:
        return {"error": "Functional unit not found or permission denied"}, 404

    functional_unit = {
        "id": result.id,
        "unit_number": str(result.unit_number).zfill(3),
        "unit_name": result.unit_name,
        "occupation_status": True if result.tenant else False,
        "tenant": result.tenant,
        "consortium_address": result.consortium_address,
        "surface": float(result.surface),
        "debt": float(result.debt),
        "rent_value": float(result.rent_value)
    }

    return jsonify({"functional_unit": functional_unit}), 200

@functional_units_bp.route("/functional_units", methods=["POST"])
@jwt_required()
def post_functional_units():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    unit_number = data.get("unit_number")
    unit_name = data.get("unit_name")
    surface = data.get("surface")
    consortium_id = data.get("consortium_id")

    query = """
            INSERT INTO functional_units (unit_number, unit_name, surface, consortium)
            VALUES (:unit_number, :unit_name, :surface, :consortium)
            """

    query_consortium = """
                       SELECT id \
                       FROM consortiums \
                       WHERE id = :consortium_id \
                         AND user_id = :user_id \
                       """

    params = {}
    params["unit_number"] = unit_number
    params["unit_name"] = unit_name
    params["surface"] = surface
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

    return {"message": f"functional unit {unit_name} created"}, 201

@functional_units_bp.route("/functional_units/<int:id>", methods=["PATCH"])
@jwt_required()
def patch_functional_unit(id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    optional_data = ["unit_number", "unit_name", "tenant", "debt", "rent_value", "surface"]
    received_data = {key: data.get(key) for key in optional_data if key in data}
    if not received_data:
        return {"error": "No fields to update"}, 400

    set_clause = ", ".join([f"{key} = :{key}" for key in received_data.keys()])
    query = f"""
        UPDATE functional_units
        SET {set_clause}
        WHERE id = :id
        AND consortium IN (SELECT id FROM consortiums WHERE user_id = :user_id)
    """
    params = {
        **received_data,
        "id": id,
        "user_id": user_id
    }

    try:
        with engine.begin() as conn:
            result = conn.execute(text(query), params)
            if result.rowcount == 0:
                return {"error": "Functional unit not found or permission denied"}, 404

    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": "Functional unit updated"}, 200

#Deletes a functional unit and its paymnets
@functional_units_bp.route("/functional_unit/<int:unit_id>", methods=["DELETE"])
@jwt_required()
def delete_unit(unit_id):
    user_id = int(get_jwt_identity())
    query = """
        DELETE FROM functional_units
        WHERE id = :unit_id
        AND consortium IN (SELECT id FROM consortiums WHERE user_id = :user_id)
    """

    params = {"unit_id": unit_id, "user_id": user_id}
    delete_payments_q = "DELETE FROM payments WHERE functional_unit = :unit_id"

    try:
        with engine.begin() as conn:
            conn.execute(text(delete_payments_q), {"unit_id": unit_id})
            result = conn.execute(text(query), params)
            if result.rowcount == 0:
                return {"error": "Functional unit not found or permission denied"}, 404
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": f"Unit {unit_id} deleted"}, 200