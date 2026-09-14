// =====================================================
// LUMI
// APP
// =====================================================

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

        if (data.speech) {

            speak(data.speech);

        }

    }
    catch (error) {

        console.error(error);


        hideLoading();


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

    if (
        Array.isArray(
            data.places
        )
    ) {

        return data.places;

    }


    if (
        Array.isArray(
            data.images
        )
    ) {

        return data.images.map(
            (image, index) => {

                return {

                    name:
                        "Lugar " +
                        (index + 1),

                    image:
                        image,

                    description:
                        "Descubre este lugar con Lumi."

                };

            }
        );

    }


    return [];

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


                const image =
                    document.createElement(
                        "img"
                    );


                image.src =
                    place.image;


                image.alt =
                    place.name ||
                    "Lugar";


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
                    place.name ||
                    "Lugar";


                const description =
                    document.createElement(
                        "p"
                    );


                description.textContent =
                    place.description ||
                    "";


                info.appendChild(title);

                info.appendChild(description);

                card.appendChild(image);

                card.appendChild(info);


                card.addEventListener(
                    "click",
                    () => {

                        openImage(
                            place.image,
                            place.name ||
                                "Lugar",
                            place.description ||
                                ""
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

    modalImage.src =
        image;

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