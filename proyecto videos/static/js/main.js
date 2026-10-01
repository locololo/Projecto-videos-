document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("reproductor");
    const btnPlay = document.getElementById("btn-play");
    const capaInicio = document.getElementById("capa-inicio");
    const cartelFinal = document.getElementById("cartel-final");
    const videoWrapper = document.querySelector(".video-wrapper");

    if (!video || !btnPlay) return;

    btnPlay.addEventListener("click", () => {
        if (capaInicio) capaInicio.classList.add("hidden");
        const playPromise = video.play();
        if (playPromise !== undefined) {
            playPromise.catch(err => {
                console.error("Error al iniciar video:", err);
                if (capaInicio) capaInicio.classList.remove("hidden");
            });
        }
    });

    video.addEventListener("pause", () => {
        if (!video.ended && video.currentTime < video.duration - 0.5) {
            video.play().catch(() => {});
        }
    });

    video.addEventListener("contextmenu", e => e.preventDefault());

    video.addEventListener("ended", () => {
        if (videoWrapper) videoWrapper.classList.add("hidden");
        if (cartelFinal) cartelFinal.classList.remove("hidden");
    });
});
