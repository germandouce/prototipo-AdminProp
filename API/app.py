from flask import Flask, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import *
from flask import jsonify
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
engine = create_engine(f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
app.config["JWT_SECRET_KEY"] = "una_clave_super_segura"  # cambiala en producción
app.config["JWT_COOKIE_NAME"] = "access_token_cookie"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
jwt = JWTManager(app)

def send_query(query: str) -> tuple[bool, any]:
    """Send a query to the database and return the result, if any error occurred return False and the error message."""
    try:
        conn = engine.connect()
        result = conn.execute(text(query))
        conn.commit()
        conn.close()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err.__cause__}")
        return False, str(err.__cause__)
    return True, result

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {"error": "Email and password are required"}, 400

    query = "SELECT * FROM users WHERE email=:email"

    try:
        conn = engine.connect()
        result = conn.execute(text(query), {"email": email, "password": password})
        user = result.mappings().fetchone()
        conn.close()

        if user:
            user_id = user["id"]
            if not (check_password_hash(user["password"], password)):
                return jsonify({"error": "Credenciales incorrectas"}), 401
            access_token = create_access_token(identity=str(user_id))  # <-- convertir a str
            resp = jsonify({"access_token_cookie": access_token})
            resp.set_cookie("access_token_cookie", access_token, httponly=True, secure=False)
            return resp, 200
        else:
            return jsonify({"error": "Credenciales incorrectas"}), 401

    except Exception as e:
        if DEBUG:
            print(f"DB_ERROR: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/consortiums", methods=["GET"])
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
    conn = engine.connect()
    result = conn.execute(text(query), {"user_id": user_id})
    rows = result.mappings().all()
    conn.close()

    consortiums = [
        {"id": row["id"], "address": row["address"], "ufs_amount": int(row["ufs_amount"] or 0)}
        for row in rows
    ]
    return jsonify({"consortiums": consortiums}), 200


@app.route("/functional_units", methods=["GET"])
def get_functional_units():
    consortium_id = request.args.get("consortium_id", type=int)

    query = """
        SELECT f.id, f.unit_number, f.unit_name, f.surface, f.surface_percentage,
               f.tenant, f.debt, c.address AS consortium_address
        FROM functional_units f
        JOIN consortiums c ON f.consortium = c.id
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
            "consortium_address": row.consortium_address,
            "surface": float(row.surface),
            "debt": float(row.debt)
        })

    return jsonify({"functional_units": functional_units}), 200

@app.route("/functional_unit", methods=["GET"])
def get_functional_unit():
    consortium_id = request.args.get("consortium_id", type=int)
    unit_id = request.args.get("unit_id", type=int)

    if unit_id is None:
        return {"error": "Se requiere unit_id"}, 400

    query = """
        SELECT f.id, f.unit_number, f.unit_name, f.surface, f.surface_percentage,
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

@app.route("/payments", methods=["GET"])
def get_payments():
    tenant_name = request.args.get("tenant_name", type=str)
    id_unit = request.args.get("id_unit", type=int)

    if tenant_name is None or id_unit is None:
        return {"error": "tenant_name and id_unit are required"}, 400

    query = """
        SELECT p.id, p.amount, p.date
        FROM payments p
        WHERE p.tenant = :tenant_name AND p.functional_unit = :id_unit
        ORDER BY p.date DESC
    """

    params = {"tenant_name": tenant_name, "id_unit": id_unit}

    try:
        conn = engine.connect()
        result = conn.execute(text(query), params)
        rows = result.fetchall()
        conn.close()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    payments = []
    latest_payment = 0
    for i, row in enumerate(rows):
        payments.append({
            "id": row.id,
            "amount": float(row.amount),
            "date": str(row.date)
        })
        if i == 0:
            latest_payment = float(row.amount)

    response = {
        "tenant": tenant_name,
        "payments": payments,
        "latest_payment": latest_payment,
    }

    return jsonify(response), 200

@app.route("/expenses", methods=["GET"])
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

@app.route("/owners_reports", methods=["GET"])
def get_owners_reports():
    consortium_id = request.args.get("consortium_id", type=int)
    month_of_year = request.args.get("month_of_year")  # "YYYY-MM"

    if consortium_id is None or month_of_year is None:
        return {"error": "consortium_id and month_of_year are required"}, 400

    try:
        datetime.strptime(month_of_year, "%Y-%m")
    except ValueError:
        return {"error": "month_of_year must be in format YYYY-MM"}, 400

    query_payments = """
        SELECT COALESCE(SUM(amount),0) AS total_payments
        FROM payments
        WHERE consortium = :consortium_id
          AND DATE_FORMAT(date, '%Y-%m') = :month_of_year
    """

    query_expenses = """
        SELECT COALESCE(SUM(amount),0) AS total_expenses
        FROM common_expenses
        WHERE consortium = :consortium_id
          AND DATE_FORMAT(date, '%Y-%m') = :month_of_year
    """

    params = {"consortium_id": consortium_id, "month_of_year": month_of_year}

    try:
        with engine.connect() as conn:
            total_payments_row = conn.execute(text(query_payments), params).fetchone()
            total_income = float(total_payments_row.total_payments)

            total_expenses_row = conn.execute(text(query_expenses), params).fetchone()
            total_outcome = float(total_expenses_row.total_expenses)

            addr_row = conn.execute(
                text("SELECT address FROM consortiums WHERE id = :id"),
                {"id": consortium_id}
            ).fetchone()
            consortium_address = addr_row.address if addr_row else None

            admin_commission_row = conn.execute(
                text("SELECT admin_comission FROM consortiums WHERE id = :id"),
                {"id": consortium_id}
            ).fetchone()
            admin_commission = float(admin_commission_row.admin_comission) if admin_commission_row else 0.0
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    admin_fee = (total_income - total_outcome) * admin_commission
    net_income = total_income - total_outcome - admin_fee

    owner_report = {
        "consortium_address": consortium_address,
        "month_of_year": month_of_year,
        "total_incomes": total_income,
        "total_outcomes": total_outcome,
        "administration_percentage": admin_commission,
        "administration_fee": admin_fee,
        "net_income": net_income,
    }

    return jsonify({"owner_report": owner_report}), 200

@app.route("/administration_fee", methods=["GET"])
def get_administration_fee():
    month_of_year = request.args.get("month_of_year")  # "YYYY-MM"

    if month_of_year is None:
        return {"error": "month_of_year is required"}, 400

    try:
        datetime.strptime(month_of_year, "%Y-%m")
    except ValueError:
        return {"error": "month_of_year must be in format YYYY-MM"}, 400

    query = """
        SELECT COALESCE(SUM(p.amount),0) AS total_payments, c.address, c.admin_comission
        FROM payments p
        JOIN consortiums c ON p.consortium = c.id
        WHERE DATE_FORMAT(date, '%Y-%m') = :month_of_year
        GROUP BY c.id, c.address, c.admin_comission
    """

    params = {"month_of_year": month_of_year}

    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            rows = result.fetchall()
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    details = []
    total_administration_fee = 0
    for row in rows:
        row_admin_commission = float(row.admin_comission)
        row_total_income = float(row.total_payments)
        row_admin_fee = row_total_income * row_admin_commission
        total_administration_fee += row_admin_fee
        details.append({
            "consortium_address": row.address,
            "administration_percentage": row_admin_commission,
            "net_income": row_total_income,
            "administration_fee": row_admin_fee,
        })

    administration_fee = {
        "month_of_year": month_of_year,
        "total_administration_fee": total_administration_fee,
        "details": details,
    }

    return jsonify({"administration_fee": administration_fee}), 200

@app.route("/functional_unit/<int:unit_id>", methods=["DELETE"])
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

@app.route("/consortiums/<int:consortium_id>", methods=["DELETE"])
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

@app.route("/expenses/<int:expense_id>", methods=["DELETE"])
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

@app.route("/payments/<int:payment_id>", methods=["DELETE"])
def delete_payment(payment_id):
    query = """
        DELETE FROM payments
        WHERE id = :payment_id 
    """

    try:
        with engine.begin() as conn:
            result = conn.execute(text(query), {"payment_id": payment_id})
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": f"Payment {payment_id} deleted"}, 200

@app.route("/users/register", methods=["POST"])
def post_register():

    data = request.get_json()
    name = data.get("name")
    surname = data.get("surname")
    email = data.get("email")
    password = generate_password_hash(data.get("password"), method="pbkdf2:sha256")

    query = """
            INSERT INTO users (name, surname, email, password)
            VALUES (:name, :surname, :email, :password)
            """

    params = {}
    params["name"] = name
    params["surname"] = surname
    params["email"] = email
    params["password"] = password

    try:
        with engine.begin() as conn:
            result = conn.execute(text(query), params)
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": f"User {name} created"}, 201

@app.route("/payments", methods=["POST"])
@jwt_required()
def post_payments():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    tenant_name = data.get("tenant_name")
    id_unit = data.get("id_unit")
    date = data.get("date")
    amount = data.get("amount")

    query = """
            INSERT INTO payments (consortium, tenant, functional_unit, date, amount)
            VALUES (:consortium_id, :tenant_name, :id_unit, :date, :amount)
            """

    query_get_consortium = """
                            SELECT c.id
                            FROM consortiums c
                            WHERE c.user_id = :user_id
                           """

    params = {}
    params["tenant_name"] = tenant_name
    params["id_unit"] = id_unit
    params["date"] = date
    params["amount"] = amount

    try:
        with engine.begin() as conn:
            result_consortium_id = conn.execute(text(query_get_consortium), {"user_id": user_id})
            consortium_id = result_consortium_id.mappings().first()
            params["consortium_id"] = consortium_id["id"]
            result = conn.execute(text(query), params)
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": f"payment for unit {id_unit} created"}, 201

@app.route("/consortiums", methods=["POST"])
@jwt_required()
def post_consortiums():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    name = data.get("name")
    address = data.get("address")
    admin_comission = data.get("admin_comission")
    owner_name = data.get("owner_name")

    query = """
            INSERT INTO consortiums (name, address, owner_name, admin_comission, user_id)
            VALUES (:name, :address, :owner_name, :admin_comission, :user_id)
            """

    params = {}
    params["name"] = name
    params["address"] = address
    params["owner_name"] = owner_name
    params["admin_comission"] = admin_comission
    params["user_id"] = user_id

    try:
        with engine.begin() as conn:
            result = conn.execute(text(query), params)
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

    return {"message": f"consortium {name} created"}, 201

if __name__ == "__main__":
    app.run("0.0.0.0", API_PORT, debug=DEBUG=="True")