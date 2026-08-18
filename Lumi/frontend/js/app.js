// ======================================
// app.js
// ======================================

const input = document.getElementById("message");
const button = document.getElementById("send");
const responseDiv = document.getElementById("response");

async function askLumi(message) {

    if (!message.trim()) return;

    try {

        const data = await sendMessage(message);

        console.log(data);

        responseDiv.innerHTML = data.speech;

        speak(data.speech);

    } catch (error) {

        console.error(error);

        responseDiv.innerHTML = "Error al comunicarse con el servidor.";

    }

}

button.addEventListener("click", () => {

    askLumi(input.value);

});

input.addEventListener("keydown", (event) => {

    if (event.key === "Enter") {

        askLumi(input.value);

    }

});