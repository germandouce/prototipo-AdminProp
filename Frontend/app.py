import requests
from flask import Flask, render_template, request, make_response, redirect, url_for
from config import *
import datetime
import os

API_URL = f"{API_HOST}:{API_PORT}"
app = Flask(__name__)


# ------------------------------ ERROR HANDLER --------------------------------

app.config['TRAP_HTTP_EXCEPTIONS'] = True
@app.errorhandler(Exception)
def error(e):
    return render_template("error.html",error=e)

#------------------------------- INDEX ----------------------------------------

@app.route("/")
def base():
    return render_template("index.html")

@app.route("/inicio")
def inicio():
    return render_template("inicio.html", active_page='inicio')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        response = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
        if response.status_code == 200:
            return redirect(url_for("inicio"))
        else:
            error_msg = response.json().get("error", "Error desconocido")
            return render_template("login.html", error=error_msg)
    return render_template("login.html")

@app.route("/clientes")
def clientes():
    return render_template("clientes.html", active_page='clientes')

@app.route("/consorcios")
def consorcios():
    return render_template("consorcios.html", active_page='consorcios')

@app.route("/rendiciones")
def rendiciones():
    return render_template("rendiciones.html", active_page='rendiciones')

@app.route("/comisiones")
def comisiones():
    return render_template("comisiones.html", active_page='comisiones')

@app.route("/configuracion")
def configuracion():
    return render_template("configuracion.html", active_page='configuracion')

@app.route("/unidades_funcionales")
def unidades_funcionales():
    functional_units = [
        {
            "id": 0,
            "unit_number": "001",
            "unit_name": "1A",
            "occupation_status": True,
            "tentant": "John Doe",
            "consortium_address": "Av. Paseo Colón 850",
            "rent_value": 1500.00,
            "expenses_value": 300.00,
            "surface":10,
            "debt": 0.00
        },
        {
            "id": 1,
            "unit_number": "002",
            "unit_name": "1B",
            "occupation_status": False,
            "tentant": None,
            "consortium_address": "Av. Paseo Colón 850",
            "rent_value": 1200.00,
            "expenses_value": 250.00,
            "surface":8,
            "debt": 150.00
        },
        {
            "id": 2,
            "unit_number": "003",
            "unit_name": "2A",
            "occupation_status": True,
            "tentant": "Jane Smith",
            "consortium_address": "Av. Paseo Colón 850",
            "rent_value": 1800.00,
            "expenses_value": 350.00,
            "surface":12,
            "debt": 0.00
        }
    ]
    return render_template("unidades_funcionales.html", active_page='consorcios', units=functional_units)

@app.route("/unidad_funcional")
def unidad_funcional():
    return render_template("vista_local.html", active_page='consorcios')

if __name__ == "__main__":
    app.run("0.0.0.0", port=FRONT_PORT, debug=DEBUG=="True")
