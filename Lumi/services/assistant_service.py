# ==========================================
# assistant_service.py
# Cerebro principal de Lumi
# ==========================================

import json
import random

from services.nlp import (
    detect_intent,
    extract_category,
    extract_place_name
)

from services.memory import ConversationMemory

from repositories.place_repository import PlaceRepository

from services.gemini_service import ask_gemini


# ==========================================
# Memoria
# ==========================================

memory = ConversationMemory()


# ==========================================
# Repositorio
# ==========================================

repository = PlaceRepository()


class AssistantService:

    def process_message(self, message):

        # ==========================================
        # 1. Analizar mensaje
        # ==========================================

        intent = detect_intent(message, debug=True)

        category = extract_category(message)

        place_name = extract_place_name(message)

        print(f"""
========================
MENSAJE: {message}
INTENT: {intent}
LUGAR: {place_name}
CATEGORÍA: {category}
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

            return {
                "intent": intent,
                "speech": respuesta
            }


        # ==========================================
        # 4. Buscar lugar específico
        # ==========================================

        place = None

        if place_name:

            place = repository.get_by_name(place_name)

        # ==========================================
        # 5. Usar memoria
        # ==========================================

        if place is None:

            last_place = memory.get_last_place()

            if last_place:

                place = last_place

                context["lugar_memoria"] = last_place["name"]


        # ==========================================
        # 6. Si encontró un lugar
        # ==========================================

        if place:

            memory.remember_place(place)

            context["lugar"] = place


        # ==========================================
        # 7. Buscar por categoría
        # ==========================================

        places = []

        if category:

            places = repository.get_by_category(category)

            if places:

                memory.remember_category(category)

                context["lugares_categoria"] = places


        # ==========================================
        # 8. Recomendación
        # ==========================================

        if intent == "recomendar":

            if places:

                recommended_place = random.choice(places)

                memory.remember_place(recommended_place)

                context["recomendacion"] = recommended_place

            else:

                all_places = repository.get_all()

                if all_places:

                    recommended_place = random.choice(all_places)

                    memory.remember_place(recommended_place)

                    context["recomendacion"] = recommended_place


        # ==========================================
        # 9. Si no hay contexto específico
        # ==========================================

        if not place and not places:

            all_places = repository.get_all()

            context["lugares_disponibles"] = all_places


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

        if place:

            response["place"] = place


        if places:

            response["places"] = places


        if intent == "recomendar" and context.get("recomendacion"):

            response["place"] = context["recomendacion"]


        return response