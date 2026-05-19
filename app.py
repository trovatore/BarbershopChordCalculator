from flask import Flask, render_template, request, jsonify, send_from_directory
from engine.analyzer import ChordAnalyzer
import os

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/tests/js")
def js_tests():
    return render_template("js-tests.html")


@app.route("/help")
def help():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_dir, "README.md"), "r", encoding="utf-8") as f:
            content = f.read()
        return render_template("readme.html", content=content)
    except FileNotFoundError:
        return "Documentation (README.md) not found in root directory.", 404


@app.route("/images/<path:filename>")
def serve_images(filename):
    """Explicitly serve images from the root images directory."""
    return send_from_directory("images", filename)


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
    app.run(host="0.0.0.0", port=port)