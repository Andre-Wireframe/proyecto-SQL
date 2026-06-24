from flask import Flask, render_template, request, url_for, redirect, flash
from flask_mysqldb import MySQL
from flask_login import login_user, logout_user, UserMixin, login_required, LoginManager, current_user, AnonymousUserMixin
import bcrypt
import os
from google import genai
import datetime

# Program functions
def login_func(username, password):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE nombre = %s;", (username,))
    user = cursor.fetchone()

    if not user:
        return False
    
    if bcrypt.checkpw(password.encode("utf-8"), user[2].encode("utf-8")):
        login_user(User(user[0], user[1], user[5]))
        return True
    
    else:
        return False

def singin_func(username, password, password2, edad, phone, type):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE nombre = %s;", (username,))
    user_ch = cursor.fetchone()

    if not password == password2:
        return "no_pass"

    if user_ch:
        return "usr_exists"
    
    hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12))
    
    cursor.execute("""
        INSERT INTO usuarios(nombre, password, edad, phone, type)
            VALUES (%s, %s, %s, %s, %s);
    """, (username, hash.decode("utf-8"), edad, phone if phone else None, type))

    cursor.close()
    mysql.connection.commit()

    return True

def add_service(nombre, costo, periodo, type):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO servicios(nombre, costo, periodo, type)
                VALUES (%s, %s, %s, %s);
        """, (nombre, costo, periodo, type))
        cursor.close()
        mysql.connection.commit()

        return True
    except:
        return False

def add_report(servicio, direccion, descripcion):
    cursor = mysql.connection.cursor()
    user = current_user.id
    fecha = datetime.date.today()

    try:
        promp = gemini.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""
            En una sola palabra y sin explicaciones elige entre urgencia alta, media o baja segun el siguiente
            problema: {descripcion}
        """)
        
        urgencia = promp.text

    except:
        urgencia = "S/A"
        flash("IA no disponible urgencia no asignada, pruebe conectarse a internet", "warning")
    
    cursor.execute("""
        INSERT INTO reportes(usuario, servicio, direccion, urgencia, descripcion, fecha)
            VALUES (%s, %s, %s, %s, %s, %s);
    """, (user, servicio, direccion, urgencia, descripcion, fecha))
    cursor.close()
    mysql.connection.commit()

    return True

def get_services():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM servicios;")
 
    return cursor.fetchall()

def get_reports():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT
            rp.id,
            us.nombre,
            se.nombre,
            rp.direccion,
            rp.urgencia,
            rp.descripcion,
            rp.fecha
        FROM reportes rp
        LEFT JOIN usuarios us ON rp.usuario = us.id
        LEFT JOIN servicios se ON rp.servicio = se.id;
    """)

    return cursor.fetchall()

#app
app = Flask(__name__)
app.secret_key = os.environ.get("flask_secret_key")

#Gemini
gemini = genai.Client(api_key=os.environ.get("gemini_API_key"))

#Login-flask
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Por favor inicie sesion para contuinar"

class User(UserMixin):
    def __init__(self, id, nombre, type):
        self.id = id 
        self.nombre = nombre
        self.type = type

# Base de datos MYSQL
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = os.environ.get("mysql_key")
app.config["MYSQL_DB"] = "proyecto"

mysql = MySQL(app)

# Rutas app
@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, nombre, type FROM usuarios WHERE id = %s;", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return User(user[0], user[1], user[2])
    else:
        return None


@app.route("/", methods=["GET"])
def index():
    context = {}
    return render_template("index.html", **context)

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")

        if login_func(name, password):
            print("succses")
            return redirect(url_for("index"))
        
        else:
            flash("Los datos ingresados no son correctos", "error")
    
    return render_template("login.html")

@app.route("/singin/", methods=["GET", "POST"])
def singin():
    if request.method == "POST":
        name = request.form.get("username")
        edad = request.form.get("edad")
        phone = request.form.get("phone")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        type_ = "normal"
        if not isinstance(current_user, AnonymousUserMixin):
            if current_user.type == "admin":
                type_ = "admin"

        if singin_func(name, password, password2, edad, phone, type_):
            return redirect(url_for("index"))
        
        else:
            flash("Error interno del servidor", "error")
        
    return render_template("singin.html")

@app.route("/logout/")
def logout():
    logout_user()
    flash("La sesion fue cerrada exitosamente", "success")

    return redirect(url_for("index"))

@app.route("/services/", methods=["GET", "POST"])
@login_required
def services():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        costo = request.form.get("costo")
        periodo = request.form.get("periodo")
        type = request.form.get("type")

        if add_service(nombre, costo, periodo, type):
            flash("Servicio agregado exitosamente", "success")
            return redirect(url_for("services_get"))

    return render_template("services.html")

@app.route("/reports/", methods=["POST", "GET"])
@login_required
def reports():
    context = {
        "services":get_services()
    }

    if request.method == "POST":
        servicio = request.form.get("servicio")
        direccion = request.form.get("direccion")
        descripcion = request.form.get("descripcion")

        if add_report(servicio, direccion, descripcion):
            flash("Reporte agregado exitosamente", "success")
            return redirect(url_for("reports_get"))
        
        else:
            flash("A ocurrido un error al intentar agregar el reporte reintente", "error")
    
    return render_template("reports.html", **context)

@app.route("/services-get/", methods = ["GET"])
@login_required
def services_get():
    context = {
        "services" : get_services()
    }
    return render_template("services_get.html", **context)

@app.route("/reports-get/", methods = ["GET"])
@login_required
def reports_get():
    context = {
        "reports" : get_reports()
    }
    return render_template("reports_get.html", **context)

@app.route("/reports-del/<id>/")
@login_required
def reports_del(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM reportes WHERE id = %s", (id,))
    reporte = cursor.fetchone()
    if current_user.type == "admin" or current_user.id == reporte[1]:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            DELETE FROM reportes
            WHERE id = %s;
        """, (id,))

        mysql.connection.commit()
        flash("Reporte eliminado con exito", "success")
    else:
        flash("Usuario no autorizado a esta operacion", "error")

    return redirect(url_for("reports_get"))

@app.route("/reports-mod/<id>/", methods = ["GET", "POST"])
@login_required
def reports_mod(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM reportes WHERE id = %s", (id,))
    reporte = cursor.fetchone()
    context = {"id": id, "services":get_services()}

    if request.method == "POST":
        servicio = request.form.get("servicio")
        direccion = request.form.get("direccion")
        urgencia = request.form.get("urgencia")
        descripcion = request.form.get("descripcion")

        if current_user.type == "admin" or current_user.id == reporte[1]:
            cursor.execute("""
                UPDATE reportes
                SET
                    servicio = %s,
                    direccion = %s,
                    urgencia = %s,
                    descripcion = %s
                WHERE id = %s;
            """, (servicio, direccion, urgencia, descripcion, id))
            mysql.connection.commit()
            flash("Reporte modificado con exito", "success")
        else:
            flash("Usuario no autorizado a esta operacion", "error")
    
        return redirect(url_for("reports_get"))
    
    return render_template("reports.html", **context)

@app.route("/services_mod/<id>/", methods = ["GET", "POST"])
@login_required
def services_mod(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nombre FROM servicios WHERE id = %s", (id,))
    service = cursor.fetchone()
    context = {"id": id, "service":service[0]}

    if request.method == "POST":
        nombre = request.form.get("nombre")
        costo = request.form.get("costo")
        periodo = request.form.get("periodo")
        type = request.form.get("type")

        if current_user.type == "admin":
            cursor.execute("""
                UPDATE servicios
                SET
                    nombre = %s,
                    costo = %s,
                    periodo = %s,
                    type = %s
                WHERE id = %s;
            """, (nombre, costo, periodo, type, id))
            mysql.connection.commit()
            flash("Servicio modificado con exito", "success")
        else:
            flash("Usuario no autorizado a esta operacion", "error")
        
        return redirect(url_for("services_get"))
    
    return render_template("services.html", **context)

@app.route("/services_del/<id>/", methods = ["POST", "GET"])
@login_required
def services_del(id):
    if current_user.type == "admin":
        cursor = mysql.connection.cursor()
        cursor.execute("""
            DELETE FROM servicios
            WHERE id = %s;
        """, (id,))

        mysql.connection.commit()

        flash("Servicio eliminado con exito", "success")
    else:
        flash("Usuario no autorizado a esta operacion", "error")

    return redirect(url_for("services_get"))

@app.route("/mis_reportes/", methods=["GET"])
@login_required
def mis_reportes():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT
            rp.id,
            us.nombre,
            se.nombre,
            rp.direccion,
            rp.urgencia,
            rp.descripcion
        FROM reportes rp
        LEFT JOIN usuarios us ON rp.usuario = us.id
        LEFT JOIN servicios se ON rp.servicio = se.id
        WHERE us.id = %s;
    """, (current_user.id, ))

    reports = cursor.fetchall()
    context = {
        "reports" : reports
    }
    return render_template("admin-zone.html", **context)

# Server run
if __name__ == "__main__":
    app.run("0.0.0.0", port=3030, debug=True)