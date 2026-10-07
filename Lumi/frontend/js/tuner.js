// =====================================================
// LUMI — Ajustador visual (solo con ?tune en la URL)
//
// - Edita CELULAR (ventana < 900px de ancho) y ESCRITORIO
//   (>= 900px) por separado: cambiar uno NO afecta al otro.
// - Los valores se guardan en este navegador, así que puedes
//   recargar, ensanchar o angostar la ventana sin perderlos.
// - "Copiar CSS" genera el bloque completo (ambos modos).
//   Pégalo en style.css reemplazando TODO lo que está entre
//   ">>> INICIO AJUSTES DEL ESCENARIO <<<" y
//   ">>> FIN AJUSTES DEL ESCENARIO <<<" (inclusive).
// - Sin ?tune en la URL la página usa solo style.css.
// =====================================================

(function () {

    if (!/[?&]tuner?\b/.test(location.search)) {
        return;
    }

    const VARS = [
        ["--trees-w", "Árboles · ancho", 0, 300, 0.5],
        ["--trees-x", "Árboles · horizontal", -100, 100, 0.5],
        ["--trees-y", "Árboles · vertical", -50, 100, 0.5],
        ["--house-w", "Casita · ancho", 10, 150, 0.5],
        ["--house-x", "Casita · horizontal", -100, 100, 0.5],
        ["--house-y", "Casita · vertical", -50, 100, 0.5],
        ["--bird-w", "Pajarito · ancho", 5, 100, 0.25],
        ["--bird-x", "Pajarito · horizontal", -100, 100, 0.25],
        ["--bird-y", "Pajarito · vertical", -50, 100, 0.25]
    ];

    const KEY = "lumiTunerV2";
    const mq = matchMedia("(min-width: 900px)");


    // ---- Valores de style.css (de ambos modos) ----------------

    function readCssDefaults() {

        const result = { mobile: {}, desktop: {} };

        const names = VARS.map(v => v[0]);

        for (const sheet of document.styleSheets) {

            if (sheet.ownerNode && sheet.ownerNode.id === "lumi-tuner-style") {
                continue;
            }

            let rules;

            try {
                rules = sheet.cssRules;
            } catch (e) {
                continue;
            }

            for (const rule of rules) {

                if (
                    rule instanceof CSSStyleRule &&
                    rule.selectorText === ":root"
                ) {

                    names.forEach(n => {
                        const v = rule.style.getPropertyValue(n).trim();
                        if (v) {
                            result.mobile[n] = v;
                            result.desktop[n] = v;
                        }
                    });

                }
                else if (
                    rule instanceof CSSMediaRule &&
                    /min-width:\s*900px/.test(rule.media.mediaText) &&
                    !/max-width|height/.test(rule.media.mediaText)
                ) {

                    for (const inner of rule.cssRules) {

                        if (
                            inner instanceof CSSStyleRule &&
                            inner.selectorText === ":root"
                        ) {

                            names.forEach(n => {
                                const v = inner.style.getPropertyValue(n).trim();
                                if (v) {
                                    result.desktop[n] = v;
                                }
                            });
                        }
                    }
                }
            }
        }

        return result;
    }

    const defaults = readCssDefaults();

    let saved = {};

    try {
        saved = JSON.parse(localStorage.getItem(KEY) || "{}");
    } catch (e) {
        saved = {};
    }

    const values = { mobile: {}, desktop: {} };

    ["mobile", "desktop"].forEach(mode => {
        VARS.forEach(([name]) => {

            const stored = saved[mode] && saved[mode][name];

            values[mode][name] =
                stored !== undefined
                    ? stored
                    : (parseFloat(defaults[mode][name]) || 0);
        });
    });


    // ---- <style> propio: dos bloques independientes -----------

    const tag = document.createElement("style");
    tag.id = "lumi-tuner-style";
    document.head.appendChild(tag);

    function block(mode, indent) {
        return VARS.map(
            ([n]) => indent + n + ": " + values[mode][n] + ";"
        ).join("\n");
    }

    function applyStyles() {

        tag.textContent =
            ":root {\n" + block("mobile", "  ") + "\n}\n" +
            "@media (min-width: 900px) {\n:root {\n" +
            block("desktop", "  ") + "\n}\n}";

        try {
            localStorage.setItem(KEY, JSON.stringify(values));
        } catch (e) { /* sin almacenamiento: no pasa nada */ }
    }

    applyStyles();


    // ---- Panel ------------------------------------------------

    const panel = document.createElement("div");

    panel.style.cssText =
        "position:fixed;top:8px;right:8px;z-index:5000;width:270px;" +
        "max-height:85vh;overflow:auto;background:rgba(0,20,15,.95);" +
        "color:#fff;font:12px Arial,sans-serif;padding:10px;border-radius:10px;";

    document.body.appendChild(panel);

    function render() {

        const mode = mq.matches ? "desktop" : "mobile";

        panel.innerHTML = "";

        const title = document.createElement("div");
        title.style.cssText = "font-weight:bold;cursor:pointer;";
        title.textContent =
            "Editando: " + (mode === "desktop" ? "ESCRITORIO" : "CELULAR") +
            " (clic = plegar)";
        panel.appendChild(title);

        const note = document.createElement("div");
        note.style.cssText = "opacity:.75;margin:4px 0 6px;";
        note.textContent =
            mode === "desktop"
                ? "Para editar celular, angosta la ventana a menos de 900px."
                : "Para editar escritorio, ensancha la ventana a 900px o más.";
        panel.appendChild(note);

        const body = document.createElement("div");
        panel.appendChild(body);

        title.addEventListener("click", () => {
            body.style.display = body.style.display === "none" ? "block" : "none";
        });

        VARS.forEach(([name, label, min, max, step]) => {

            const row = document.createElement("div");
            row.style.cssText = "margin:6px 0;";

            const text = document.createElement("div");
            text.textContent = label;

            const line = document.createElement("div");
            line.style.cssText = "display:flex;gap:6px;align-items:center;";

            const range = document.createElement("input");
            range.type = "range";
            range.min = min;
            range.max = max;
            range.step = step;
            range.value = values[mode][name];
            range.style.cssText = "flex:1;min-width:0;";

            const num = document.createElement("input");
            num.type = "number";
            num.step = step;
            num.value = values[mode][name];
            num.style.cssText = "width:62px;";

            function set(v) {
                const n = parseFloat(v);
                if (isNaN(n)) {
                    return;
                }
                values[mode][name] = n;
                applyStyles();
            }

            range.addEventListener("input", () => {
                num.value = range.value;
                set(range.value);
            });

            num.addEventListener("input", () => {
                range.value = num.value;
                set(num.value);
            });

            line.appendChild(range);
            line.appendChild(num);
            row.appendChild(text);
            row.appendChild(line);
            body.appendChild(row);
        });

        const copy = document.createElement("button");
        copy.textContent = "Copiar CSS (celular + escritorio)";
        copy.style.cssText = "width:100%;margin-top:8px;padding:6px;cursor:pointer;";

        const reset = document.createElement("button");
        reset.textContent = "Restablecer a style.css";
        reset.style.cssText = "width:100%;margin-top:6px;padding:6px;cursor:pointer;";

        const output = document.createElement("textarea");
        output.readOnly = true;
        output.rows = 10;
        output.style.cssText = "width:100%;margin-top:6px;font:11px monospace;";

        copy.addEventListener("click", () => {

            output.value =
                "/* >>> INICIO AJUSTES DEL ESCENARIO <<< */\n\n" +
                ":root {\n" + block("mobile", "    ") + "\n}\n\n" +
                "@media (min-width: 900px) {\n    :root {\n" +
                block("desktop", "        ") + "\n    }\n}\n\n" +
                "/* >>> FIN AJUSTES DEL ESCENARIO <<< */";

            output.select();

            try {
                navigator.clipboard.writeText(output.value);
                copy.textContent = "¡Copiado!";
            } catch (e) {
                copy.textContent = "Copia el texto de abajo";
            }
        });

        reset.addEventListener("click", () => {
            localStorage.removeItem(KEY);
            location.reload();
        });

        body.appendChild(copy);
        body.appendChild(reset);
        body.appendChild(output);
    }

    render();

    // Al cruzar los 900px el panel pasa a editar el otro modo
    mq.addEventListener("change", render);

})();
