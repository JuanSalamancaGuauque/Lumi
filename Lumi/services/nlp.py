import re
import unicodedata
from difflib import get_close_matches

from repositories.place_repository import PlaceRepository

repository = PlaceRepository()


# ---------------------------------------------------------------------------
# Normalización de texto
# ---------------------------------------------------------------------------

def normalize_text(text):
    """
    Normaliza el texto: minúsculas, sin tildes/acentos, sin signos de
    puntuación y sin espacios múltiples.

    Al quitar los acentos ya NO es necesario duplicar cada palabra clave
    con y sin tilde (ej: "informacion" / "información").
    """
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# Alias para mantener compatibilidad con el nombre original
clean_text = normalize_text


def _keyword_pattern(keyword):
    """
    Compila un patrón regex con límites de palabra para cada keyword,
    soportando keywords de una o varias palabras (ej: "como llegar").
    Esto evita falsos positivos como que "hora" matchee dentro de
    "ahorita" o "ahora mismo" de forma no deseada.
    """
    keyword = normalize_text(keyword)
    escaped = re.escape(keyword).replace(r"\ ", r"\s+")
    return re.compile(rf"\b{escaped}\b")


# ---------------------------------------------------------------------------
# Diccionario de categorías (sinónimos)
# ---------------------------------------------------------------------------

CATEGORIES = {
    "museo": [
        "museo", "museos", "galeria", "galerias", "exposicion",
        "exposiciones", "arte", "cultural", "patrimonio", "coleccion",
    ],
    "parque": [
        "parque", "parques", "jardin", "jardines", "plaza", "plazas",
        "zona verde", "bosque", "area verde", "reserva natural",
    ],
    "mirador": [
        "mirador", "miradores", "vista", "vistas", "panoramica",
        "mirante", "cerro", "vista panoramica",
    ],
}


# ---------------------------------------------------------------------------
# Diccionario de intenciones (orden = prioridad en caso de empate)
# ---------------------------------------------------------------------------

INTENTS = {
    "saludo": [
        "hola", "holaa", "buenas", "buenos dias", "buenas tardes",
        "buenas noches", "hey", "ey", "que tal", "que hay", "que mas",
        "quiubo", "saludos",
    ],

    "despedida": [
        "adios", "hasta luego", "nos vemos", "chao", "chau", "bye",
        "hasta pronto", "me despido", "listo gracias eso es todo",
    ],

    "agradecimiento": [
        "gracias", "muchas gracias", "te agradezco", "mil gracias",
        "genial gracias", "perfecto gracias", "excelente gracias",
    ],

    "consultar_horario": [
        "horario", "horarios", "hora", "horas", "abre", "abierto",
        "abren", "cierra", "cierre", "cierran", "a que hora",
        "esta abierto", "esta abierta", "dias de atencion",
        "atencion al publico",
    ],

    "consultar_ubicacion": [
        "donde", "ubicacion", "ubicado", "ubicada", "queda", "quedan",
        "como llegar", "direccion", "en que parte", "en que zona",
        "en que barrio", "por donde", "coordenadas", "mapa",
    ],

    "consultar_descripcion": [
        "hablame", "informacion", "info", "cuentame", "descripcion",
        "que es", "de que se trata", "en que consiste", "detalles",
        "mas sobre", "que tiene", "que ofrece", "historia de", "quiero saber",
        "quiero saber mas", "saber mas", "más información", "mas informacion",
        "cuéntame más", "cuentame mas", "dime mas", "dime más", "explícame", "explicame",
    ],

    "buscar_categoria": [
        keyword
        for keywords in CATEGORIES.values()
        for keyword in keywords
    ],

    "recomendar": [ 
        "recomienda",
        "recomiendame",
        "recomendacion",
        "recomendaciones",
        "que visitar",
        "que me recomiendas",
        "cual recomiendas",
        "quiero ir",
        "quiero visitar",
        "me gustaria visitar",
        "estoy buscando",
        "busco",
        "quiero conocer",
        "donde puedo ir",
        "que lugar",
        "que sitio",
        "sugerencia",
        "sugiereme"

    ],
}

# Lista plana de (keyword, intent) usada para el fallback de coincidencia
# aproximada (tolerante a errores de tipeo)
_ALL_KEYWORDS = [
    (keyword, intent)
    for intent, keywords in INTENTS.items()
    for keyword in keywords
]
_INTENT_ORDER = list(INTENTS.keys())


def _fuzzy_intent(normalized_text, cutoff=0.82):
    """
    Fallback para cuando ninguna keyword matchea exactamente.
    Compara cada palabra del texto contra todas las keywords conocidas
    para tolerar errores de tipeo (ej: "recomiendame" -> "recomindame").
    """
    words = normalized_text.split()
    all_keywords = [kw for kw, _ in _ALL_KEYWORDS]

    for word in words:
        matches = get_close_matches(word, all_keywords, n=1, cutoff=cutoff)
        if matches:
            matched_keyword = matches[0]
            for keyword, intent in _ALL_KEYWORDS:
                if keyword == matched_keyword:
                    return intent
    return None


def detect_intent(text, debug=False):
    """
    Detecta la intención principal del usuario usando un sistema de
    puntuación: cuenta cuántas keywords de cada intención aparecen en el
    texto (dando más peso a keywords de varias palabras, por ser más
    específicas) y elige la de mayor puntaje. En caso de empate, gana la
    intención declarada primero en INTENTS (más específica).

    Si no hay ninguna coincidencia exacta, intenta una coincidencia
    aproximada (tolerante a errores de tipeo) antes de devolver
    "desconocida".
    """
    normalized = normalize_text(text)
    scores = {}

    for intent, keywords in INTENTS.items():
        score = 0
        matched = []

        for keyword in keywords:
            pattern = _keyword_pattern(keyword)
            if pattern.search(normalized):
                weight = max(2, len(keyword.split()))  # multi-palabra pesa más
                score += weight
                matched.append(keyword)

        if score:
            scores[intent] = score
            if debug:
                print(f"Intent '{intent}' -> score {score} ({matched})")

    if not scores:
        fuzzy = _fuzzy_intent(normalized)
        if fuzzy:
            if debug:
                print(f"✅ Coincidencia aproximada -> {fuzzy}")
            return fuzzy

        if debug:
            print("❌ No encontré ninguna coincidencia")
        return "desconocida"

    # Si el usuario habla de visitar o buscar un lugar,
    # damos prioridad a la intención de recomendación.
    travel_words = [
        "quiero ir",
        "quiero visitar",
        "me gustaria",
        "estoy buscando",
        "busco",
        "donde puedo ir"
    ]

    if any(word in normalized for word in travel_words):
        scores["recomendar"] = scores.get("recomendar", 0) + 3

    best_intent = max(
        scores.items(),
        key=lambda item: (item[1], -_INTENT_ORDER.index(item[0])),
    )[0]

    if debug:
        print(f"✅ Intención elegida: {best_intent}")

    return best_intent


def extract_category(text):
    """
    Busca la categoría mencionada usando el diccionario de sinónimos.
    Si el texto menciona keywords de más de una categoría, devuelve la
    que tenga más coincidencias.
    """
    normalized = normalize_text(text)
    best_category = None
    best_score = 0

    for category, keywords in CATEGORIES.items():
        score = sum(
            1 for keyword in keywords if _keyword_pattern(keyword).search(normalized)
        )
        if score > best_score:
            best_score = score
            best_category = category

    return best_category


def extract_place_name(text, fuzzy_cutoff=0.85):
    """
    Busca si el usuario mencionó un lugar específico. Primero intenta una
    coincidencia exacta (con límites de palabra) y, si no encuentra nada,
    intenta una coincidencia aproximada para tolerar errores de tipeo o
    nombres escritos parcialmente.
    """
    normalized = normalize_text(text)
    places = repository.get_all()

    # 1. Coincidencia exacta (normalizada)
    exact_matches = []
    for place in places:
        place_name_normalized = normalize_text(place["name"])
        if _keyword_pattern(place_name_normalized).search(normalized):
            exact_matches.append(place)

    if exact_matches:
        # Si hay varias coincidencias, devolver el nombre más largo/específico
        best = max(exact_matches, key=lambda p: len(p["name"]))
        return best["name"]

    # 2. Coincidencia aproximada (tolerante a errores de tipeo)
    place_names = {normalize_text(p["name"]): p["name"] for p in places}
    words = normalized.split()

    # Compara tanto palabras individuales como el texto completo
    candidates = list(place_names.keys()) 
    matches = get_close_matches(normalized, candidates, n=1, cutoff=fuzzy_cutoff)
    if matches:
        return place_names[matches[0]]

    for word in words:
        matches = get_close_matches(word, candidates, n=1, cutoff=fuzzy_cutoff)
        if matches:
            return place_names[matches[0]]

    return None