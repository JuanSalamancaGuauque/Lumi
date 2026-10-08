// =====================================================
// LUMI
// RECONOCIMIENTO Y SÍNTESIS DE VOZ
// =====================================================


// =====================================================
// ELEMENTOS
// =====================================================

const micButton =
    document.getElementById("mic");


const inputSpeech =
    document.getElementById("message");


const lumiAvatarSpeech =
    document.getElementById(
        "lumi-avatar-image"
    );


// =====================================================
// RECONOCIMIENTO DE VOZ
// =====================================================

let recognition = null;

let isRecording = false;

let baseText = "";   // texto que ya había en el campo antes de grabar


// =====================================================
// COMPROBAR SOPORTE
// =====================================================

if (
    "webkitSpeechRecognition"
    in window
) {

    recognition =
        new webkitSpeechRecognition();

}
else if (
    "SpeechRecognition"
    in window
) {

    recognition =
        new SpeechRecognition();

}


// =====================================================
// CONFIGURACIÓN
// =====================================================

if (recognition) {

    recognition.lang =
        "es-CO";


    recognition.interimResults =
        true;


    recognition.continuous =
        false;


    recognition.maxAlternatives =
        1;


    // =================================================
    // EMPEZÓ A ESCUCHAR
    // =================================================

    recognition.onstart =
        () => {

            isRecording = true;

            baseText = inputSpeech.value.trim();



            micButton.classList.add(
                "recording"
            );


            inputSpeech.placeholder =
                "Escuchando...";


        };


    // =================================================
    // DEJÓ DE ESCUCHAR
    // =================================================

    recognition.onend =
        () => {

            isRecording = false;



            micButton.classList.remove(
                "recording"
            );


            inputSpeech.placeholder =
                "Soy Lumi! Pregúntame algo...";

        };


    // =================================================
    // ERROR
    // =================================================

    recognition.onerror =
        (event) => {

            isRecording = false;


            console.error(
                "Error de reconocimiento:",
                event
            );


            micButton.classList.remove(
                "recording"
            );


            inputSpeech.placeholder =
                "Soy Lumi! Pregúntame algo...";

        };


    // =================================================
    // RESULTADO
    // =================================================

    recognition.onresult =
        (event) => {

            // Se junta lo ya confirmado + lo que se está diciendo ahora

            let transcript = "";

            for (let i = 0; i < event.results.length; i++) {

                transcript +=
                    event.results[i][0].transcript;

            }


            inputSpeech.value =
                (baseText
                    ? baseText + " "
                    : "") +
                transcript.trim();


            // NO se envía: la persona decide cuándo enviarlo.

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

            if (isRecording) {

                // Segundo toque: detener la grabación

                recognition.stop();

            }
            else {

                // Que Lumi no se escuche a sí misma

                if ("speechSynthesis" in window) {
                    speechSynthesis.cancel();
                }

                recognition.start();

            }

        }
        catch (error) {

            console.error(
                error
            );

        }

    }
);


// =====================================================
// LIMPIEZA ESPECIAL PARA SPEECH
//
// Esta función también se deja aquí para que
// speech.js sea independiente.
// =====================================================

function prepareTextForSpeech(text) {

    if (!text) {
        return "";
    }


    let clean =
        String(text);


    // Links Markdown: "[Fachada](lugares/...jpg)" -> "Fachada".
    // Lumi no debe leer rutas de archivos en voz alta.
    clean =
        clean.replace(
            /\[([^\]]+)\]\((?:[^()]|\([^()]*\))*\)/g,
            "$1"
        );


    // =================================================
    // MARKDOWN
    // =================================================

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


    // Subrayados Markdown

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


    // Código

    clean =
        clean.replace(
            /`([^`]+)`/g,
            "$1"
        );


    // Títulos

    clean =
        clean.replace(
            /^#{1,6}\s*/gm,
            ""
        );


    // Citas

    clean =
        clean.replace(
            /^>\s?/gm,
            ""
        );


    // Links Markdown

    clean =
        clean.replace(
            /\[([^\]]+)\]\([^)]+\)/g,
            "$1"
        );


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


    clean =
        clean.replace(
            /[\u{1F3FB}-\u{1F3FF}]/gu,
            ""
        );


    clean =
        clean.replace(
            /[\u{FE0E}\u{FE0F}]/gu,
            ""
        );


    clean =
        clean.replace(
            /\u200D/g,
            ""
        );


    // =================================================
    // SÍMBOLOS
    // =================================================

    clean =
        clean.replace(
            /[#*_`~^|\\]+/g,
            " "
        );


    clean =
        clean.replace(
            /^[•▪◦●○◆◇■□►▸→←]+\s*/gm,
            ""
        );


    // =================================================
    // URLs
    // =================================================

    clean =
        clean.replace(
            /https?:\/\/\S+/gi,
            " "
        );


    // =================================================
    // ESPACIOS
    // =================================================

    clean =
        clean.replace(
            /\s+/g,
            " "
        );


    return clean.trim();
}


// =====================================================
// VOZ DE LUMI
// =====================================================

function speak(text) {

    if (
        !(
            "speechSynthesis"
            in window
        )
    ) {

        console.warn(
            "Speech Synthesis no está disponible."
        );


        setLumiAnimation(
            "feliz"
        );


        return;
    }


    // =================================================
    // LIMPIAR TEXTO
    // =================================================

    const cleanText =
        prepareTextForSpeech(
            text
        );


    if (!cleanText) {

        setLumiAnimation(
            "feliz"
        );

        return;
    }


    // =================================================
    // CANCELAR VOZ ANTERIOR
    // =================================================

    speechSynthesis.cancel();


    // =================================================
    // GIF HABLANDO
    // =================================================

    setLumiAnimation(
        "hablando"
    );


    // =================================================
    // CREAR VOZ
    // =================================================

    const utterance =
        new SpeechSynthesisUtterance(
            cleanText
        );


    utterance.lang =
        "es-CO";


    utterance.rate =
        1;


    utterance.pitch =
        1;


    utterance.volume =
        1;


    // =================================================
    // CUANDO COMIENZA
    // =================================================

    utterance.onstart =
        () => {

            setLumiAnimation(
                "hablando"
            );

        };


    // =================================================
    // CUANDO TERMINA
    // =================================================

    utterance.onend =
        () => {

            setLumiAnimation(
                "feliz"
            );

        };


    // =================================================
    // SI OCURRE ERROR
    // =================================================

    utterance.onerror =
        (event) => {

            console.error(
                "Error de síntesis de voz:",
                event
            );


            setLumiAnimation(
                "error"
            );

        };


    // =================================================
    // HABLAR
    // =================================================

    speechSynthesis.speak(
        utterance
    );

}