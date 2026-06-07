from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_from_directory,
    Response,
)
from engine.analyzer import ChordAnalyzer
import os
from typing import Union, Tuple, List, Any

app = Flask(__name__)


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/tests/js")
def js_tests() -> str:
    return render_template("js-tests.html")


@app.route("/help")
def help() -> Union[str, Tuple[str, int]]:
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_dir, "README.md"), "r", encoding="utf-8") as f:
            content = f.read()
        return render_template("readme.html", content=content)
    except FileNotFoundError:
        return "Documentation (README.md) not found in root directory.", 404


@app.route("/images/<path:filename>")
def serve_images(filename: str) -> Response:
    """Explicitly serve images from the root images directory."""
    return send_from_directory("images", filename)


@app.route("/analyze", methods=["POST"])
def analyze() -> Union[Response, Tuple[Response, int]]:
    try:
        data: Any = request.json
        notes: List[str] = data.get("notes", []) if data else []
        allow_rootless: bool = data.get("allow_rootless", False) if data else False
        result = ChordAnalyzer(notes, allow_rootless_ninths=allow_rootless).analyze()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/analysis")
def spectral_analysis() -> str:
    return render_template("analysis.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
