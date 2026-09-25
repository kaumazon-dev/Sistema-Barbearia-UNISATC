from flask import Blueprint, jsonify


blueprint_health = Blueprint("health", __name__)

@blueprint_health.route("/health", methods=["GET"])
def verificar_saude():
    return jsonify({"status": "ok"})
