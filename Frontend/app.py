import requests
from flask import Flask, render_template, request, make_response, redirect, url_for, flash
from config import *
import datetime
import os

API_URL = f"{API_HOST}:{API_PORT}"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'admin'


# ------------------------------ ERROR HANDLER --------------------------------

app.config['TRAP_HTTP_EXCEPTIONS'] = True
@app.errorhandler(Exception)
def error(e):
    return render_template("error.html",error=e)

#------------------------------- INDEX ----------------------------------------

@app.route("/")
def base():
    return render_template("index.html")

def require_login():
    if not request.cookies.get("access_token_cookie"):
        return redirect(url_for("base"))

@app.route("/inicio")
def inicio():
    login_check = require_login()
    if login_check:
        return login_check
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

@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for("base")))
    resp.delete_cookie("access_token_cookie")
    return resp

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        surname = request.form.get("surname")
        email = request.form.get("email")
        password = request.form.get("password")
        response = requests.post(f"{API_URL}/users/register", json={"name":name, "surname":surname, "email": email, "password": password})
        if response.status_code == 201:
            flash('¡Registro exitoso! Revisa tu email para verificar tu cuenta.', 'success')
            return redirect(url_for("login"))
        else:
            error_msg = response.json().get("error", "Error desconocido")
            return render_template("register.html", error=error_msg)
    return render_template("register.html")

@app.route("/clientes")
def clientes():
    login_check = require_login()
    if login_check:
        return login_check
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}

    # Llamamos al nuevo endpoint de la API
    response = requests.get(f"{API_URL}/api/clients", cookies=cookies)
    addresses_response = requests.get(f"{API_URL}/api/consortiums/addresses", cookies=cookies)

    clients_data = []
    dashboard_data = {}
    if response.status_code == 200 and addresses_response.status_code == 200:
        clients_payload = response.json().get("response", [])
        addresses_payload = addresses_response.json()
        clients_data = clients_payload.get("clients", [])
        dashboard_data = {
            "deuda_total": clients_payload.get("deuda_total", 0),
            "ingresos": clients_payload.get("ingresos", 0),
            "direcciones": addresses_payload.get("addresses", [])
        }
    else:
        # Manejar el error, tal vez mostrando un mensaje
        print(f"Error al obtener clientes: {response.status_code}")

    return render_template("clientes.html", active_page='clientes', clients=clients_data, dashboard_data=dashboard_data)

@app.route("/consorcios", methods=["GET", "POST"])
def consorcios():
    login_check = require_login()
    if login_check:
        return login_check

    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}
    #----------POST----------#
    if request.method == "POST":
        name = request.form.get("name")
        address = request.form.get("address")
        admin_commission = request.form.get("admin_commission")
        owner_name = request.form.get("owner_name")
        response = requests.post(f"{API_URL}/consortiums", json={"name": name, "address": address, "admin_commission": admin_commission, "owner_name": owner_name}, cookies=cookies)
        if response.status_code == 201:
            return redirect(url_for("consorcios"))
        else:
            error_msg = response.json().get("error", "Error desconocido")
            return render_template("consorcios.html", error=error_msg)
    #----------GET----------#
    response = requests.get(f"{API_URL}/consortiums", cookies=cookies)
    consortiums = response.json().get("consortiums", [])
    free_limit_reached = False
    if len(consortiums) > 0:
        free_limit_reached = True
    return render_template("consorcios.html", active_page='consorcios', free_limit_reached=free_limit_reached, consortiums=consortiums)

@app.route("/consorcios/<int:consortium_id>/unidades_funcionales", methods=["GET", "POST"])
def unidades_funcionales(consortium_id):
    login_check = require_login()
    if login_check:
        return login_check
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}

    if request.method == "POST":
        unit_number = request.form.get("unit_number")
        unit_name = request.form.get("unit_name")
        surface_area = request.form.get("surface_area")
        params = {
            "unit_number": unit_number,
            "unit_name": unit_name,
            "surface": surface_area,
            "consortium_id": consortium_id
        }
        response = requests.post(f"{API_URL}/functional_units", json=params, cookies=cookies)
        if response.status_code == 201:
            return redirect(url_for("unidades_funcionales", consortium_id=consortium_id))
    response = requests.get(f"{API_URL}/functional_units", params={"consortium_id": consortium_id}, cookies=cookies).json()
    functional_units = response.get("functional_units", [])
    address = response.get("address", "Dirección")
    return render_template("unidades_funcionales.html", active_page='consorcios', units=functional_units, consortium_id=consortium_id, address=address)

@app.route("/consorcios/<int:consortium_id>/unidades_funcionales/<int:unit_id>")
def unidad_funcional(consortium_id, unit_id):
    login_check = require_login()
    if login_check:
        return login_check
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}
    response = requests.get(f"{API_URL}/functional_unit", params={"consortium_id": consortium_id, "unit_id": unit_id}, cookies=cookies).json()
    unit = response["functional_unit"] if "functional_unit" in response else None
    return render_template("vista_local.html", active_page='consorcios', unit=unit, consortium_id=consortium_id)

@app.route("/consorcios/<int:consortium_id>/unidades_funcionales/<int:unit_id>/desocupar", methods=["PATCH"])
def desocupar_unidad(consortium_id, unit_id):
    login_check = require_login()
    if login_check:
        return login_check
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}
    response = requests.patch(
        f"{API_URL}/functional_units/{unit_id}",
        json={"tenant": ""},
        cookies=cookies
    )
    return redirect(url_for("unidad_funcional", consortium_id=consortium_id, unit_id=unit_id))

@app.route("/consorcios/<int:consortium_id>/unidades_funcionales/<int:unit_id>/ocupar", methods=["PATCH"])
def ocupar_unidad(consortium_id, unit_id):
    login_check = require_login()
    if login_check:
        return login_check
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}
    tenant = request.json.get("tenant")
    response = requests.patch(
        f"{API_URL}/functional_units/{unit_id}",
        json={"tenant": tenant},
        cookies=cookies
    )
    return redirect(url_for("unidad_funcional", consortium_id=consortium_id, unit_id=unit_id))

@app.route('/consorcios/<int:consortium_id>/unidades_funcionales/<int:unit_id>/editar_alquiler', methods=['PATCH'])
def editar_alquiler(consortium_id, unit_id):
    login_check = require_login()
    if login_check:
        return login_check
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}
    new_rent = request.json.get("rent_value")
    response = requests.patch(
        f"{API_URL}/functional_units/{unit_id}",
        json={"rent_value": new_rent},
        cookies=cookies
    )
    return redirect(url_for("unidad_funcional", consortium_id=consortium_id, unit_id=unit_id))

@app.route("/consorcios/<int:consortium_id>/unidades_funcionales/<int:unit_id>/eliminar", methods=["DELETE"])
def eliminar_unidad(consortium_id, unit_id):
    login_check = require_login()
    if login_check:
        return login_check
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}
    response = requests.delete(f"{API_URL}/functional_unit/{unit_id}", cookies=cookies)
    return redirect(url_for("unidades_funcionales", consortium_id=consortium_id))

@app.route("/pagos/<int:consortium_id>/<int:unit_id>/<tenant>", methods=["GET"])
def pagos(consortium_id, unit_id, tenant):
    login_check = require_login()
    if login_check:
        return login_check
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}
    params = {
        "tenant_name": tenant,
        "id_unit": unit_id,
        "consortium_id": consortium_id
    }
    response = requests.get(f"{API_URL}/payments", params=params, cookies=cookies)
    try:
        data = response.json()
        payments = data["payments"]
    except Exception:
        return jsonify({"error": "Error inesperado en el backend"}), 500

    return payments, response.status_code

@app.route("/registrar_pago/<int:payment_id>", methods=["DELETE"])
def registrar_pago(payment_id):
    login_check = require_login()
    if login_check:
        return login_check
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}
    response = requests.delete(f"{API_URL}/payments/{payment_id}", cookies=cookies)

@app.route("/rendiciones")
def rendiciones():
    login_check = require_login()
    if login_check:
        return login_check
    return render_template("rendiciones.html", active_page='rendiciones')

@app.route("/comisiones")
def comisiones():
    login_check = require_login()
    if login_check:
        return login_check
    return render_template("comisiones.html", active_page='comisiones')

@app.route("/configuracion")
def configuracion():
    login_check = require_login()
    if login_check:
        return login_check
    return render_template("configuracion.html", active_page='configuracion')

@app.route("/suscribirse")
def suscribirse():
    return render_template("suscribirse.html")

if __name__ == "__main__":
    app.run("0.0.0.0", port=FRONT_PORT, debug=DEBUG=="True")
