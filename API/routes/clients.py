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
SELECT
    f.tenant AS nombre,
    CONCAT(c.address, ' - ', f.unit_name) AS direccion,
    f.rent_value AS alquiler,
    f.id AS unit_id,
    c.address AS direccion_consorcio,
    c.id AS consortium_id,
    
    -- 1. Reemplazo de 'last_expensa' (Subconsulta Correlacionada)
    --    Esto busca la última expensa para ESTA fila (f.id)
    COALESCE(
        (
            SELECT amount
            FROM debts d_exp
            WHERE d_exp.functional_unit = f.id
              AND d_exp.description LIKE 'Expensas Ordinarias%'
            ORDER BY d_exp.date DESC
            LIMIT 1
        ), 0
    ) AS expensas,
    
    -- El resto de las columnas
    COALESCE(p.total_pagado, 0) AS pago,
    COALESCE(d.total_debido, 0) AS deuda,
    COALESCE(d.total_debido, 0) <= 0 AS pago_al_dia,
    c.address AS direccion_consorcio
    
FROM
    functional_units f
JOIN
    consortiums c ON f.consortium = c.id

-- 2. Reemplazo de CTE 'total_debts' (Subconsulta en el JOIN)
LEFT JOIN (
    SELECT
        functional_unit,
        SUM(amount) AS total_debido
    FROM debts
    GROUP BY functional_unit
) d ON f.id = d.functional_unit

-- 3. Reemplazo de CTE 'total_payments' (Subconsulta en el JOIN)
LEFT JOIN (
    SELECT
        functional_unit,
        SUM(amount) AS total_pagado
    FROM payments
    GROUP BY functional_unit
) p ON f.id = p.functional_unit

WHERE
    c.user_id = :user_id
    AND f.tenant IS NOT NULL
    AND f.tenant != '';
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
    direcciones = set()

    clients = []
    for row in rows:
        if row.deuda > 0:
            alquiler = float(row.alquiler or 0)
            expensas = float(row.expensas or 0)
            pago_total = alquiler + expensas
            ingresos += pago_total
            direccion = row.direccion
            deuda = float(row.deuda or 0)
            direcciones.add(row.direccion_consorcio)

            clients.append({
                "nombre": row.nombre,
                "direccion": direccion,
                "alquiler": alquiler,
                "expensas": expensas,
                "deuda": deuda if deuda > 0 else 0,
                "pago": pago_total,
                "pago_al_dia": deuda == 0,
                "consortium_id": row.consortium_id,
                "unit_id": row.unit_id
            })

    response = {
        "clients": clients,
        "deuda_total": deuda_total,
        "ingresos": ingresos,
        "direcciones": list(direcciones)
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