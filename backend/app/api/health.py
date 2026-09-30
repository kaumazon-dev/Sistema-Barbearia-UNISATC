from flask import Blueprint, current_app, jsonify
from sqlalchemy import text
from app.extensions import db


blueprint_health = Blueprint("health", __name__)

@blueprint_health.route("/health", methods=["GET"])
def verificar_saude():
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Health check: banco indisponível")
        return jsonify({"status": "erro", "banco": "indisponivel"}), 503
    return jsonify({"status": "ok", "banco": "ok"})
