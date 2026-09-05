from Flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/health', methods='GET')
def healthcheck():
    return jsonify({"status": "healthy"})

