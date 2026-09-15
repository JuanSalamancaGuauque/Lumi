# ==========================================
# memory.py
# Memoria de conversación de Lumi
# ==========================================

MAX_HISTORY = 5  # cuántos intercambios recientes recordamos por sesión


class ConversationMemory:
    """
    Guarda el estado de UNA conversación (una sesión).
    """

    def __init__(self):
        self.last_place = None
        self.last_category = None
        self.history = []

    def remember_place(self, place):
        self.last_place = place

    def remember_category(self, category):
        self.last_category = category

    def get_last_place(self):
        return self.last_place

    def get_last_category(self):
        return self.last_category

    def add_turn(self, user_message, bot_response):
        self.history.append({
            "usuario": user_message,
            "lumi": bot_response
        })

        # Solo conservamos los últimos MAX_HISTORY intercambios
        self.history = self.history[-MAX_HISTORY:]

    def get_history(self):
        return self.history


# ==========================================
# Memoria por sesión
# ==========================================
# Antes: memory = ConversationMemory() una sola vez para TODOS
# los usuarios de la app (bug crítico).
#
# Ahora: un diccionario {session_id: ConversationMemory()},
# con una memoria independiente por cada conversación.

_sessions = {}


def get_memory(session_id):
    

    if session_id not in _sessions:
        _sessions[session_id] = ConversationMemory()

    return _sessions[session_id]