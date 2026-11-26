
from flask import Flask, render_template, request, redirect, url_for, session, flash

from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime, date, timedelta

import sqlite3

from crear_db import crear_base_datos, DATABASE


app = Flask(__name__)
app.secret_key = "eternel_clave_secreta_cambiar_en_produccion"


# ==========================================
# CREDENCIALES DEL ADMINISTRADOR
# ==========================================

ADMIN_USUARIO = "admin"
ADMIN_CONTRASENA = "EternelAdmin2026!"


# ==========================================
# CONFIGURACION DE MESAS
# ==========================================

MESAS = {
    "interior": [
        {"numero": 1, "capacidad": 2},
        {"numero": 2, "capacidad": 4},
        {"numero": 3, "capacidad": 2},
        {"numero": 4, "capacidad": 4},
        {"numero": 5, "capacidad": 6},
        {"numero": 6, "capacidad": 4},
        {"numero": 7, "capacidad": 2},
        {"numero": 8, "capacidad": 8},
        {"numero": 9, "capacidad": 4},
        {"numero": 10, "capacidad": 2},
        {"numero": 11, "capacidad": 6},
        {"numero": 12, "capacidad": 4},
        {"numero": 13, "capacidad": 2},
        {"numero": 14, "capacidad": 8},
        {"numero": 15, "capacidad": 4},
        {"numero": 16, "capacidad": 2}
    ],

    "exterior": [
        {"numero": 1, "capacidad": 2},
        {"numero": 2, "capacidad": 4},
        {"numero": 3, "capacidad": 6},
        {"numero": 4, "capacidad": 4},
        {"numero": 5, "capacidad": 2},
        {"numero": 6, "capacidad": 8},
        {"numero": 7, "capacidad": 4},
        {"numero": 8, "capacidad": 2},
        {"numero": 9, "capacidad": 6},
        {"numero": 10, "capacidad": 4},
        {"numero": 11, "capacidad": 2},
        {"numero": 12, "capacidad": 8}
    ]
}


# ==========================================
# CONEXION A LA BASE DE DATOS
# ==========================================

def conectar_db():
    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


# ==========================================
# HORARIOS
# ==========================================

def obtener_horarios():
    horarios = []

    hora = datetime.strptime("10:00", "%H:%M")
    limite = datetime.strptime("22:00", "%H:%M")

    while hora <= limite:
        horarios.append(hora.strftime("%H:%M"))
        hora += timedelta(minutes=30)

    return horarios


def convertir_minutos(hora):
    partes = hora.split(":")
    minutos = int(partes[0]) * 60 + int(partes[1])

    if minutos == 0:
        return 1440

    return minutos


# ==========================================
# COMPROBAR SI UNA MESA ESTA OCUPADA
# ==========================================

def mesa_esta_ocupada(fecha, zona, numero_mesa, hora_inicio, hora_fin):

    conexion = conectar_db()

    reservas = conexion.execute("""
        SELECT hora_inicio, hora_fin
        FROM reservaciones
        WHERE fecha = ?
        AND zona = ?
        AND mesa_numero = ?
        AND estado = 'confirmada'
    """, (fecha, zona, numero_mesa)).fetchall()

    conexion.close()

    nuevo_inicio = convertir_minutos(hora_inicio)
    nuevo_fin = convertir_minutos(hora_fin)

    for reserva in reservas:
        reserva_inicio = convertir_minutos(reserva["hora_inicio"])
        reserva_fin = convertir_minutos(reserva["hora_fin"])

        if nuevo_inicio < reserva_fin and nuevo_fin > reserva_inicio:
            return True

    return False


# ==========================================
# PORTADA
# ==========================================

@app.route("/")
def inicio():
    return render_template("index.html")


# ==========================================
# RESTAURANTE
# ==========================================

@app.route("/restaurante")
def restaurante():
    return render_template("restaurante.html")


# ==========================================
# MENU
# ==========================================

@app.route("/menu")
def menu():
    return render_template("menu.html")


# ==========================================
# CUENTAS
# ==========================================

@app.route("/cuenta")
def cuenta():

    if "cliente_id" in session:
        return redirect(url_for("reservaciones"))

    return render_template("cuenta.html")


# ==========================================
# REGISTRO
# ==========================================

@app.route("/crear-cuenta", methods=["POST"])
def crear_cuenta():

    nombre = request.form.get("nombre", "").strip()
    edad = request.form.get("edad", "").strip()
    telefono = request.form.get("telefono", "").strip()
    correo = request.form.get("correo", "").strip().lower()
    contrasena = request.form.get("contrasena", "")
    confirmar = request.form.get("confirmar", "")

    if not all([nombre, edad, telefono, correo, contrasena, confirmar]):
        flash("Completa todos los campos.", "error")
        return redirect(url_for("cuenta") + "#registro")

    try:
        edad = int(edad)

        if edad < 18 or edad > 120:
            flash("Debes tener al menos 18 años para crear una cuenta.", "error")
            return redirect(url_for("cuenta") + "#registro")

    except ValueError:
        flash("Ingresa una edad válida.", "error")
        return redirect(url_for("cuenta") + "#registro")

    if "@" not in correo or "." not in correo:
        flash("Ingresa un correo electrónico válido.", "error")
        return redirect(url_for("cuenta") + "#registro")

    if len(contrasena) < 8:
        flash("La contraseña debe tener al menos 8 caracteres.", "error")
        return redirect(url_for("cuenta") + "#registro")

    if contrasena != confirmar:
        flash("Las contraseñas no coinciden.", "error")
        return redirect(url_for("cuenta") + "#registro")

    contrasena_segura = generate_password_hash(contrasena)
    conexion = conectar_db()

    try:
        cursor = conexion.execute("""
            INSERT INTO clientes (
                nombre, edad, telefono, correo, contrasena
            )
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, edad, telefono, correo, contrasena_segura))

        conexion.commit()

        session.clear()
        session["cliente_id"] = cursor.lastrowid
        session["cliente_nombre"] = nombre

        flash("¡Tu cuenta fue creada correctamente!", "exito")
        return redirect(url_for("reservaciones"))

    except sqlite3.IntegrityError:
        flash("Ese correo ya está registrado. Inicia sesión.", "error")
        return redirect(url_for("cuenta") + "#registro")

    finally:
        conexion.close()


# ==========================================
# INICIAR SESION DEL CLIENTE
# ==========================================

@app.route("/iniciar-sesion", methods=["POST"])
def iniciar_sesion():

    correo = request.form.get("correo", "").strip().lower()
    contrasena = request.form.get("contrasena", "")

    conexion = conectar_db()

    try:
        cliente = conexion.execute("""
            SELECT * FROM clientes
            WHERE correo = ?
        """, (correo,)).fetchone()

    finally:
        conexion.close()

    if cliente and check_password_hash(cliente["contrasena"], contrasena):

        session.clear()
        session["cliente_id"] = cliente["id"]
        session["cliente_nombre"] = cliente["nombre"]

        return redirect(url_for("reservaciones"))

    flash("Correo o contraseña incorrectos.", "error")
    return redirect(url_for("cuenta") + "#login")


# ==========================================
# CALENDARIO Y HORARIOS
# ==========================================

@app.route("/reservaciones")
def reservaciones():

    if "cliente_id" not in session:
        flash("Primero debes iniciar sesión para reservar.", "error")
        return redirect(url_for("cuenta"))

    return render_template(
        "reservaciones.html",
        nombre=session.get("cliente_nombre"),
        fecha_minima=date.today().isoformat(),
        horarios=obtener_horarios(),
        seleccion=session.get("seleccion_reserva")
    )


# ==========================================
# GUARDAR FECHA Y HORARIO
# ==========================================

@app.route("/continuar-reservacion", methods=["POST"])
def continuar_reservacion():

    if "cliente_id" not in session:
        return redirect(url_for("cuenta"))

    fecha_texto = request.form.get("fecha", "")
    hora_texto = request.form.get("hora", "")
    personas_texto = request.form.get("personas", "")

    try:
        fecha_reserva = datetime.strptime(fecha_texto, "%Y-%m-%d").date()
        hora_inicio = datetime.strptime(hora_texto, "%H:%M")
        personas = int(personas_texto)

    except ValueError:
        flash("Verifica la fecha, horario y cantidad de personas.", "error")
        return redirect(url_for("reservaciones"))

    if fecha_reserva < date.today():
        flash("No puedes elegir una fecha que ya pasó.", "error")
        return redirect(url_for("reservaciones"))

    if hora_texto not in obtener_horarios():
        flash("Selecciona un horario válido.", "error")
        return redirect(url_for("reservaciones"))

    if personas < 1 or personas > 8:
        flash("La reservación debe ser de 1 a 8 personas.", "error")
        return redirect(url_for("reservaciones"))

    if fecha_reserva == date.today():
        fecha_hora = datetime.combine(fecha_reserva, hora_inicio.time())

        if fecha_hora <= datetime.now():
            flash("Ese horario ya pasó. Elige uno posterior.", "error")
            return redirect(url_for("reservaciones"))

    hora_fin = hora_inicio + timedelta(hours=2)

    session["seleccion_reserva"] = {
        "fecha": fecha_texto,
        "hora_inicio": hora_texto,
        "hora_fin": hora_fin.strftime("%H:%M"),
        "personas": personas
    }

    session.pop("zona_reserva", None)

    return redirect(url_for("elegir_zona"))


# ==========================================
# ELEGIR ZONA
# ==========================================

@app.route("/elegir-zona")
def elegir_zona():

    if "cliente_id" not in session:
        return redirect(url_for("cuenta"))

    if not session.get("seleccion_reserva"):
        return redirect(url_for("reservaciones"))

    return render_template(
        "elegir_zona.html",
        seleccion=session["seleccion_reserva"],
        nombre=session.get("cliente_nombre")
    )


@app.route("/seleccionar-zona", methods=["POST"])
def seleccionar_zona():

    if "cliente_id" not in session:
        return redirect(url_for("cuenta"))

    if not session.get("seleccion_reserva"):
        return redirect(url_for("reservaciones"))

    zona = request.form.get("zona", "")

    if zona not in ["interior", "exterior"]:
        flash("Selecciona una zona válida.", "error")
        return redirect(url_for("elegir_zona"))

    session["zona_reserva"] = zona

    return redirect(url_for("plano_mesas"))


# ==========================================
# MOSTRAR PLANO Y DISPONIBILIDAD
# ==========================================

@app.route("/plano-mesas")
def plano_mesas():

    if "cliente_id" not in session:
        return redirect(url_for("cuenta"))

    seleccion = session.get("seleccion_reserva")
    zona = session.get("zona_reserva")

    if not seleccion or zona not in MESAS:
        return redirect(url_for("elegir_zona"))

    mesas_mostrar = []

    for mesa in MESAS[zona]:

        ocupada = mesa_esta_ocupada(
            seleccion["fecha"],
            zona,
            mesa["numero"],
            seleccion["hora_inicio"],
            seleccion["hora_fin"]
        )

        if ocupada:
            estado = "ocupada"
        elif mesa["capacidad"] < seleccion["personas"]:
            estado = "incompatible"
        else:
            estado = "disponible"

        mesas_mostrar.append({
            "numero": mesa["numero"],
            "capacidad": mesa["capacidad"],
            "estado": estado
        })

    return render_template(
        "plano_mesas.html",
        mesas=mesas_mostrar,
        zona=zona,
        seleccion=seleccion,
        nombre=session.get("cliente_nombre")
    )


# ==========================================
# CONFIRMAR SELECCION DE MESA
# ==========================================

@app.route("/confirmar-mesa", methods=["POST"])
def confirmar_mesa():

    if "cliente_id" not in session:
        return redirect(url_for("cuenta"))

    seleccion = session.get("seleccion_reserva")
    zona = session.get("zona_reserva")

    if not seleccion or zona not in MESAS:
        return redirect(url_for("reservaciones"))

    try:
        numero_mesa = int(request.form.get("mesa_numero", ""))

    except ValueError:
        flash("Selecciona una mesa válida.", "error")
        return redirect(url_for("plano_mesas"))

    mesa_elegida = next(
        (mesa for mesa in MESAS[zona] if mesa["numero"] == numero_mesa),
        None
    )

    if not mesa_elegida:
        flash("La mesa seleccionada no existe.", "error")
        return redirect(url_for("plano_mesas"))

    if mesa_elegida["capacidad"] < seleccion["personas"]:
        flash("Esa mesa no tiene capacidad suficiente.", "error")
        return redirect(url_for("plano_mesas"))

    if mesa_esta_ocupada(
        seleccion["fecha"],
        zona,
        numero_mesa,
        seleccion["hora_inicio"],
        seleccion["hora_fin"]
    ):
        flash("Lo sentimos, esa mesa acaba de ser reservada. Elige otra.", "error")
        return redirect(url_for("plano_mesas"))

    conexion = conectar_db()

    try:
        cursor = conexion.execute("""
            INSERT INTO reservaciones (
                cliente_id,
                fecha,
                hora_inicio,
                hora_fin,
                zona,
                mesa_numero,
                capacidad,
                personas,
                estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'confirmada')
        """, (
            session["cliente_id"],
            seleccion["fecha"],
            seleccion["hora_inicio"],
            seleccion["hora_fin"],
            zona,
            numero_mesa,
            mesa_elegida["capacidad"],
            seleccion["personas"]
        ))

        conexion.commit()

        session["reserva_confirmada"] = {
            "id": cursor.lastrowid,
            "fecha": seleccion["fecha"],
            "hora_inicio": seleccion["hora_inicio"],
            "hora_fin": seleccion["hora_fin"],
            "zona": zona,
            "mesa": numero_mesa,
            "capacidad": mesa_elegida["capacidad"],
            "personas": seleccion["personas"]
        }

        session.pop("seleccion_reserva", None)
        session.pop("zona_reserva", None)

        return redirect(url_for("reserva_confirmada"))

    except sqlite3.Error:
        conexion.rollback()
        flash("No se pudo guardar la reservación. Intenta nuevamente.", "error")
        return redirect(url_for("plano_mesas"))

    finally:
        conexion.close()


# ==========================================
# CONFIRMACION
# ==========================================

@app.route("/reserva-confirmada")
def reserva_confirmada():

    if "cliente_id" not in session:
        return redirect(url_for("cuenta"))

    reserva = session.get("reserva_confirmada")

    if not reserva:
        return redirect(url_for("reservaciones"))

    return render_template(
        "reserva_confirmada.html",
        reserva=reserva,
        nombre=session.get("cliente_nombre")
    )


# ==========================================
# PANEL DE ADMINISTRACION
# ==========================================

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():

    if request.method == "POST":

        usuario = request.form.get("usuario", "").strip()
        contrasena = request.form.get("contrasena", "")

        if usuario == ADMIN_USUARIO and contrasena == ADMIN_CONTRASENA:
            session.clear()
            session["administrador"] = True

            return redirect(url_for("admin_panel"))

        flash("Usuario o contraseña incorrectos.", "error")
        return redirect(url_for("admin_panel"))

    if not session.get("administrador"):
        return render_template("admin_login.html")

    busqueda = request.args.get("q", "").strip()

    conexion = conectar_db()

    try:
        if busqueda:
            reservas = conexion.execute("""
                SELECT
                    r.*,
                    c.nombre,
                    c.telefono,
                    c.correo
                FROM reservaciones r
                INNER JOIN clientes c ON c.id = r.cliente_id
                WHERE CAST(r.id AS TEXT) LIKE ?
                   OR c.nombre LIKE ?
                   OR c.correo LIKE ?
                ORDER BY r.fecha DESC, r.hora_inicio DESC
            """, (
                f"%{busqueda}%",
                f"%{busqueda}%",
                f"%{busqueda}%"
            )).fetchall()

        else:
            reservas = conexion.execute("""
                SELECT
                    r.*,
                    c.nombre,
                    c.telefono,
                    c.correo
                FROM reservaciones r
                INNER JOIN clientes c ON c.id = r.cliente_id
                ORDER BY r.fecha DESC, r.hora_inicio DESC
            """).fetchall()

    finally:
        conexion.close()

    return render_template(
        "admin.html",
        reservas=reservas,
        busqueda=busqueda
    )


# ==========================================
# ELIMINAR RESERVACION (SOLO ADMINISTRADOR)
# ==========================================

@app.route("/admin/eliminar/<int:reserva_id>", methods=["POST"])
def admin_eliminar_reserva(reserva_id):

    if not session.get("administrador"):
        flash("No tienes permiso para realizar esta acción.", "error")
        return redirect(url_for("admin_panel"))

    conexion = conectar_db()

    try:
        reserva = conexion.execute("""
            SELECT id
            FROM reservaciones
            WHERE id = ?
        """, (reserva_id,)).fetchone()

        if reserva:
            conexion.execute("""
                DELETE FROM reservaciones
                WHERE id = ?
            """, (reserva_id,))

            conexion.commit()

            flash(
                "La reservación fue eliminada y la mesa quedó liberada.",
                "exito"
            )

        else:
            flash("No se encontró esa reservación.", "error")

    except sqlite3.Error:
        conexion.rollback()
        flash("No se pudo eliminar la reservación.", "error")

    finally:
        conexion.close()

    return redirect(url_for("admin_panel"))


# ==========================================
# CERRAR SESION DEL ADMINISTRADOR
# ==========================================

@app.route("/admin/cerrar-sesion")
def admin_cerrar_sesion():

    session.clear()
    return redirect(url_for("admin_panel"))


# ==========================================
# CERRAR SESION DEL CLIENTE
# ==========================================

@app.route("/cerrar-sesion")
def cerrar_sesion():

    session.clear()

    flash("Has cerrado sesión correctamente.", "exito")

    return redirect(url_for("cuenta"))


# ==========================================
# INICIAR APLICACION
# ==========================================

if __name__ == "__main__":
    crear_base_datos()
    app.run(debug=True)
