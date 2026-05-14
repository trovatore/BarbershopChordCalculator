from flask import Flask, render_template, request, jsonify
from engine.analyzer import ChordAnalyzer
import os

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        notes = request.json.get("notes", [])
        result = ChordAnalyzer(notes).analyze()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
