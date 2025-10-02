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
            token = response.json().get("access_token_cookie")
            resp = make_response(redirect(url_for("inicio")))
            resp.set_cookie("access_token_cookie", token, httponly=True, secure=False)
            return resp
        else:
            error_msg = response.json().get("error", "Error desconocido")
            return render_template("login.html", error=error_msg)
    return render_template("login.html")
#    DESCOMENTAR ARRIBA Y BORRAR ABAJO PARA EL LOGIN FUNCIONAL
#    return redirect(url_for("inicio"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        surname = request.form.get("surname")
        email = request.form.get("email")
        password = request.form.get("password")
        response = requests.post(f"{API_URL}/users/register", json={"name":name, "surname":surname, "email": email, "password": password})
        if response.status_code == 201:
            return redirect(url_for("login"))
        else:
            error_msg = response.json().get("error", "Error desconocido")
            return render_template("register.html", error=error_msg)
    return render_template("register.html")

@app.route("/clientes")
def clientes():
    return render_template("clientes.html", active_page='clientes')

@app.route("/consorcios", methods=["GET", "POST"])
def consorcios():
    #----------POST----------#
    if request.method == "POST":
        name = request.form.get("name")
        address = request.form.get("address")
        response = requests.post(f"{API_URL}/consortiums", json={"name": name, "address": address})
        if response.status_code == 201:
            return redirect(url_for("consorcios"))
        else:
            error_msg = response.json().get("error", "Error desconocido")
            return render_template("consorcios.html", error=error_msg)
    #----------GET----------#
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}
    response = requests.get(f"{API_URL}/consortiums", cookies=cookies)
    consortiums = response.json().get("consortiums", [])
    return render_template("consorcios.html", active_page='consorcios', consortiums=consortiums)


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
    consortium_id = request.args.get("consortium_id")
    response = requests.get(f"{API_URL}/functional_units", params={"consortium_id": consortium_id}).json()
    functional_units = response["functional_units"] if "functional_units" in response else []
    return render_template("unidades_funcionales.html", active_page='consorcios', units=functional_units, consortium_id=consortium_id)

@app.route("/unidad_funcional")
def unidad_funcional():
    consortium_id = request.args.get("consortium_id")
    unit_id = request.args.get("unit_id")
    response = requests.get(f"{API_URL}/functional_unit", params={"consortium_id": consortium_id, "unit_id": unit_id}).json()
    unit = response["functional_unit"] if "functional_unit" in response else None
    return render_template("vista_local.html", active_page='consorcios', unit=unit)

if __name__ == "__main__":
    app.run("0.0.0.0", port=FRONT_PORT, debug=DEBUG=="True")
