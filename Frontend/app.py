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
    return render_template("unidades_funcionales.html", active_page='consorcios')

@app.route("/unidad_funcional")
def unidad_funcional():
    return render_template("vista_local.html", active_page='consorcios')

if __name__ == "__main__":
    app.run("0.0.0.0", port=FRONT_PORT, debug=DEBUG=="True")
