import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import pg8000.dbapi
from urllib.parse import urlparse
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
# Clave secreta para poder usar las sesiones y mensajes del servidor
app.secret_key = os.getenv("SECRET_KEY", "un_secreto_muy_seguro_12345")

# Función para abrir la conexión a la base de datos PostgreSQL usando pg8000 (Pure Python)
def get_db_connection():
    db_url = os.getenv("DATABASE_URL")

    if db_url:
        # Conexión para producción (Render) usando DATABASE_URL
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        result = urlparse(db_url)
        return pg8000.dbapi.connect(
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port or 5432,
            database=result.path[1:]
        )
    else:
        # Conexión local (para tus pruebas en la computadora)
        return pg8000.dbapi.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "proyecto_videos"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "tu_contraseña"),
            port=int(os.getenv("DB_PORT", "5432"))
        )

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Traemos los datos ingresados y limpiamos espacios vacíos
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()

        if not nombre or not apellido:
            flash("Por favor, escribe tu nombre y apellido.")
            return redirect(url_for("index"))

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Buscamos si ya existe el nombre + apellido (sin importar mayúsculas/minúsculas)
            cur.execute(
                "SELECT id FROM personas WHERE LOWER(nombre) = LOWER(%s) AND LOWER(apellido) = LOWER(%s);",
                (nombre, apellido)
            )
            persona = cur.fetchone()

            if persona:
                # Si ya existe en la base de datos, lo enviamos a la pantalla de bloqueo
                cur.close()
                conn.close()
                return render_template("bloqueado.html", nombre=nombre, apellido=apellido)
            else:
                # Si NO existe, lo registramos de inmediato en la base de datos
                cur.execute(
                    "INSERT INTO personas (nombre, apellido) VALUES (%s, %s);",
                    (nombre, apellido)
                )
                conn.commit()
                cur.close()
                conn.close()

                # Guardamos la sesión temporal para que Flask lo deje pasar a la página de videos
                session["usuario"] = f"{nombre} {apellido}"
                return redirect(url_for("videos"))

        except Exception as e:
            # Si ocurre algún error con la base de datos, lo mostramos en consola
            print(f"Error de base de datos: {e}")
            flash("Ocurrió un error al conectar con el servidor. Inténtalo más tarde.")
            return redirect(url_for("index"))

    return render_template("index.html")

@app.route("/videos")
def videos():
    # Si un participante intenta entrar directamente escribiendo /videos en la barra,
    # el sistema comprueba la sesión. Si no pasó por el formulario, lo devuelve al inicio.
    if "usuario" not in session:
        return redirect(url_for("index"))

    return render_template("videos.html")

@app.route("/bloqueado")
def bloqueado():
    return render_template("bloqueado.html")

if __name__ == "__main__":
    # Arranca el servidor local en modo desarrollo
    app.run(debug=True)
