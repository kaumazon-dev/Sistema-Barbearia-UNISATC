from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def verificar_saude():
    return jsonify({"status": "ok"})



