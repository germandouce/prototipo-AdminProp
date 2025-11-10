import requests
from flask import Flask, render_template, request, make_response, redirect, url_for, flash
from config import *
from flask import jsonify
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
        return redirect(url_for("login"))

@app.route("/inicio")
def inicio():
    login_check = require_login()
    if login_check:
        return login_check
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}
    response = requests.get(f"{API_URL}/users", cookies=cookies)
    if response.status_code == 200:
        name = response.json().get("name", [])
        surname = response.json().get("surname", [])
    else:
        error_msg = response.json().get("error", "Error desconocido")
        return render_template("login.html", error=error_msg)
    response = requests.get(f"{API_URL}/debts_total", cookies=cookies)
    if response.status_code == 200:
        total_debts = response.json().get("total", 0)
    else:
        error_msg = response.json().get("error", "Error desconocido")
        return render_template("login.html", error=error_msg)

    date = datetime.datetime.now()
    year_month = date.strftime('%Y-%m')
    response = requests.get(f"{API_URL}/administration_fee", params={"month_of_year":year_month}, cookies=cookies)
    if response.status_code == 200:
        administration_income = response.json().get("total_administration_fee", 0)
    else:
        error_msg = response.json().get("error", "Error desconocido")
        return render_template("login.html", error=error_msg)

    addresses_response = requests.get(f"{API_URL}/api/consortiums/addresses", cookies=cookies)
    addresses_response = addresses_response.json().get("addresses", [])
    dashboard_data = {
        "direcciones": addresses_response
    }

    response = requests.get(f"{API_URL}/payments_total", cookies=cookies)
    if response.status_code == 200:
        total_payments = response.json().get("total", 0)
    else:
        error_msg = response.json().get("error", "Error desconocido")
        return render_template("login.html", error=error_msg)

    return render_template("inicio.html", active_page='inicio', name=name, surname=surname, total_debts=total_debts, administration_income=administration_income, dashboard_data=dashboard_data, total_payments=total_payments)

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

@app.route("/deudores")
def clientes():
    login_check = require_login()
    if login_check:
        return login_check
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}

    response = requests.get(f"{API_URL}/api/clients", cookies=cookies)

    clients_data = []
    dashboard_data = {}
    if response.status_code == 200:
        clients_payload = response.json().get("response", [])
        clients_data = clients_payload.get("clients", [])
        dashboard_data = {
            "deuda_total": clients_payload.get("deuda_total", 0),
            "ingresos": clients_payload.get("ingresos", 0),
            "direcciones": clients_payload.get("direcciones", []),
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
        surface = request.form.get("surface")
        response = requests.post(f"{API_URL}/consortiums", json={"name": name, "address": address, "admin_commission": admin_commission, "owner_name": owner_name, "surface": surface}, cookies=cookies)
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

@app.route("/consorcios/<int:consortium_id>/eliminar", methods=["DELETE"])
def eliminar_consorcio(consortium_id):
    login_check = require_login()
    if login_check:
        return login_check
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}
    response = requests.delete(f"{API_URL}/consortiums/{consortium_id}", cookies=cookies)
    return redirect(url_for("consorcios"))

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
    for functional_unit in functional_units:
        if functional_unit["tenant"]:
            functional_unit["debt_state"] = "paid"
            response_debt = requests.get(f"{API_URL}/functional_units/debt", params={"unit_id": functional_unit["id"], "tenant": functional_unit["tenant"]}, cookies=cookies).json()
            debt = response_debt.get("total_debt")
            if float(debt) > 0:
                functional_unit["debt_state"] = "pending"

    consortium_info_response = requests.get(f"{API_URL}/consortium", params={"consortium_id": consortium_id}, cookies=cookies)
    consortium_info = consortium_info_response.json()

    response = requests.get(f"{API_URL}/expenses", params={"consortium_id": consortium_id}, cookies=cookies)
    common_expenses = []
    if response.status_code == 200:
        common_expenses = response.json().get("expenses", [])

    return render_template(
        "unidades_funcionales.html",
        active_page='consorcios',
        units=functional_units,
        consortium_id=consortium_id,
        address=address,
        consortium_info=consortium_info,
        common_expenses=common_expenses
    )

@app.route("/consorcios/<int:consortium_id>/gastos_comunes", methods=["POST"])
def agregar_gasto_comun(consortium_id):
    login_check = require_login()
    if login_check:
        return login_check
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}

    description = request.form.get("description")
    amount = request.form.get("amount")
    date = request.form.get("date")
    params = {
        "description": description,
        "amount": amount,
        "date": date,
        "consortium_id": consortium_id
    }
    response = requests.post(f"{API_URL}/expenses", json=params, cookies=cookies)
    if response.status_code == 201:
        flash("Gasto común agregado exitosamente.", "success")
    else:
        flash("Error al agregar el gasto común.", "error")
    return redirect(url_for("unidades_funcionales", consortium_id=consortium_id))

@app.route("/consorcios/<int:consortium_id>/gastos_comunes", methods=["GET"])
def fetch_gastos_comunes(consortium_id):
    login_check = require_login()
    if login_check:
        return login_check
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}

    if DEBUG:
        print(f"Fetching common expenses for consortium_id: {consortium_id}")  # Debug log

    response = requests.get(f"{API_URL}/expenses", params={"consortium_id": consortium_id}, cookies=cookies)
    if response.status_code == 200:
        data = response.json()
        if DEBUG:
            print(f"Fetched common expenses: {data}")  # Debug log
        return jsonify(data), 200
    else:
        if DEBUG:
            print(f"Error fetching common expenses: {response.status_code}, {response.text}")  # Debug log
        return jsonify({"error": "Error al obtener los gastos comunes"}), response.status_code

@app.route("/consorcios/<int:consortium_id>/unidades_funcionales/<int:unit_id>")
def unidad_funcional(consortium_id, unit_id):
    login_check = require_login()
    if login_check:
        return login_check
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}
    response = requests.get(f"{API_URL}/functional_unit", params={"consortium_id": consortium_id, "unit_id": unit_id}, cookies=cookies).json()
    unit = response["functional_unit"] if "functional_unit" in response else None
    debt = None
    if unit:
        tenant_name = unit.get("tenant")
        if tenant_name:
            response_debt = requests.get(f"{API_URL}/functional_units/debt", params={"unit_id": unit_id, "tenant": tenant_name}, cookies=cookies).json()
            debt = response_debt.get("total_debt")
    return render_template("vista_local.html", active_page='consorcios', unit=unit, consortium_id=consortium_id, debt=debt)

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
    response = requests.get(f"{API_URL}/debts", params=params, cookies=cookies)
    try:
        data = response.json()
        debts = data["debts"]
    except Exception:
        return jsonify({"error": "Error inesperado en el backend"}), 500

    return debts, response.status_code

@app.route("/registrar_pago/<int:payment_id>", methods=["DELETE"])
def registrar_pago(payment_id):
    login_check = require_login()
    if login_check:
        return login_check
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}
    response = requests.delete(f"{API_URL}/debts/{payment_id}", cookies=cookies)
    try:
        data = response.json()
    except Exception:
        data = None

    if response.status_code == 200:
        return jsonify(data), 200
    elif data and "error" in data:
        return jsonify(data), response.status_code
    else:
        return jsonify({"error": "Error desconocido"}), response.status_code

@app.route("/consorcios_json", methods=["GET"])
def consorcios_json():
    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}
    res = requests.get(f"{API_URL}/consortiums", cookies=cookies)
    return jsonify(res.json()), res.status_code

@app.route("/rendiciones", methods=["GET"])
def rendiciones():
    login_check = require_login()
    if login_check:
        return login_check

    # Si la request pide datos (AJAX con parámetros)
    consortium_id = request.args.get("consortium_id", type=int)
    month = request.args.get("month")

    # Si vienen parámetros, significa que el HTML pidió datos → respondemos JSON
    if consortium_id and month:
        # Normalizamos el formato del mes
        if "/" in month:
            mm, yyyy = month.split("/")
            month = f"{yyyy}-{mm.zfill(2)}"

        cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}
        params = {"consortium_id": consortium_id, "month_of_year": month}
        resp = requests.get(f"{API_URL}/owners_reports", params=params, cookies=cookies)

        return jsonify(resp.json()), resp.status_code

    # Si no hay parámetros → render normal de la página HTML vacía
    return render_template("rendiciones.html", active_page="rendiciones")


@app.route("/comisiones")
def comisiones():
    login_check = require_login()
    if login_check:
        return login_check

    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}
    periodo = request.args.get("periodo")
    consorcio_id = request.args.get("consorcio_id", type=int)

    # 1. Obtener TODOS los consorcios SIEMPRE
    response = requests.get(f"{API_URL}/consortiums", cookies=cookies)
    all_consortiums = response.json().get("consortiums", []) if response.status_code == 200 else []

    # 2. Encontrar el consorcio seleccionado (si existe)
    selected_consortium = next((c for c in all_consortiums if c["id"] == consorcio_id), None)

    # 3. Obtener unidades SOLO para el consorcio seleccionado
    #    (Tu código original lo hacía dos veces, esto es más limpio)
    if selected_consortium:
        uf_response = requests.get(
            f"{API_URL}/functional_units",
            params={"consortium_id": selected_consortium["id"], "period": periodo},
            cookies=cookies
        )
        # Añadimos las unidades directamente al diccionario del consorcio seleccionado
        selected_consortium["units"] = uf_response.json().get("functional_units", []) if uf_response.status_code == 200 else []

    # 4. Enviar SIEMPRE la lista completa (all_consortiums) al template
    #    Y también el seleccionado por separado.
    return render_template(
        "comisiones.html",
        active_page='comisiones',
        consortiums=all_consortiums,  # <--- ¡LA LISTA COMPLETA!
        selected_consortium=selected_consortium # <--- El seleccionado (o None)
    )


@app.route("/consortiums/<int:consortium_id>", methods=["PATCH"])
def patch_consortium(consortium_id):
    login_check = require_login()
    if login_check:
        return login_check

    cookies = {"access_token_cookie": request.cookies.get("access_token_cookie")}
    data = request.get_json()

    response = requests.patch(
        f"{API_URL}/consortiums/{consortium_id}",
        json=data,
        cookies=cookies
    )

    return jsonify(response.json()), response.status_code




@app.route("/configuracion")
def configuracion():
    login_check = require_login()
    if login_check:
        return login_check
    return render_template("configuracion.html", active_page='configuracion')

@app.route("/suscribirse")
def suscribirse():
    return render_template("suscribirse.html")

@app.route("/verificacion")
def verification_result():
    status = request.args.get("status")
    message = request.args.get("message")

    return render_template("verificacion.html",
                           status=status,
                           message=message)

if __name__ == "__main__":
    app.run("0.0.0.0", port=FRONT_PORT, debug=DEBUG=="True")
