from flask import Blueprint, request, jsonify

from services.assistant_service import AssistantService

assistant = Blueprint("assistant", __name__)

service = AssistantService()


@assistant.route("/assistant", methods=["POST"])
def chat():

    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({
            "error": "No se recibió ningún mensaje."
        }), 400

    response = service.process_message(data["message"])

    return jsonify(response)