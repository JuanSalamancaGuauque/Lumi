// =====================================================
// LUMI
// RECONOCIMIENTO DE VOZ
// =====================================================

const micButton =
    document.getElementById("mic");


let recognition = null;


// =====================================================
// COMPROBAR SOPORTE
// =====================================================

if ("webkitSpeechRecognition" in window) {

    recognition =
        new webkitSpeechRecognition();

}
else if ("SpeechRecognition" in window) {

    recognition =
        new SpeechRecognition();

}


// =====================================================
// CONFIGURACIÓN
// =====================================================

if (recognition) {

    recognition.lang = "es-CO";

    recognition.interimResults = false;

    recognition.continuous = false;

    recognition.maxAlternatives = 1;


    // =================================================
    // EMPEZÓ A ESCUCHAR
    // =================================================

    recognition.onstart = () => {

        micButton.textContent = "🔴";

        micButton.classList.add(
            "recording"
        );

        input.placeholder =
            "Escuchando...";

    };


    // =================================================
    // DEJÓ DE ESCUCHAR
    // =================================================

    recognition.onend = () => {

        micButton.textContent = "🎙";

        micButton.classList.remove(
            "recording"
        );

        input.placeholder =
            "Soy Lumi! Pregúntame algo...";

    };


    // =================================================
    // ERROR
    // =================================================

    recognition.onerror = (event) => {

        console.error(
            "Error de reconocimiento:",
            event
        );

        micButton.textContent = "🎙";

        micButton.classList.remove(
            "recording"
        );

        input.placeholder =
            "Soy Lumi! Pregúntame algo...";

    };


    // =================================================
    // RESULTADO
    // =================================================

    recognition.onresult = (event) => {

        const text =
            event.results[0][0]
                .transcript;


        input.value = text;


        askLumi(text);

    };

}


// =====================================================
// BOTÓN MICRÓFONO
// =====================================================

micButton.addEventListener(
    "click",
    () => {

        if (!recognition) {

            alert(
                "Tu navegador no soporta reconocimiento de voz."
            );

            return;

        }


        try {

            recognition.start();

        }
        catch (error) {

            console.error(error);

        }

    }
);


// =====================================================
// VOZ DE LUMI
// =====================================================

function speak(text) {

    if (
        !("speechSynthesis" in window)
    ) {

        // 🆕 Sin soporte de voz: no hay "hablando" que mostrar,
        // pasamos directo a feliz para no dejar a Lumi
        // pensando para siempre.
        setAvatarState("feliz");

        return;

    }


    speechSynthesis.cancel();


    const utterance =
        new SpeechSynthesisUtterance(
            text
        );


    utterance.lang = "es-CO";

    utterance.rate = 1;

    utterance.pitch = 1;

    utterance.volume = 1;


    // 🆕 Avatar sincronizado con el ciclo real de la voz
    utterance.onstart = () => {

        setAvatarState("hablando");

    };

    utterance.onend = () => {

        setAvatarState("feliz");

    };

    utterance.onerror = () => {

        setAvatarState("feliz");

    };


    speechSynthesis.speak(
        utterance
    );

}