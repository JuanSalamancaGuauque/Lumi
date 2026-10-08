// =====================================================
// LUMI — Galería de fotos del lugar
//  · Miniatura en el chat: 1 foto a la vez, fundido en loop
//  · Visor ampliado: carrusel con fotos laterales y puntos
// =====================================================

(function () {
    "use strict";

    const ROTATE_MS = 3500;   // tiempo entre fotos
    const FADE_MS   = 900;    // duración del desvanecido
    const CLOSE_ICON = "/static/images/quitar%20lumi.png";


    // ---------- Utilidades ----------

    function photoUrl(archivo) {
        const v = String(archivo || "").trim();
        if (!v) return "";
        if (/^(https?:|data:|blob:|\/)/i.test(v)) return v;
        // "lugares/zona_g/1.jpg" -> "/static/images/lugares/zona_g/1.jpg"
        return "/static/images/" + v.split("/").map(encodeURIComponent).join("/");
    }

    // Si una foto no carga (nombre mal escrito) se descarta sin romper nada
    function preload(item) {
        return new Promise(resolve => {
            const probe = new Image();
            probe.onload = () => resolve(item);
            probe.onerror = () => {
                console.warn("No se pudo cargar la foto:", item.url);
                resolve(null);
            };
            probe.src = item.url;
        });
    }


    // =================================================
    // VISOR AMPLIADO
    // =================================================

    let viewer = null, stage = null, dotsBox = null;
    let slides = [], dots = [];
    const state = { items: [], cur: 0 };

    function ensureViewer() {
        if (viewer) return;

        viewer = document.createElement("div");
        viewer.className = "gv";
        viewer.setAttribute("role", "dialog");
        viewer.setAttribute("aria-modal", "true");
        viewer.setAttribute("aria-hidden", "true");
        viewer.innerHTML = `
            <div class="gv-stage"></div>
            <div class="gv-dots"></div>
            <button type="button" class="gv-close" aria-label="Cerrar fotos">
                <img src="${CLOSE_ICON}" alt="">
            </button>`;
        document.body.appendChild(viewer);

        stage   = viewer.querySelector(".gv-stage");
        dotsBox = viewer.querySelector(".gv-dots");

        viewer.querySelector(".gv-close").addEventListener("click", closeViewer);

        // Clic en el fondo oscuro = cerrar
        stage.addEventListener("click", e => {
            if (e.target === stage) closeViewer();
        });

        // Deslizar con el dedo
        let startX = null;
        stage.addEventListener("touchstart", e => {
            startX = e.touches[0].clientX;
        }, { passive: true });
        stage.addEventListener("touchend", e => {
            if (startX === null) return;
            const dx = e.changedTouches[0].clientX - startX;
            startX = null;
            if (Math.abs(dx) > 50) go(dx < 0 ? 1 : -1);
        }, { passive: true });

        // Teclado
        document.addEventListener("keydown", e => {
            if (!viewer.classList.contains("open")) return;
            if (e.key === "Escape") closeViewer();
            else if (e.key === "ArrowRight") go(1);
            else if (e.key === "ArrowLeft") go(-1);
        });
    }

    // Coloca cada foto según su distancia a la foto actual
    function layout() {
        const n = state.items.length;

        slides.forEach((slide, i) => {
            let d = ((i - state.cur) % n + n) % n;
            if (d > n / 2) d -= n;                 // carrusel circular

            slide.style.setProperty("--d", d);
            slide.dataset.pos =
                d === 0 ? "center" : Math.abs(d) === 1 ? "side" : "far";
        });

        dots.forEach((dot, i) => dot.classList.toggle("active", i === state.cur));
    }

    function go(step) {
        const n = state.items.length;
        state.cur = (state.cur + step + n) % n;
        layout();
    }

    function openViewer(items, start) {
        ensureViewer();

        state.items = items;
        state.cur = start || 0;

        stage.innerHTML = "";
        dotsBox.innerHTML = "";

        slides = items.map((item, i) => {
            const slide = document.createElement("div");
            slide.className = "gv-slide";

            const img = document.createElement("img");
            img.src = item.url;
            img.alt = item.alt;
            img.draggable = false;
            slide.appendChild(img);

            // Clic en una foto lateral = pasar a esa foto
            slide.addEventListener("click", () => {
                if (slide.dataset.pos === "side") {
                    state.cur = i;
                    layout();
                }
            });

            stage.appendChild(slide);
            return slide;
        });

        dots = items.map((item, i) => {
            const dot = document.createElement("button");
            dot.type = "button";
            dot.className = "gv-dot";
            dot.setAttribute("aria-label", "Foto " + (i + 1));
            dot.addEventListener("click", () => {
                state.cur = i;
                layout();
            });
            dotsBox.appendChild(dot);
            return dot;
        });

        layout();

        viewer.classList.add("open");
        viewer.setAttribute("aria-hidden", "false");
        document.body.classList.add("gv-open");
        viewer.querySelector(".gv-close").focus({ preventScroll: true });
    }

    function closeViewer() {
        if (!viewer) return;
        viewer.classList.remove("open");
        viewer.setAttribute("aria-hidden", "true");
        document.body.classList.remove("gv-open");
    }


    // =================================================
    // MINIATURA EN EL CHAT
    // =================================================

    async function createPhotoGallery(place) {

        const responseDiv = document.getElementById("response");
        const scroller = document.querySelector(".chat-messages");

        if (
            !place || !responseDiv ||
            !Array.isArray(place.imagenes) || place.imagenes.length === 0
        ) {
            return;
        }

        const nombre = place.nombre || "este lugar";

        // Solo la galería más reciente "llama" al usuario con el shake
        document
            .querySelectorAll(".photo-stack.cta")
            .forEach(el => el.classList.remove("cta"));

        // Se reserva el lugar en el chat para respetar el orden de mensajes
        const wrap = document.createElement("div");
        wrap.className = "photo-gallery";
        wrap.hidden = true;
        responseDiv.appendChild(wrap);

        const candidates = place.imagenes.slice(0, 4).map((foto, i) => ({
            url: photoUrl(foto.archivo),
            alt: foto.texto_alternativo || `${nombre} - foto ${i + 1}`
        }));

        const items = (await Promise.all(candidates.map(preload))).filter(Boolean);

        if (items.length === 0) {
            wrap.remove();
            return;
        }

        const stack = document.createElement("div");
        stack.className = "photo-stack cta";
        stack.setAttribute("role", "button");
        stack.tabIndex = 0;
        stack.setAttribute("aria-label", "Ver fotos de " + nombre);

        const els = items.map(item => {
            const img = document.createElement("img");
            img.src = item.url;
            img.alt = item.alt;
            img.draggable = false;
            stack.appendChild(img);
            return img;
        });

        els[0].classList.add("active");
        wrap.appendChild(stack);
        wrap.hidden = false;

        // ---- Fundido entre fotos ----
        let current = 0;
        let timer = null;

        function show(next) {
            if (next === current) return;

            const old = els[current];
            const nuevo = els[next];

            // La anterior queda visible debajo hasta que la nueva termina de aparecer
            old.classList.remove("active");
            old.classList.add("prev");

            nuevo.classList.remove("prev");
            nuevo.classList.add("active");

            setTimeout(() => old.classList.remove("prev"), FADE_MS + 50);
            current = next;
        }

        function start() {
            if (timer || els.length < 2) return;
            timer = setInterval(() => {
                if (document.body.classList.contains("gv-open")) return; // pausa con el visor abierto
                show((current + 1) % els.length);
            }, ROTATE_MS);
        }

        function stop() {
            clearInterval(timer);
            timer = null;
        }

        // Solo rota mientras es visible dentro del chat
        if ("IntersectionObserver" in window) {
            new IntersectionObserver(entries => {
                entries.forEach(entry => (entry.isIntersecting ? start() : stop()));
            }, { root: scroller, threshold: 0.3 }).observe(stack);
        } else {
            start();
        }

        // ---- Abrir visor ----
        function open() {
            stack.classList.remove("cta");   // ya vio la animación: se detiene el shake
            openViewer(items, current);
        }

        stack.addEventListener("click", open);
        stack.addEventListener("keydown", e => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                open();
            }
        });
    }

    window.createPhotoGallery = createPhotoGallery;

})();