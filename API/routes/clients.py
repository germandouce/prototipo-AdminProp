from flask import Blueprint, jsonify
from sqlalchemy import text
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import engine, DEBUG

clients_bp = Blueprint("clients_bp", __name__)

@clients_bp.route("/clients", methods=["GET"])
@jwt_required()
def get_clients():
    user_id = int(get_jwt_identity())

    # --- INICIO DE LA CORRECCIÓN ---
    # Consulta SQL sin las barras invertidas (\) innecesarias y sin el error final.
    query = """
            SELECT f.tenant                              AS name, \
                   CONCAT(c.address, ' - ', f.unit_name) AS address, \
                   f.rent_value                          AS rent, \
                   f.debt                                AS debt
            FROM functional_units f
                     JOIN consortiums c ON f.consortium = c.id
            WHERE c.user_id = :user_id
              AND f.tenant IS NOT NULL
              AND f.tenant != ''
            """
    # --- FIN DE LA CORRECCIÓN ---

    params = {"user_id": user_id}

    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            rows = result.fetchall()
    except Exception as e:
        if DEBUG:
            print(f"DB_ERROR: {e}")
        return {"error": str(e)}, 500

    clients = []
    for row in rows:
        alquiler = float(row.rent or 0)
        deuda = float(row.debt or 0)
        pago_total = alquiler + deuda

        clients.append({
            "nombre": row.name,
            "direccion": row.address,
            "alquiler": alquiler,
            "deuda": deuda,
            "pago": pago_total,
            "pago_al_dia": deuda == 0
        })

    return jsonify({"clients": clients}), 200