from flask import Flask, render_template, request, url_for, redirect
from flask_mysqldb import MySQL
from flask_login import login_user, logout_user, UserMixin, login_required
import bcrypt

# Program functions
def login(username, password):
    cursor = mysql.connection.cursor()

def singin(username, password, password2):
    cursor = mysql.connection.cursor()

def add_service(nombre, costo, periodo, type):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO servicios(nombre, costo, periodo, type)
            VALUES (%s, %s, %s, %s);
    """, (nombre, costo, periodo, type))
    mysql.connection.commit()

    return True

app = Flask(__name__)

# Base de datos MYSQL
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "admin123"
app.config["MYSQL_DB"] = "proyecto"

mysql = MySQL(app)

# Rutas app
@app.route("/", methods=["GET"])
def index():
    context = {}
    return render_template("index.html", **context)

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")

        if login(name, password):
            return url_for("index")
    
    return render_template("login.html")

@app.route("/singin/", methods=["GET", "POST"])
def singin():
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        if singin(name, password, password2):
            return url_for("index")
        
    return render_template("singin.html")

@app.route("/services/", methods=["GET", "POST"])
def services():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        costo = request.form.get("costo")
        periodo = request.form.get("periodo")
        type = request.form.get("type")

        if add_service(nombre, costo, periodo, type):
            return redirect(url_for("index"))

    return render_template("services.html")

# Server run
if __name__ == "__main__":
    app.run("0.0.0.0", port=3030, debug=True)