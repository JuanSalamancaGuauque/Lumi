// =====================================================
// LUMI
// AVATAR (mediador visual y emocional)
// =====================================================
//
// Este es uno de los 3 pilares de la innovacion segun la
// propuesta QTA: un mediador visual/emocional que acompaña
// al usuario, pensado para reducir la barrera de entrada en
// personas con poca experiencia tecnologica.
//
// Cambia el GIF de Lumi (div#lumi-avatar) segun el estado de
// la conversacion. Los 5 estados y sus archivos reales viven
// tambien en database/init_db.py (tabla estado_avatar).

const AVATAR_STATES = {
    saludo:   "SALUDO LUMI.gif",
    pensando: "PENSANDO LUMI.gif",
    hablando: "HABLANDO LUMI.gif",
    feliz:    "FELIZ LUMI.gif",
    idle:     "IDLE LUMI.gif",
    error:    "ERROR LUMI.gif",
};

// Cuánto tiempo se queda Lumi en "saludo"/"feliz" antes de
// asentarse de vuelta en "idle" (reposo), si no pasa nada más.
const SETTLE_DELAY_MS = 6000;

const avatarContainer =
    document.getElementById("lumi-avatar");

let avatarImage = null;
let idleTimer = null;


function setAvatarState(state) {

    const archivo = AVATAR_STATES[state];

    // Si nos piden un estado que no existe, simplemente no
    // cambiamos nada en vez de romper la app.
    if (!archivo || !avatarContainer) {

        return;

    }

    // Cualquier cambio de estado cancela un "asentamiento a
    // idle" pendiente, si lo había.
    if (idleTimer) {

        clearTimeout(idleTimer);

        idleTimer = null;

    }

    // Creamos el <img> una sola vez, y despues solo le
    // cambiamos el "src" (mas eficiente que recrearlo).
    if (!avatarImage) {

        avatarImage =
            document.createElement("img");

        avatarImage.alt = "Lumi";

        avatarContainer.appendChild(
            avatarImage
        );

    }

    avatarImage.src =
        encodeURI(
            "/static/images/" + archivo
        );

    // Tras saludar o responder, si no pasa nada más,
    // Lumi vuelve a su estado de reposo (idle).
    if (state === "saludo" || state === "feliz") {

        idleTimer = setTimeout(() => {

            setAvatarState("idle");

        }, SETTLE_DELAY_MS);

    }

}


// Estado inicial: Lumi saludando al abrir la pagina,
// a juego con el mensaje de bienvenida.
setAvatarState("saludo");