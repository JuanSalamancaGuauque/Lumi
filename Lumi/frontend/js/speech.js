// ======================================
// speech.js
// ======================================

const micButton = document.getElementById("mic");

let recognition;

// Crear reconocimiento
if ("webkitSpeechRecognition" in window) {

    recognition = new webkitSpeechRecognition();

} else if ("SpeechRecognition" in window) {

    recognition = new SpeechRecognition();

} else {

    alert("Tu navegador no soporta reconocimiento de voz.");

}

if (recognition) {

    recognition.lang = "es-CO";
    recognition.interimResults = false;
    recognition.continuous = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {

        micButton.innerHTML = "🔴";

    };

    recognition.onend = () => {

        micButton.innerHTML = "🎤";

    };

    recognition.onerror = (event) => {

        console.error(event);

    };

    recognition.onresult = (event) => {

        const text = event.results[0][0].transcript;

        // usamos la variable input creada en app.js
        input.value = text;

        askLumi(text);

    };

}

micButton.addEventListener("click", () => {

    if (recognition) {

        recognition.start();

    }

});

// ------------------------------
// Voz de Lumi
// ------------------------------

function speak(text) {

    speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.lang = "es-CO";
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.volume = 1;

    speechSynthesis.speak(utterance);

}