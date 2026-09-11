document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("video-principal");
    const capaInicio = document.getElementById("capa-inicio");
    const cartelFinal = document.getElementById("cartel-final");
    const bloqueVideo = document.getElementById("bloque-video-unico");

    if (!video) return;

    // 1. Bloqueo estricto de pausa
    video.addEventListener("pause", () => {
        if (video.currentTime < video.duration - 0.5) {
            video.play().catch(() => {});
        }
    });

    // 2. Evitar adelantamientos y retrocesos
    let tiempoVisto = 0;
    video.addEventListener("timeupdate", () => {
        if (video.currentTime > tiempoVisto + 1.5) {
            video.currentTime = tiempoVisto;
        } else {
            tiempoVisto = video.currentTime;
        }
    });

    video.addEventListener("seeking", () => {
        if (video.currentTime > tiempoVisto) {
            video.currentTime = tiempoVisto;
        }
    });

    // 3. Botón de inicio interactivo
    if (capaInicio) {
        const boton = capaInicio.querySelector("button");
        boton.addEventListener("click", () => {
            capaInicio.classList.add("hidden");
            video.play().catch(err => console.error("Error al iniciar video:", err));
        });
    }

    // 4. Mostrar cartel al finalizar el video
    video.addEventListener("ended", () => {
        bloqueVideo.classList.add("hidden");
        if (cartelFinal) {
            cartelFinal.classList.remove("hidden");
        }
    });

    // 5. Bloquear clic derecho
    document.addEventListener("contextmenu", (e) => e.preventDefault());
});