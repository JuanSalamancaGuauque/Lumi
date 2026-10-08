// =====================================================
// LUMI
// APP
// =====================================================


// =====================================================
// ELEMENTOS
// =====================================================

const input =
    document.getElementById("message");


const button =
    document.getElementById("send");


const responseDiv =
    document.getElementById("response");


const welcomeMessage =
    document.getElementById("welcome-message");


const chatContainer =
    document.getElementById("chatContainer");


const chatMessages =
    document.querySelector(".chat-messages");


const lumiAvatarImage =
    document.getElementById("lumi-avatar-image");


// =====================================================
// RUTAS DE LOS GIF
// =====================================================

const LUMI_GIFS = {

    saludo:
        "/static/images/SALUDO%20LUMI.gif",

    hablando:
        "/static/images/HABLANDO%20LUMI.gif",

    pensando:
        "/static/images/PENSANDO%20LUMI.gif",

    feliz:
        "/static/images/FELIZ%20LUMI.gif",

    error:
        "/static/images/ERROR%20LUMI.gif"

};


// =====================================================
// CAMBIAR ANIMACIÓN DE LUMI
// =====================================================

function setLumiAnimation(tipo) {

    if (!lumiAvatarImage) {
        return;
    }


    const nuevaRuta =
        LUMI_GIFS[tipo] ||
        LUMI_GIFS.saludo;


    if (
        lumiAvatarImage.src.endsWith(
            nuevaRuta
        )
    ) {
        return;
    }


    lumiAvatarImage.src =
        nuevaRuta;
}


// =====================================================
// SCROLL AUTOMÁTICO
//
// Siempre se muestra lo más reciente. Si la persona sube
// a releer, el chat no la "arrastra" de vuelta hasta que
// envíe otro mensaje.
// =====================================================

let stickToBottom = true;


// El parámetro se conserva por compatibilidad con las
// llamadas existentes, pero ya no se usa scroll suave:
// varios scrolls suaves seguidos se cancelaban entre sí
// y el chat se quedaba arriba.

function scrollChatToBottom() {

    if (!chatMessages) {
        return;
    }


    stickToBottom = true;


    const goToBottom = () => {

        chatMessages.scrollTop =
            chatMessages.scrollHeight;

    };


    // Inmediato y otra vez cuando el layout ya se calculó

    goToBottom();

    requestAnimationFrame(goToBottom);
}


if (chatMessages) {

    // ¿La persona está leyendo mensajes anteriores?

    chatMessages.addEventListener(
        "scroll",
        () => {

            const distance =
                chatMessages.scrollHeight -
                chatMessages.scrollTop -
                chatMessages.clientHeight;

            stickToBottom =
                distance < 80;

        }
    );
}


// Si el contenido crece (mensajes nuevos, imágenes, etc.)
// y la persona está al final, se mantiene abajo.

if (responseDiv && "ResizeObserver" in window) {

    new ResizeObserver(() => {

        if (stickToBottom) {

            scrollChatToBottom();

        }

    }).observe(responseDiv);
}


// =====================================================
// LIMPIAR MARKDOWN PARA MOSTRAR EN PANTALLA
//
// Se eliminan los símbolos de formato,
// pero NO los emojis.
// =====================================================

function cleanDisplayText(text) {

    if (!text) {
        return "";
    }


    let clean =
        String(text);


    // Links Markdown: "[Fachada](lugares/...jpg)" -> "Fachada".
    // Las fotos ya se muestran en la galería; la ruta no sirve en el chat.
    clean =
        clean.replace(
            /\[([^\]]+)\]\((?:[^()]|\([^()]*\))*\)/g,
            "$1"
        );


    // Negrilla
    clean =
        clean.replace(
            /\*\*(.*?)\*\*/g,
            "$1"
        );


    // Cursiva
    clean =
        clean.replace(
            /(?<!\*)\*([^*\n]+)\*(?!\*)/g,
            "$1"
        );


    // Guiones bajos usados para cursiva/negrilla
    clean =
        clean.replace(
            /__([^_]+)__/g,
            "$1"
        );


    clean =
        clean.replace(
            /(?<!_)_([^_\n]+)_(?!_)/g,
            "$1"
        );


    // Código inline
    clean =
        clean.replace(
            /`([^`]+)`/g,
            "$1"
        );


    // Encabezados Markdown
    clean =
        clean.replace(
            /^#{1,6}\s*/gm,
            ""
        );


    // Citas Markdown
    clean =
        clean.replace(
            /^>\s?/gm,
            ""
        );


    // Separadores
    clean =
        clean.replace(
            /^[-*_]{3,}\s*$/gm,
            ""
        );


    return clean.trim();
}


// =====================================================
// LIMPIAR TEXTO PARA SPEECH
//
// IMPORTANTE:
// Los emojis se mantienen en el chat,
// pero NO se mandan al lector de voz.
// =====================================================

function cleanTextForSpeech(text) {

    if (!text) {
        return "";
    }


    let clean =
        cleanDisplayText(text);


    // =================================================
    // EMOJIS
    // =================================================

    clean =
        clean.replace(
            /[\u{1F000}-\u{1FAFF}]/gu,
            " "
        );


    clean =
        clean.replace(
            /[\u{2600}-\u{27BF}]/gu,
            " "
        );


    // Variaciones de emoji
    clean =
        clean.replace(
            /[\u{FE0E}\u{FE0F}]/gu,
            ""
        );


    // Modificadores de tono de piel
    clean =
        clean.replace(
            /[\u{1F3FB}-\u{1F3FF}]/gu,
            ""
        );


    // Zero width joiner
    clean =
        clean.replace(
            /\u200D/g,
            ""
        );


    // =================================================
    // SÍMBOLOS QUE NO TIENE SENTIDO LEER
    // =================================================

    clean =
        clean.replace(
            /[#*_`~^|\\]+/g,
            " "
        );


    // Viñetas
    clean =
        clean.replace(
            /^[•▪◦●○◆◇■□►▸→←]+\s*/gm,
            ""
        );


    // Links Markdown
    clean =
        clean.replace(
            /\[([^\]]+)\]\([^)]+\)/g,
            "$1"
        );


    // URLs
    clean =
        clean.replace(
            /https?:\/\/\S+/gi,
            " "
        );


    // Múltiples espacios
    clean =
        clean.replace(
            /\s+/g,
            " "
        );


    return clean.trim();
}


// =====================================================
// ENVIAR MENSAJE
// =====================================================

async function askLumi(message) {

    if (!message.trim()) {
        return;
    }


    // Ocultar bienvenida

    if (welcomeMessage) {

        welcomeMessage.style.display =
            "none";
    }


    // Mostrar mensaje usuario

    addUserMessage(message);


    input.value = "";


    // Enviar inmediatamente al último mensaje

    scrollChatToBottom(true);


    // Lumi pensando

    setLumiAnimation("pensando");


    // Loading

    showLoading();


    try {

        const data =
            await sendMessage(message);


        console.log(
            "Respuesta:",
            data
        );


        hideLoading();


        // Mostrar respuesta

        showLumiResponse(data);


        // Si hay texto para hablar

        if (
            data &&
            data.speech
        ) {

            speak(
                data.speech
            );

        }
        else {

            setLumiAnimation("feliz");

        }


    }
    catch (error) {

        console.error(
            "Error comunicando con Lumi:",
            error
        );


        hideLoading();


        setLumiAnimation(
            "error"
        );


        showLumiResponse({

            speech:
                "Lo siento, ocurrió un error al comunicarme con Lumi."

        });

    }


    scrollChatToBottom(true);
}


// =====================================================
// MENSAJE USUARIO
// =====================================================

function addUserMessage(message) {

    const bubble =
        document.createElement(
            "div"
        );


    bubble.className =
        "user-message";


    bubble.textContent =
        message;


    responseDiv.appendChild(
        bubble
    );


    scrollChatToBottom(true);
}


// =====================================================
// RESPUESTA LUMI
// =====================================================

function showLumiResponse(data) {

    if (
        data &&
        data.speech
    ) {

        const bubble =
            document.createElement(
                "div"
            );


        bubble.className =
            "lumi-response";


        // Se limpia SOLO el formato visual.
        // Los emojis permanecen.

        bubble.textContent =
            cleanDisplayText(
                data.speech
            );


        responseDiv.appendChild(
            bubble
        );

    }


    // =================================================
    // FOTOS DEL LUGAR (gallery.js)
    // =================================================

    if (data && data.place && typeof createPhotoGallery === "function") {

        createPhotoGallery(data.place);

    }


    scrollChatToBottom(true);
}


// =====================================================
// LOADING
// =====================================================

function showLoading() {

    document.body.classList.add("is-busy");


    // Evitar duplicados

    if (
        document.getElementById(
            "lumiLoading"
        )
    ) {

        return;
    }


    const loading =
        document.createElement(
            "div"
        );


    loading.id =
        "lumiLoading";


    loading.className =
        "lumi-response loading-message";


    loading.innerHTML = `

        <span>
            Lumi está pensando
        </span>

        <span class="loading-dots">

            <span></span>
            <span></span>
            <span></span>

        </span>

    `;


    responseDiv.appendChild(
        loading
    );


    scrollChatToBottom(true);
}


// =====================================================
// OCULTAR LOADING
// =====================================================

function hideLoading() {

    document.body.classList.remove("is-busy");


    const loading =
        document.getElementById(
            "lumiLoading"
        );


    if (loading) {

        loading.remove();

    }


    scrollChatToBottom(true);
}


// =====================================================
// ENVIAR
// =====================================================

button.addEventListener(
    "click",
    () => {

        askLumi(
            input.value
        );

    }
);


// =====================================================
// ENTER
// =====================================================

input.addEventListener(
    "keydown",
    (event) => {

        if (
            event.key ===
            "Enter"
        ) {

            event.preventDefault();


            askLumi(
                input.value
            );

        }

    }
);


// =====================================================
// INICIALIZAR LUMI
// =====================================================

setLumiAnimation(
    "saludo"
);


scrollChatToBottom(
    false
);