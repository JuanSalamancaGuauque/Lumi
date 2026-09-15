import uuid

from flask import Blueprint, request, jsonify, session

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

    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    response = service.process_message(data["message"], session["session_id"])

    return jsonify(response)