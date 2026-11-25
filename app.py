
import os
import shutil
import subprocess
from pathlib import Path
from flask import Flask, request

app = Flask(__name__)

VIDEO_FOLDER = Path("/tmp/videos")
VIDEO_FOLDER.mkdir(parents=True, exist_ok=True)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "")


@app.route("/", methods=["GET"])
def home():
    return "StickerBot WhatsApp esta funcionando."


@app.route("/ffmpeg-check", methods=["GET"])
def ffmpeg_check():
    ffmpeg_path = shutil.which("ffmpeg")

    if not ffmpeg_path:
        return "FFmpeg NO esta instalado o no esta disponible.", 500

    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            version = result.stdout.splitlines()[0]
            return f"FFmpeg funciona correctamente. {version}"

        return "FFmpeg fue encontrado, pero no pudo ejecutarse.", 500

    except Exception as error:
        return f"Error comprobando FFmpeg: {error}", 500


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN and VERIFY_TOKEN:
        return challenge or "", 200

    return "Verificacion rechazada", 403


@app.route("/webhook", methods=["POST"])
def receive_webhook():
    data = request.get_json(silent=True)

    if data is None:
        return "Solicitud invalida", 400

    print("Evento de WhatsApp recibido.")
    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
            
