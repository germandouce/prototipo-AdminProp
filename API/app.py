import os
from urllib.parse import quote_plus

import requests
import sendgrid
from sendgrid.helpers.mail import *
from flask import Blueprint, request, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask, request, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import *
from flask import jsonify
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine

from routes.consortiums import consortiums_bp
from routes.functional_units import functional_units_bp
from routes.debts import debts_bp
from routes.expenses import expenses_bp
from routes.expenses_record import expenses_record_bp
from routes.clients import clients_bp
from database import engine, DEBUG
from flask import redirect
from urllib.parse import quote_plus

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
app.register_blueprint(debts_bp)
app.register_blueprint(expenses_bp)
app.register_blueprint(expenses_record_bp)
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

owners_reports_bp = Blueprint("owners_reports", __name__)

@owners_reports_bp.route("/owners_reports", methods=["GET"])
def owners_reports():
    try:
        consortium_id = request.args.get("consortium_id", type=int)
        month_of_year = request.args.get("month_of_year")  # formato "YYYY-MM"

        if not consortium_id or not month_of_year:
            return jsonify({"error": "Parámetros 'consortium_id' y 'month_of_year' requeridos"}), 400

        # ---- Datos del consorcio ----
        query_consortium = """
                           SELECT address, admin_commission
                           FROM consortiums
                           WHERE id = :consortium_id \
                           """
        with engine.connect() as conn:
            consortium = conn.execute(text(query_consortium), {"consortium_id": consortium_id}).mappings().fetchone()

        if not consortium:
            return jsonify({"error": "Consorcio no encontrado"}), 404

        consortium_address = consortium["address"]
        admin_percentage = float(consortium["admin_commission"]) / 100.0

        # ---- Ingresos del mes ----
        query_incomes = """
                        SELECT COALESCE(SUM(amount), 0) AS total_incomes
                        FROM payments
                        WHERE consortium = :consortium_id
                          AND DATE_FORMAT(date, '%Y-%m') = :month_of_year \
                        """

        # ---- Gastos del mes ----
        query_outcomes = """
                         SELECT COALESCE(SUM(amount), 0) AS total_outcomes
                         FROM common_expenses
                         WHERE consortium = :consortium_id
                           AND DATE_FORMAT(date, '%Y-%m') = :month_of_year \
                         """

        # ---- Detalle de gastos comunes ----
        query_expenses_list = """
                              SELECT description, amount, date
                              FROM common_expenses
                              WHERE consortium = :consortium_id
                                AND DATE_FORMAT(date, '%Y-%m') = :month_of_year \
                              """

        params = {"consortium_id": consortium_id, "month_of_year": month_of_year}

        with engine.connect() as conn:
            total_incomes = float(conn.execute(text(query_incomes), params).mappings().fetchone()["total_incomes"])
            total_outcomes = float(conn.execute(text(query_outcomes), params).mappings().fetchone()["total_outcomes"])
            expenses_rows = conn.execute(text(query_expenses_list), params).mappings().all()

        expenses_list = [
            {"description": r["description"], "amount": float(r["amount"]), "date": str(r["date"])}
            for r in expenses_rows
        ]

        # ---- Cálculo de comisión y saldo ----
        administration_fee = total_incomes * admin_percentage
        net_income = total_incomes - total_outcomes - administration_fee

        owner_report = {
            "consortium_address": consortium_address,
            "month_of_year": month_of_year,
            "total_incomes": total_incomes,
            "total_outcomes": total_outcomes,
            "administration_percentage": admin_percentage,
            "administration_fee": administration_fee,
            "net_income": net_income,
            "common_expenses": expenses_list
        }

        return jsonify({"owner_report": owner_report}), 200

    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return jsonify({"error": str(err)}), 500

    except Exception as e:
        print("Error en /owners_reports:", e)
        return jsonify({"error": str(e)}), 500

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
        SELECT COALESCE(SUM(p.amount),0) AS total_payments, c.address, c.admin_commission
        FROM payments p
        JOIN consortiums c ON p.consortium = c.id
        WHERE DATE_FORMAT(date, '%Y-%m') = :month_of_year
        GROUP BY c.id, c.address, c.admin_commission
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
        row_admin_commission = float(row.admin_commission)
        row_total_income = float(row.total_payments)
        row_admin_fee = row_total_income * (row_admin_commission/100)
        total_administration_fee += row_admin_fee
        details.append({
            "consortium_address": row.address,
            "administration_percentage": row_admin_commission,
            "net_income": row_total_income,
            "administration_fee": row_admin_fee,
        })

    response = {
        "month_of_year": month_of_year,
        "total_administration_fee": total_administration_fee,
        "details": details,
    }

    return response, 200

@app.route("/users/register", methods=["POST"])
def post_register():
    data = request.get_json()
    name = data.get("name")
    surname = data.get("surname")
    email = data.get("email")
    password = generate_password_hash(data.get("password"), method="pbkdf2:sha256")

    if not all([name, surname, email, password]):
        return {"error": "Faltan datos requeridos"}, 400

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
            identity=email,
            additional_claims={"action": "verify_email"}
        )
        verify_link = f"{API_BASE_URL}{url_for('verify_email', token=verify_token)}"
        sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
        from_email = FROM_EMAIL
        to = email
        subject = "Verificá tu cuenta"
        content = f"Hola {name}, hacé clic en este enlace para verificar tu cuenta:\n\n{verify_link}\n\nEl enlace expira en 1 hora."

        mail = Mail(
            from_email=from_email,
            to_emails=to,
            subject=subject,
            plain_text_content=content
        )
        mail_json = mail.get()
        response = sg.client.mail.send.post(request_body=mail_json)

        return {"message": "Usuario creado. Revisá tu correo para verificar la cuenta."}, 201
    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return {"error": "El email ya está registrado."}, 400
    except Exception as e:
        if DEBUG:
            print(f"EMAIL_ERROR: {e}")
        return {"error": f"Error al enviar el email de verificación: {e}"}, 500

@app.route("/verify/<token>")
def verify_email(token):
    try:
        decoded = decode_token(token)
        email = decoded["sub"]  # identidad del token
        action = decoded.get("action")

        if action != "verify_email":
            error_message = quote_plus("Token inválido")
            return redirect(f"{FRONTEND_URL}/verificacion?status=error&message={error_message}")

    except Exception as e:
        error_message = quote_plus("error: Token inválido o expirado")
        return redirect(f"{FRONTEND_URL}/verificacion?status=error&message={error_message}")

    query = """
        UPDATE users
        SET verified = TRUE
        WHERE email = :email
    """

    with engine.begin() as conn:
        result = conn.execute(text(query), {"email": email})

    if result.rowcount == 0:
        error_message = quote_plus("El usuario no fue encontrado.")
        return redirect(f"{FRONTEND_URL}/verificacion?status=error&message={error_message}")

    return redirect(f"{FRONTEND_URL}/verificacion?status=success")

@app.route("/users", methods=["GET"])
@jwt_required()
def get_user():
    user_id = int(get_jwt_identity())

    query = """
            SELECT u.name, u.surname
            FROM users u
            WHERE u.id = :user_id;
            """

    try:
        with engine.connect() as conn:
            user_row = conn.execute(text(query), {"user_id": user_id}).fetchone()

        if not user_row:
            return jsonify({"error": "User not found"}), 404

    except SQLAlchemyError as err:
        if DEBUG:
            print(f"DB_ERROR: {err}")
        return jsonify({"error": "A database error occurred"}), 500

    response = {
        "name": user_row.name,
        "surname": user_row.surname
    }

    return jsonify(response), 200

app.register_blueprint(owners_reports_bp)

if __name__ == "__main__":
    app.run("0.0.0.0", API_PORT, debug=DEBUG=="True")