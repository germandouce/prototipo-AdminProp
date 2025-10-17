from flask import Blueprint, jsonify
from sqlalchemy import text
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import engine, DEBUG

clients_bp = Blueprint("clients_bp", __name__)

@clients_bp.route("/clients", methods=["GET"])
@jwt_required()
def get_clients():
    user_id = int(get_jwt_identity())

    query = """
            SELECT f.tenant                              AS name, \
                   CONCAT(c.address, ' - ', f.unit_name) AS address, \
                   f.rent_value                          AS rent, \
                   CASE \
                       WHEN cs.total_surface > 0 THEN (f.surface / cs.total_surface) * \
                                                      COALESCE(me.total_monthly_expense, 0) \
                       ELSE 0 \
                       END                               AS expensas
            FROM functional_units f
                     JOIN consortiums c ON f.consortium = c.id
                     LEFT JOIN (SELECT consortium, \
                                       SUM(amount) AS total_monthly_expense \
                                FROM common_expenses \
                                WHERE DATE_FORMAT(date, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m') \
                                GROUP BY consortium) me ON f.consortium = me.consortium
                     LEFT JOIN (SELECT consortium, \
                                       SUM(surface) AS total_surface \
                                FROM functional_units \
                                GROUP BY consortium) cs ON f.consortium = cs.consortium
            WHERE c.user_id = :user_id
              AND f.tenant IS NOT NULL
              AND f.tenant != '' \
            """

    params = {"user_id": user_id}

    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            rows = result.fetchall()
    except Exception as e:
        if DEBUG:
            print(f"DB_ERROR: {e}")
        return {"error": str(e)}, 500

    deuda_total = 0
    ingresos = 0
    direcciones = []

    clients = []
    for row in rows:
        alquiler = float(row.rent or 0)
        expensas = float(row.expensas or 0)
        pago_total = alquiler + expensas
        ingresos += pago_total
        direccion = row.address
        if not direcciones or direcciones[-1] != direccion:
            direcciones.append(direccion)

        clients.append({
            "nombre": row.name,
            "direccion": row.address,
            "alquiler": alquiler,
            "expensas": expensas,
            "deuda": deuda,
            "pago": pago_total,
            "pago_al_dia": deuda == 0
        })

    response = {
        "clients": clients,
        "deuda_total": deuda_total,
        "ingresos": ingresos,
        "direcciones": direcciones
    }

    return jsonify({"response": response}), 200


@clients_bp.route("/consortiums/addresses", methods=["GET"])
@jwt_required()
def get_consortium_addresses():
    user_id = int(get_jwt_identity())

    # Consulta simple y directa a la tabla de consorcios
    query = "SELECT DISTINCT address FROM consortiums WHERE user_id = :user_id"

    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), {"user_id": user_id})
            # Convertimos el resultado en una lista simple de strings
            addresses = [row.address for row in result]
    except Exception as e:
        if DEBUG:
            print(f"DB_ERROR: {e}")
        return {"error": str(e)}, 500

    return jsonify({"addresses": addresses}), 200