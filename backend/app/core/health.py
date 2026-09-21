from flask import Blueprint
from flask import jsonify

blueprint_health = Blueprint("health", __name__, url_prefix="/health")

@blueprint_health.route("/", methods=["GET"])
def verificar_saude():
    return jsonify({"status": "ok"})