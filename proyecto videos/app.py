import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
import pg8000.native
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secreto_desarrollo_123")

def get_db_connection():
    return pg8000.native.Connection(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "proyecto_videos"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        port=int(os.getenv("DB_PORT", 5432))
    )

VIDEOS = {
    "positivo": {
        "titulo": "Evaluación - Video Positivo",
        "url": "https://www.w3schools.com/html/mov_bbb.mp4",
        "badge": "Fase Positiva",
        "clase_badge": "badge-bueno"
    },
    "neutro": {
        "titulo": "Evaluación - Video Neutro",
        "url": "https://www.w3schools.com/html/movie.mp4",
        "badge": "Fase Neutra",
        "clase_badge": "badge-neutro"
    },
    "negativo": {
        "titulo": "Evaluación - Video Negativo",
        "url": "https://www.w3schools.com/html/mov_bbb.mp4",
        "badge": "Fase Negativa",
        "clase_badge": "badge-malo"
    }
}

@app.route("/", methods=["GET", "POST"])
def inicio():
    if request.method == "POST":
        return redirect(url_for("login_video", tipo_video="positivo"), code=307)
    return redirect(url_for("login_video", tipo_video="positivo"))

@app.route("/<tipo_video>", methods=["GET", "POST"])
def login_video(tipo_video):
    tipo = tipo_video.lower()
    if tipo not in VIDEOS:
        return "Página no encontrada", 404

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()

        if not nombre or not apellido:
            flash("Por favor, completa ambos campos.", "danger")
            return redirect(url_for("login_video", tipo_video=tipo))

        try:
            conn = get_db_connection()
            
            conn.run("CREATE TABLE IF NOT EXISTS personas (id SERIAL PRIMARY KEY, nombre VARCHAR(100), apellido VARCHAR(100));")
            conn.run("ALTER TABLE personas ADD COLUMN IF NOT EXISTS tipo_video VARCHAR(50) DEFAULT 'general';")

            existente = conn.run(
                "SELECT id FROM personas WHERE LOWER(nombre) = LOWER(:n) AND LOWER(apellido) = LOWER(:a) AND tipo_video = :t",
                n=nombre, a=apellido, t=tipo
            )

            if existente:
                conn.close()
                return render_template("bloqueado.html")

            conn.run(
                "INSERT INTO personas (nombre, apellido, tipo_video) VALUES (:n, :a, :t)",
                n=nombre, a=apellido, t=tipo
            )
            conn.close()

            session["usuario_validado"] = f"{nombre}_{apellido}_{tipo}"
            return redirect(url_for("ver_video_unico", tipo_video=tipo))

        except Exception as e:
            print("Error DB:", e)
            flash("Error de conexión a la base de datos.", "danger")
            return redirect(url_for("login_video", tipo_video=tipo))

    return render_template("login.html", tipo=tipo, info=VIDEOS[tipo])


@app.route("/ver/<tipo_video>")
def ver_video_unico(tipo_video):
    tipo = tipo_video.lower()
    if not session.get("usuario_validado") or tipo not in VIDEOS:
        return redirect(url_for("login_video", tipo_video=tipo if tipo in VIDEOS else "positivo"))
    
    return render_template("videos.html", video_info=VIDEOS[tipo])


if __name__ == "__main__":
    app.run(debug=True)
