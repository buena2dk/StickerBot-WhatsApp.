
import os
from flask import Flask, request
from pathlib import Path

app = Flask(__name__)

# Carpeta temporal para los vídeos recibidos
VIDEO_FOLDER = Path("/tmp/videos")
VIDEO_FOLDER.mkdir(parents=True, exist_ok=True)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "")


@app.route("/", methods=["GET"])
def home():
    return "StickerBot WhatsApp está funcionando."


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN and VERIFY_TOKEN:
        return challenge or "", 200

    return "Verificación rechazada", 403


@app.route("/webhook", methods=["POST"])
def receive_webhook():
    data = request.get_json(silent=True)

    if data is None:
        return "Solicitud inválida", 400

    print("Evento de WhatsApp recibido.")

    # Más adelante añadiremos aquí:
    # 1. Detectar vídeos recibidos.
    # 2. Detectar el comando !sticker.
    # 3. Procesar el vídeo con FFmpeg.
    # 4. Enviar el sticker resultante.

    return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
