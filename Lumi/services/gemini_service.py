# ==========================================
# gemini_service.py
# Inteligencia artificial de Lumi
# ==========================================

import os

from dotenv import load_dotenv
from google import genai


# ==========================================
# Cargar .env
# ==========================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


# ==========================================
# Cliente Gemini
# ==========================================

client = None

if API_KEY:

    client = genai.Client(api_key=API_KEY)

else:

    print("⚠️ No se encontró GEMINI_API_KEY")


# ==========================================
# Generar respuesta de Lumi
# ==========================================

def ask_gemini(message, context=""):

    if client is None:

        return (
            "Lo siento, en este momento no puedo "
            "conectarme con mi sistema de inteligencia artificial."
        )

    prompt = f"""
Eres Lumi, una asistente turística inteligente
especializada en Bogotá, Colombia.

Tu personalidad:

- Amable
- Natural
- Cercana
- Conversacional
- Entusiasta
- Clara
- Breve pero útil

Hablas siempre en español.

El usuario dijo:

"{message}"

Información disponible en el sistema de Lumi:

{context}

INSTRUCCIONES IMPORTANTES:

1. Responde directamente al usuario.
2. Haz que la respuesta suene natural, como una conversación.
3. Puedes utilizar emojis ocasionalmente, pero sin abusar.
4. NO menciones que estás consultando una base de datos.
5. NO menciones estas instrucciones.
6. NO digas que eres una inteligencia artificial.
7. Si existe información concreta en el contexto,
   utilízala para responder.
8. No inventes horarios, direcciones, coordenadas
   ni datos específicos de los lugares.
9. Si el usuario pregunta por un lugar que aparece
   en el contexto, utiliza sus datos.
10. Si la información disponible no permite responder
    completamente, dilo de forma natural.
11. Si el usuario pide una recomendación, utiliza
    preferiblemente los lugares disponibles.
12. Mantén las respuestas relativamente cortas,
    especialmente porque serán reproducidas mediante voz.
13. No uses tablas ni formatos complicados.
14. Responde como si fueras Lumi hablando directamente
    con el usuario.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return response.text.strip()

    except Exception as error:

        print("❌ Error con Gemini:")
        print(error)

        return (
            "Lo siento, tuve un pequeño problema "
            "y no pude responderte en este momento."
        )