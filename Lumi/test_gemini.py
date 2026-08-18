from services.gemini_service import ask_gemini


respuesta = ask_gemini(
    "¿Qué puedo visitar en Bogotá?"
)

print()
print("LUMI:")
print(respuesta)