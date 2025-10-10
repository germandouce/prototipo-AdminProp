from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import *
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine, DEBUG

functional_units_bp = Blueprint("functional_units", __name__)

@functional_units_bp.route("/functional_units", methods=["GET"])
def get_functional_units():
    consortium_id = request.args.get("consortium_id", type=int)

    query = """
        SELECT f.id, f.unit_number, f.unit_name, f.surface,
               f.tenant, f.rent_value, f.debt
        FROM functional_units f
        JOIN consortiums c ON f.consortium = c.id
    """

    query_address = """
                    SELECT c.address
                    FROM   consortiums c
                    WHERE c.id = :consortium_id
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
def get_functional_unit():
    consortium_id = request.args.get("consortium_id", type=int)
    unit_id = request.args.get("unit_id", type=int)

    if unit_id is None:
        return {"error": "Se requiere unit_id"}, 400

    query = """
        SELECT f.id, f.unit_number, f.unit_name, f.surface,
               f.tenant, f.debt, c.address AS consortium_address
        FROM functional_units f
        JOIN consortiums c ON f.consortium = c.id
        WHERE f.id = :unit_id
    """

    params = {"unit_id": unit_id}

    if consortium_id is not None:
        query += " AND f.consortium = :consortium_id"
        params["consortium_id"] = consortium_id

    try:
        conn = engine.connect()
        result = conn.execute(text(query), params).fetchone()
        conn.close()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    if not result:
        return {"error": "Unidad no encontrada"}, 404

    functional_unit = {
        "id": result.id,
        "unit_number": str(result.unit_number).zfill(3),
        "unit_name": result.unit_name,
        "occupation_status": True if result.tenant else False,
        "tenant": result.tenant,
        "consortium_address": result.consortium_address,
        "surface": float(result.surface),
        "debt": float(result.debt)
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

    query = """
            INSERT INTO functional_units (unit_number, unit_name, surface, consortium)
            VALUES (:unit_number, :unit_name, :surface, :consortium)
            """

    query_get_consortium = """
                           SELECT c.id
                           FROM consortiums c
                           WHERE c.user_id = :user_id \
                           """

    params = {}
    params["unit_number"] = unit_number
    params["unit_name"] = unit_name
    params["surface"] = surface

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

    return {"message": f"functional unit {unit_name} created"}, 201

@functional_units_bp.route("/functional_units/<int:id>", methods=["PATCH"])
@jwt_required()
def patch_functional_unit(id):
    data = request.get_json()

    optional_data = ["unit_number", "unit_name", "tenant", "debt"]
    received_data = {key: data.get(key) for key in optional_data if key in data}
    if not received_data:
        return {"error": "No fields to update"}, 400

    set_clause = ", ".join([f"{key} = :{key}" for key in received_data.keys()])
    query = f"UPDATE functional_units SET {set_clause} WHERE id = :id"
    received_data["id"] = id

    try:
        with engine.begin() as conn:
            exists = conn.execute(text("SELECT 1 FROM functional_units WHERE id = :id"), {"id": id}).fetchone()
            if not exists:
                return {"error": f"Functional unit with id {id} not found"}, 404

            result = conn.execute(text(query), received_data)
            if result.rowcount == 0:
                return {"error": "Functional unit not found"}, 404

    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": "Functional unit updated"}, 200

@functional_units_bp.route("/functional_unit/<int:unit_id>", methods=["DELETE"])
def delete_unit(unit_id):
    query = """
        DELETE FROM functional_units
        WHERE id = :unit_id 
    """

    try:
        with engine.begin() as conn:
            result = conn.execute(text(query), {"unit_id": unit_id})
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": f"Unit {unit_id} deleted"}, 200