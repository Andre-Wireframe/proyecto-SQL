from flask import Flask, render_template, request, url_for, redirect
from flask_mysqldb import MySQL
from flask_login import login_user, logout_user, UserMixin, login_required, LoginManager, current_user
import bcrypt

# Program functions
def login_func(username, password):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE nombre = %s;", (username,))
    user = cursor.fetchone()

    if not user:
        return "no_usr"
    
    if bcrypt.checkpw(password.encode("utf-8"), user[2].encode("utf-8")):
        login_user(User(user[0], user[1]))
        return True
    
    else:
        return "no_pass"

def singin_func(username, password, password2, edad, phone):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE nombre = %s;", (username,))
    user_ch = cursor.fetchone()

    if not password == password2:
        return "no_pass"

    if user_ch:
        return "usr_exists"
    
    hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12))
    
    cursor.execute("""
        INSERT INTO usuarios(nombre, password, edad, phone)
            VALUES (%s, %s, %s, %s);
    """, (username, hash.decode("utf-8"), edad, phone))

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

def add_report(servicio, direccion, urgencia, descripcion):
    try:
        cursor = mysql.connection.cursor()
        user = current_user.id
        
        cursor.execute("""
            INSERT INTO reportes(usuario, servicio, direccion, urgencia, descripcion)
                VALUES (%s, %s, %s, %s, %s);
        """, (user, servicio, direccion, urgencia, descripcion))
        cursor.close()
        mysql.connection.commit()

        return True
    except:
        return False

def get_services():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, nombre FROM servicios;")
 
    return cursor.fetchall()

def get_reports():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM reportes;")

    return cursor.fetchall()

app = Flask(__name__)
app.secret_key = "admin123"

#Login-flask
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre

# Base de datos MYSQL
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "admin123"
app.config["MYSQL_DB"] = "proyecto"

mysql = MySQL(app)

# Rutas app
@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, nombre FROM usuarios WHERE id = %s;", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return User(user[0], user[1])
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
            return redirect(url_for("index"))
    
    return render_template("login.html")

@app.route("/singin/", methods=["GET", "POST"])
def singin():
    if request.method == "POST":
        name = request.form.get("username")
        edad = request.form.get("edad")
        phone = request.form.get("phone")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        if singin_func(name, password, password2, edad, phone):
            return redirect(url_for("index"))
        
    return render_template("singin.html")

@app.route("/services/", methods=["GET", "POST"])
@login_required
def services():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        costo = request.form.get("costo")
        periodo = request.form.get("periodo")
        type = request.form.get("type")

        if add_service(nombre, costo, periodo, type):
            return redirect(url_for("index"))

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
        urgencia = request.form.get("urgencia")
        descripcion = request.form.get("descripcion")

        if add_report(servicio, direccion, urgencia, descripcion):
            return redirect(url_for("index"))
    
    return render_template("reports.html", **context)

@app.route("/reports-get/", methods = ["GET"])
@login_required
def reports_get():
    context = {
        "reports" : get_reports()
    }
    return render_template("", **context)

# Server run
if __name__ == "__main__":
    app.run("0.0.0.0", port=3030, debug=True)