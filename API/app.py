import os
from flask import Flask, request, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import *
from flask import jsonify
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from sqlalchemy import create_engine

from routes.consortiums import consortiums_bp
from routes.functional_units import functional_units_bp
from routes.payments import payments_bp
from routes.expenses import expenses_bp
from routes.clients import clients_bp
from database import engine, DEBUG
from flask_mail import Mail, Message

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "una_clave_super_segura"  # cambiala en producción
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_COOKIE_NAME"] = "access_token_cookie"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
jwt = JWTManager(app)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "gsdia186@gmail.com"
app.config["MAIL_PASSWORD"] = "cctz dmyf sowk jqhh"
mail = Mail(app)

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

app.register_blueprint(consortiums_bp)
app.register_blueprint(functional_units_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(expenses_bp)
app.register_blueprint(clients_bp, url_prefix='/api')

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
        result = conn.execute(text(query), {"email": email})
        user = result.mappings().fetchone()
        conn.close()

        if user:
            if not (check_password_hash(user["password"], password)):
                return jsonify({"error": "Credenciales incorrectas"}), 401
            if not user["verified"]:
                return jsonify(
                    {"error": "La cuenta no ha sido verificada. Por favor, revisa tu correo electrónico."}), 403
            user_id = user["id"]
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
        verify_token = create_access_token(
            identity=email, additional_claims={"action": "verify_email"}
        )
        verify_link = f"{API_BASE_URL}{url_for('verify_email', token=verify_token)}"
        msg = Message(
            "Verificá tu cuenta",
            sender="gsdia186@gmail.com",
            recipients=[email],
        )
        msg.body = f"Hola {name}, hacé clic en este enlace para verificar tu cuenta:\n\n{verify_link}\n\nEl enlace expira en 1 hora."
        mail.send(msg)

        return {"message": "Usuario creado. Revisá tu correo para verificar la cuenta."}, 201
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": str(err)}, 500

@app.route("/verify/<token>")
def verify_email(token):
    try:
        decoded = decode_token(token)
        email = decoded["sub"]  # identidad del token
        action = decoded.get("action")

        if action != "verify_email":
            return {"error": "Token inválido"}, 400

    except Exception as e:
        return {"error": f"Token inválido o expirado: {e}"}, 400

    query = """
        UPDATE users
        SET verified = TRUE
        WHERE email = :email
    """

    with engine.begin() as conn:
        result = conn.execute(text(query), {"email": email})

    if result.rowcount == 0:
        return {"error": "Usuario no encontrado"}, 404

    return {"message": "Cuenta verificada con éxito. Ya podés iniciar sesión."}, 200

if __name__ == "__main__":
    app.run("0.0.0.0", API_PORT, debug=DEBUG=="True")