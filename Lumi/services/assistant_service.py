# ==========================================
# assistant_service.py
# Cerebro principal de Lumi
# ==========================================

import json
import random

from services.nlp import (
    detect_intent,
    extract_category,
    extract_place_name,
    extract_zona
)

from services.memory import get_memory

from repositories.place_repository import PlaceRepository

from services.gemini_service import ask_gemini


# ==========================================
# Repositorio
# ==========================================

repository = PlaceRepository()


# Intenciones en las que, si hay varios lugares candidatos (por
# categoría o zona), se elige UNO para mostrar sus fotos.
INTENCIONES_CON_DESTACADO = {"recomendar", "buscar_categoria", "ver_fotos"}


def _para_gemini(place):
    """
    Copia del lugar SIN las rutas de las fotos. Las fotos las muestra
    el frontend; si Gemini las ve, las escribe en el chat como links.
    """
    return {
        key: value
        for key, value in place.items()
        if key not in ("imagenes", "imagen_principal")
    }


def _elegir_recomendacion(candidatos, memory):
    """
    Elige un lugar al azar, evitando repetir el último del que se
    habló si hay otras opciones.
    """
    if not candidatos:
        return None

    last_place = memory.get_last_place()

    if last_place and len(candidatos) > 1:
        candidatos = [
            p for p in candidatos if p["id"] != last_place["id"]
        ]

    return random.choice(candidatos)


class AssistantService:

    def process_message(self, message, session_id):

        # ==========================================
        # 0. Memoria de ESTA sesión
        # ==========================================

        memory = get_memory(session_id)

        # 🔎 Debug temporal: confirma que cada navegador tiene
        # su propia memoria y que el historial va creciendo.
        # Puedes borrar esta línea cuando ya confíes en el flujo.
        print(f"🔑 SESSION_ID: {session_id} | Turnos en historial: {len(memory.get_history())}")

        # ==========================================
        # 1. Analizar mensaje
        # ==========================================

        intent = detect_intent(message, debug=True)

        category = extract_category(message)

        place_name = extract_place_name(message)

        zona = extract_zona(message)

        print(f"""
========================
MENSAJE: {message}
INTENT: {intent}
LUGAR: {place_name}
CATEGORÍA: {category}
ZONA: {zona}
========================
""")

        # ==========================================
        # 2. Obtener contexto
        # ==========================================

        context = {}

        context["usuario"] = message

        context["intencion"] = intent

        context["categoria"] = category

        context["lugar_mencionado"] = place_name

        # 🆕 Historial reciente de la conversación (últimos turnos).
        # Va ANTES de las ramas de saludo/agradecimiento/despedida
        # para que también ellas tengan acceso a él si hace falta.
        context["historial_reciente"] = memory.get_history()


        # ==========================================
        # 3. Conversación básica
        # ==========================================

        if intent == "saludo":

            context["tipo_respuesta"] = "saludo"

            respuesta = ask_gemini(
                message,
                json.dumps(
                    context,
                    ensure_ascii=False,
                    indent=2
                )
            )

            memory.add_turn(message, respuesta)

            return {
                "intent": intent,
                "speech": respuesta
            }


        if intent == "agradecimiento":

            context["tipo_respuesta"] = "agradecimiento"

            respuesta = ask_gemini(
                message,
                json.dumps(
                    context,
                    ensure_ascii=False,
                    indent=2
                )
            )

            memory.add_turn(message, respuesta)

            return {
                "intent": intent,
                "speech": respuesta
            }


        if intent == "despedida":

            context["tipo_respuesta"] = "despedida"

            respuesta = ask_gemini(
                message,
                json.dumps(
                    context,
                    ensure_ascii=False,
                    indent=2
                )
            )

            memory.add_turn(message, respuesta)

            return {
                "intent": intent,
                "speech": respuesta
            }


        # ==========================================
        # 4. Buscar lugar específico
        # ==========================================

        place = None

        # True si el lugar NO lo mencionó el usuario en este mensaje,
        # sino que se recuperó de la memoria (preguntas de seguimiento).
        place_from_memory = False

        if place_name:

            place = repository.get_by_name(place_name)

        # ==========================================
        # 5. Usar memoria
        # ==========================================

        # Solo para seguimientos ("¿y a qué hora abre?", "¿fotos?").
        # Si el usuario pide una categoría, una zona o una
        # recomendación nueva, el lugar anterior ya no aplica.
        es_seguimiento = (
            not category
            and not zona
            and intent != "recomendar"
        )

        if place is None and es_seguimiento:

            last_place = memory.get_last_place()

            if last_place:

                place = last_place

                place_from_memory = True

                context["lugar_memoria"] = last_place["nombre"]


        # ==========================================
        # 6. Si encontró un lugar
        # ==========================================

        if place:

            memory.remember_place(place)

            context["lugar"] = _para_gemini(place)


        # ==========================================
        # 7. Buscar por categoría
        # ==========================================

        places = []

        if category:

            places = repository.get_by_category(category)

            if places:

                memory.remember_category(category)

                context["lugares_categoria"] = [
                    _para_gemini(p) for p in places
                ]


        # ==========================================
        # 7.5. Buscar por zona (ej. "Chapinero")
        # ==========================================

        if zona:

            zona_places = repository.get_by_zona(zona)

            if zona_places:

                context["zona"] = zona

                context["lugares_zona"] = [
                    _para_gemini(p) for p in zona_places
                ]

                # Se agregan a "places" para que el frontend reciba
                # también estos lugares (mismo campo que categorías),
                # sin duplicar los que ya estuvieran por categoría.
                ids_ya_incluidos = {p["id"] for p in places}

                for zona_place in zona_places:
                    if zona_place["id"] not in ids_ya_incluidos:
                        places.append(zona_place)


        # ==========================================
        # 8. Lugar destacado (el de las fotos)
        # ==========================================

        # Es el ÚNICO lugar cuyas fotos se mandan al frontend, y a
        # Gemini se le pide que hable de ese mismo lugar. Así el texto
        # y la foto siempre coinciden.
        featured = None

        if place and not place_from_memory:

            # El usuario nombró el lugar en este mensaje.
            featured = place

        elif place and intent == "ver_fotos":

            # "¿Imágenes?" justo después de hablar de un lugar.
            featured = place

        elif places and intent in INTENCIONES_CON_DESTACADO:

            featured = _elegir_recomendacion(places, memory)

        elif intent == "recomendar":

            featured = _elegir_recomendacion(repository.get_all(), memory)

        if featured and featured is not place:

            memory.remember_place(featured)

            context["recomendacion"] = _para_gemini(featured)

        # Le dice a Gemini de qué lugar verá fotos el usuario (o que
        # no hay fotos que mostrar, para que pregunte de qué lugar).
        if intent == "ver_fotos":

            context["tipo_respuesta"] = "ver_fotos"

        context["fotos_en_pantalla"] = (
            featured["nombre"] if featured else None
        )


        # ==========================================
        # 9. Si no hay contexto específico
        # ==========================================

        if not place and not places and not featured:

            all_places = repository.get_all()

            context["lugares_disponibles"] = [
                _para_gemini(p) for p in all_places
            ]


        # ==========================================
        # 10. Convertir contexto
        # ==========================================

        context_text = json.dumps(
            context,
            ensure_ascii=False,
            indent=2
        )


        # ==========================================
        # 11. SIEMPRE consultar Gemini
        # ==========================================

        print("🤖 Generando respuesta con Gemini...")

        respuesta = ask_gemini(
            message,
            context_text
        )

        memory.add_turn(message, respuesta)


        # ==========================================
        # 12. Respuesta final
        # ==========================================

        response = {
            "intent": intent,
            "speech": respuesta
        }


        # ==========================================
        # 13. Datos para frontend
        # ==========================================

        if featured:

            response["place"] = featured


        if places:

            response["places"] = places


        return response
