// =====================================================
// LUMI
// ACCESIBILIDAD
// =====================================================
//
// Uno de los 3 pilares de la innovacion segun la propuesta
// QTA: "diseño inclusivo como principio estructural". Dos
// ajustes simples que ya cubren buena parte de las
// necesidades mas comunes de personas con baja alfabetizacion
// digital, adultos mayores o dificultad visual:
//
//   - Texto mas grande
//   - Alto contraste
//
// Las preferencias se guardan en el navegador (localStorage),
// asi se recuerdan la proxima vez que la persona entre.

const STORAGE_KEY_TEXT =
    "lumi_texto_grande";

const STORAGE_KEY_CONTRAST =
    "lumi_alto_contraste";

const textToggleButton =
    document.getElementById(
        "toggle-text-size"
    );

const contrastToggleButton =
    document.getElementById(
        "toggle-contrast"
    );


function leerPreferencia(clave) {

    try {

        return (
            localStorage.getItem(clave) ===
            "true"
        );

    }
    catch (error) {

        // Modo incognito / navegador que bloquea
        // localStorage: seguimos sin romper la app.
        return false;

    }

}


function guardarPreferencia(clave, valor) {

    try {

        localStorage.setItem(
            clave,
            String(valor)
        );

    }
    catch (error) {

        // No se pudo guardar; no pasa nada,
        // simplemente no se recordará la próxima vez.

    }

}


function aplicarPreferencias() {

    const textoGrande =
        leerPreferencia(STORAGE_KEY_TEXT);

    const altoContraste =
        leerPreferencia(
            STORAGE_KEY_CONTRAST
        );

    document.body.classList.toggle(
        "text-large",
        textoGrande
    );

    document.body.classList.toggle(
        "high-contrast",
        altoContraste
    );

    if (textToggleButton) {

        textToggleButton.setAttribute(
            "aria-pressed",
            String(textoGrande)
        );

    }

    if (contrastToggleButton) {

        contrastToggleButton.setAttribute(
            "aria-pressed",
            String(altoContraste)
        );

    }

}


if (textToggleButton) {

    textToggleButton.addEventListener(
        "click",
        () => {

            const actual =
                leerPreferencia(
                    STORAGE_KEY_TEXT
                );

            guardarPreferencia(
                STORAGE_KEY_TEXT,
                !actual
            );

            aplicarPreferencias();

        }
    );

}


if (contrastToggleButton) {

    contrastToggleButton.addEventListener(
        "click",
        () => {

            const actual =
                leerPreferencia(
                    STORAGE_KEY_CONTRAST
                );

            guardarPreferencia(
                STORAGE_KEY_CONTRAST,
                !actual
            );

            aplicarPreferencias();

        }
    );

}


// Aplicar preferencias guardadas al cargar la página
aplicarPreferencias();