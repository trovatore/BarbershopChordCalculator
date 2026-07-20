from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_from_directory,
    Response,
)
from engine.analyzer import ChordAnalyzer
from engine.wav_chord_detector import detect_chord
import io
import os
from typing import Union, Tuple, List, Any

app = Flask(__name__)

# Kotlin/JS browser bundle built by `./gradlew jsBrowserDevelopmentWebpack` in engine-kt/
# (plan.md §5.6/§5.7). Not committed — engine-kt/build/ is gitignored build output — so /score
# 404s on the JS request until that Gradle task has been run at least once locally.
ENGINE_JS_DIR = os.path.join(
    "engine-kt", "build", "kotlin-webpack", "js", "productionExecutable"
)


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/score/")
def score() -> str:
    return render_template("score.html")


@app.route("/engine/barbershop-engine.js")
def serve_engine_js() -> Response:
    return send_from_directory(
        ENGINE_JS_DIR, "barbershop-engine.js", mimetype="application/javascript"
    )


@app.route("/tests/js")
def js_tests() -> str:
    return render_template("js-tests.html")


@app.route("/help/")
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
        tuning_style: str = data.get("tuning_style", "just") if data else "just"
        result = ChordAnalyzer(notes, allow_rootless_ninths=allow_rootless).analyze(
            tuning_style=tuning_style
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/analysis/")
def spectral_analysis() -> str:
    return render_template("analysis.html")


@app.route("/detect-chord-wav", methods=["POST"])
def detect_chord_wav() -> Union[Response, Tuple[Response, int]]:
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400
    try:
        result = detect_chord(io.BytesIO(request.files["file"].read()))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/sw.js")
def serve_sw() -> Response:
    return send_from_directory("static/js", "sw.js", mimetype="application/javascript")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
