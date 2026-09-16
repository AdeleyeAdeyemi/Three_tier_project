from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "backend"
    })


@app.route("/api/platform")
def platform():
    return jsonify({
        "timestamp": "2026-09-16 12:00",
        "title": "Platform is running",
        "messages": [
            "Application started successfully"
        ],
        "errors": []
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
