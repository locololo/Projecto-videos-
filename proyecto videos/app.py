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

# Servidores ultraligeros CDN de W3Schools (archivos .mp4 livianos y ultrarrápidos)
VIDEOS = {
    "video1": {
        "titulo": "Evaluación - Video 1",
        "url": "https://pub-72bc7fabaecc4adea8d80b642c12d19d.r2.dev/Video%20positivo.mp4",
        "badge": "Fase 1",
        "clase_badge": "badge-general"
    },
    "video2": {
        "titulo": "Evaluación - Video 2",
        "url": "https://pub-72bc7fabaecc4adea8d80b642c12d19d.r2.dev/Video%20neutro.mp4",
        "badge": "Fase 2",
        "clase_badge": "badge-general"
    },
    "video3": {
        "titulo": "Evaluación - Video 3",
        "url": "https://pub-72bc7fabaecc4adea8d80b642c12d19d.r2.dev/Video%20negativo.mp4",
        "badge": "Fase 3",
        "clase_badge": "badge-general"
    },
    "palabras": {
        "titulo": "Evaluación - Palabras",
        "url": "https://pub-72bc7fabaecc4adea8d80b642c12d19d.r2.dev/Palabras.mp4",
        "badge": "Fase Palabras",
        "clase_badge": "badge-general"
    }
}

@app.route("/")
def inicio():
    return redirect(url_for("login_video", tipo_video="video1"))

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
    val = session.get("usuario_validado", "")
    
    if not val or not val.endswith(f"_{tipo}") or tipo not in VIDEOS:
        return redirect(url_for("login_video", tipo_video=tipo if tipo in VIDEOS else "video1"))
    
    return render_template("videos.html", video_info=VIDEOS[tipo])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
