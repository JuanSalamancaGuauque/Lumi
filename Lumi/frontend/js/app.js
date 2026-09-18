// =====================================================
// LUMI
// APP
// =====================================================

// =====================================================
// ICONOGRAFÍA POR CATEGORÍA
// =====================================================
// El QTA menciona la iconografía como parte de la
// accesibilidad: un ícono ayuda a reconocer de qué tipo de
// lugar se trata de un vistazo, sin depender solo del texto.

const CATEGORY_ICONS = {
    museo: "🏛️",
    parque: "🌳",
    mirador: "🌄",
    iglesia: "⛪",
    libreria: "📚",
    gastronomia: "🍽️",
    restaurante: "🍴",
    sendero: "🥾",
};


function getCategoryIcon(place) {

    if (
        Array.isArray(place.categorias) &&
        place.categorias.length > 0
    ) {

        return (
            CATEGORY_ICONS[
                place.categorias[0]
            ] || "📍"
        );

    }

    return "📍";

}


const input =
    document.getElementById("message");

const button =
    document.getElementById("send");

const responseDiv =
    document.getElementById("response");

const welcomeMessage =
    document.getElementById(
        "welcome-message"
    );

const imageModal =
    document.getElementById(
        "imageModal"
    );

const modalImage =
    document.getElementById(
        "modalImage"
    );

const modalTitle =
    document.getElementById(
        "modalTitle"
    );

const modalDescription =
    document.getElementById(
        "modalDescription"
    );

const closeModal =
    document.getElementById(
        "closeModal"
    );


// =====================================================
// PREGUNTAR
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


    // Mostrar loading

    showLoading();

    // 🆕 Lumi "piensa" mientras esperamos al backend
    setAvatarState("pensando");


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


        // Hablar
        // (avatar.js pasa a "hablando" cuando arranca la voz,
        // y a "feliz" cuando termina, ver speech.js)

        if (data.speech) {

            speak(data.speech);

        }
        else {

            setAvatarState("feliz");

        }

    }
    catch (error) {

        console.error(error);


        hideLoading();

        // 🆕 Algo falló de verdad (red, servidor caído, etc.)
        setAvatarState("error");

        setTimeout(() => {

            setAvatarState("feliz");

        }, 4000);


        showLumiResponse({

            speech:
                "Lo siento, ocurrió un error al comunicarme con Lumi."

        });

    }

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

}


// =====================================================
// RESPUESTA
// =====================================================

function showLumiResponse(data) {

    if (data.speech) {

        const bubble =
            document.createElement(
                "div"
            );


        bubble.className =
            "lumi-response";


        bubble.textContent =
            data.speech;


        responseDiv.appendChild(
            bubble
        );

    }


    // Solo si el backend
    // realmente manda lugares

    const places =
        getPlacesFromResponse(data);


    if (places.length > 0) {

        createPlacesGallery(
            places
        );

    }

}


// =====================================================
// LUGARES
// =====================================================

function getPlacesFromResponse(data) {

    // 🆕 El backend a veces manda un solo lugar (data.place,
    // ej. al preguntar por "Monserrate") y otras veces varios
    // (data.places, por categoría o zona). Antes solo se
    // revisaba "places", así que las respuestas de un solo
    // lugar nunca mostraban nada. Ahora se unifican ambos casos
    // en una sola lista, sin duplicar si el mismo lugar viene
    // en las dos.

    const places = [];

    if (data.place) {

        places.push(
            data.place
        );

    }


    if (
        Array.isArray(
            data.places
        )
    ) {

        data.places.forEach(
            (place) => {

                const yaEsta =
                    places.some(
                        (p) =>
                            p.id ===
                            place.id
                    );

                if (!yaEsta) {

                    places.push(
                        place
                    );

                }

            }
        );

    }


    return places;

}


// =====================================================
// GALERÍA
// =====================================================

function createPlacesGallery(
    places
) {

    const gallery =
        document.createElement(
            "div"
        );


    gallery.className =
        "places-grid";


    places
        .slice(0, 4)
        .forEach(
            (place) => {

                const card =
                    document.createElement(
                        "div"
                    );


                card.className =
                    "place-card";


                // 🆕 Campos reales que manda el backend
                // (antes se usaban name/image/description,
                // que no existen: siempre salían vacíos).
                const nombre =
                    place.nombre ||
                    "Lugar";

                const descripcion =
                    place.descripcion ||
                    "";

                // imagen_principal es solo el nombre del
                // archivo (ej. "monserrate.jpg"), hay que
                // anteponerle la ruta donde Flask lo sirve.
                // Puede venir null si el lugar todavía no
                // tiene foto real (la mayoría de Chapinero).
                const imageUrl =
                    place.imagen_principal
                        ? "/static/images/" +
                          encodeURIComponent(
                              place.imagen_principal
                          )
                        : null;


                if (imageUrl) {

                    const image =
                        document.createElement(
                            "img"
                        );

                    image.src =
                        imageUrl;

                    image.alt =
                        nombre;

                    card.appendChild(
                        image
                    );

                }


                const info =
                    document.createElement(
                        "div"
                    );


                info.className =
                    "place-info";


                const title =
                    document.createElement(
                        "h3"
                    );


                title.textContent =
                    getCategoryIcon(place) +
                    " " +
                    nombre;


                const description =
                    document.createElement(
                        "p"
                    );


                description.textContent =
                    descripcion;


                info.appendChild(title);

                info.appendChild(description);

                card.appendChild(info);


                card.addEventListener(
                    "click",
                    () => {

                        openImage(
                            imageUrl,
                            nombre,
                            descripcion
                        );

                    }
                );


                gallery.appendChild(card);

            }
        );


    responseDiv.appendChild(
        gallery
    );

}


// =====================================================
// MODAL
// =====================================================

function openImage(
    image,
    title,
    description
) {

    // 🆕 Varios lugares (sobre todo los de Chapinero) todavía
    // no tienen foto real. En vez de mostrar un ícono de
    // imagen rota, ocultamos el <img> por completo.
    if (image) {

        modalImage.src =
            image;

        modalImage.style.display =
            "";

    }
    else {

        modalImage.src = "";

        modalImage.style.display =
            "none";

    }

    modalTitle.textContent =
        title;

    modalDescription.textContent =
        description;


    imageModal.classList.add(
        "active"
    );

}


function closeImageModal() {

    imageModal.classList.remove(
        "active"
    );

    modalImage.src = "";

    modalImage.style.display =
        "";

}


closeModal.addEventListener(
    "click",
    closeImageModal
);


imageModal.addEventListener(
    "click",
    (event) => {

        if (
            event.target ===
            imageModal
        ) {

            closeImageModal();

        }

    }
);


// =====================================================
// LOADING
// =====================================================

function showLoading() {

    const loading =
        document.createElement(
            "div"
        );


    loading.id =
        "lumiLoading";


    loading.className =
        "lumi-response loading-message";


    loading.textContent =
        "Lumi está pensando...";


    responseDiv.appendChild(
        loading
    );

}


function hideLoading() {

    const loading =
        document.getElementById(
            "lumiLoading"
        );


    if (loading) {

        loading.remove();

    }

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
            event.key === "Enter"
        ) {

            event.preventDefault();


            askLumi(
                input.value
            );

        }

    }
);