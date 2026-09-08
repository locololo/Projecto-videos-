document.addEventListener("DOMContentLoaded", () => {
    let pasoActual = 1;

    const cartelFinal = document.getElementById("cartel-final");
    const video1 = document.getElementById("video-1");
    const video2 = document.getElementById("video-2");
    const video3 = document.getElementById("video-3");

    // Función para aplicar bloqueos estrictos a cada reproductor de video
    function aplicarBloqueosVideo(videoElement) {
        if (!videoElement) return;

        // 1. Evitar pausa (si se pausa nativamente, se obliga a reproducir al instante)
        videoElement.addEventListener("pause", () => {
            if (videoElement.currentTime < videoElement.duration - 0.5) {
                videoElement.play().catch(() => {});
            }
        });

        // 2. Evitar retrocesos y adelantos (Control de tiempo estricto)
        let tiempoVisto = 0;
        videoElement.addEventListener("timeupdate", () => {
            if (videoElement.currentTime > tiempoVisto + 1.5) {
                videoElement.currentTime = tiempoVisto;
            } else {
                tiempoVisto = videoElement.currentTime;
            }
        });

        videoElement.addEventListener("seeking", () => {
            if (videoElement.currentTime > tiempoVisto) {
                videoElement.currentTime = tiempoVisto;
            }
        });

        // 3. Bloquear clics derechos sobre el video
        videoElement.addEventListener("contextmenu", (e) => {
            e.preventDefault();
        });
    }

    aplicarBloqueosVideo(video1);
    aplicarBloqueosVideo(video2);
    aplicarBloqueosVideo(video3);

    // --- CONFIGURACIÓN DEL BOTÓN DE INICIO EXCLUSIVO PARA EL VIDEO 1 ---
    const capa1 = document.getElementById("capa-inicio-1");
    if (capa1 && video1) {
        const boton1 = capa1.querySelector("button");
        boton1.addEventListener("click", () => {
            capa1.classList.add("hidden"); // Oculta la capa de inicio
            video1.play().catch(err => {
                console.error("Error al iniciar video 1:", err);
            });
        });
    }

    // --- TRANSICIÓN AUTOMÁTICA SECUENCIAL DIRECTA (AUTOPLAY) ---
    function alTerminarVideo(numeroPaso) {
        // Ocultamos el bloque del video que acaba de finalizar
        document.getElementById(`bloque-video-${numeroPaso}`).classList.add("hidden");

        if (numeroPaso === 1) {
            pasoActual = 2;
            const bloque2 = document.getElementById("bloque-video-2");
            bloque2.classList.remove("hidden");
            if (video2) {
                // Al haber interactuado previamente con el Video 1, el navegador ya otorga permisos
                // para que el Video 2 inicie de forma automática con audio sin trabas
                video2.play().catch(err => {
                    console.error("Autoplay bloqueado en Video 2, intentando reproducir...", err);
                });
            }
        } else if (numeroPaso === 2) {
            pasoActual = 3;
            const bloque3 = document.getElementById("bloque-video-3");
            bloque3.classList.remove("hidden");
            if (video3) {
                // Autoplay directo para el Video C
                video3.play().catch(err => {
                    console.error("Autoplay bloqueado en Video 3, intentando reproducir...", err);
                });
            }
        } else if (numeroPaso === 3) {
            // Muestra el mensaje final solo cuando el último video concluya
            if (cartelFinal) {
                cartelFinal.classList.remove("hidden");
            }
        }
    }

    if (video1) video1.addEventListener("ended", () => alTerminarVideo(1));
    if (video2) video2.addEventListener("ended", () => alTerminarVideo(2));
    if (video3) video3.addEventListener("ended", () => alTerminarVideo(3));

    // Bloquear click derecho en todo el documento para evitar inspección
    document.addEventListener("contextmenu", (e) => {
        e.preventDefault();
    });
});
