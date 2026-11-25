
import os
import shutil
import logging
from pathlib import Path
from flask import Flask, request

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StickerBot")

VIDEO_FOLDER = Path("/tmp/videos")
VIDEO_FOLDER.mkdir(parents=True, exist_ok=True)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "")

# Registro temporal de vídeos recibidos.
# Más adelante lo cambiaremos por almacenamiento persistente.
received_videos = {}


@app.route("/", methods=["GET"])
def home():
    return "StickerBot WhatsApp esta funcionando."


@app.route("/ffmpeg-check", methods=["GET"])
def ffmpeg_check():
    ffmpeg = shutil.which("ffmpeg")

    if not ffmpeg:
        return "FFmpeg no esta disponible.", 500

    return "FFmpeg funciona correctamente."


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN and VERIFY_TOKEN:
        logger.info("Webhook verificado correctamente.")
        return challenge or "", 200

    return "Verificacion rechazada", 403


@app.route("/webhook", methods=["POST"])
def receive_webhook():
    data = request.get_json(silent=True)

    if not data:
        return "Solicitud invalida", 400

    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                for message in value.get("messages", []):
                    message_id = message.get("id")
                    message_type = message.get("type")
                    sender = message.get("from", "")

                    # Detectar vídeos recibidos
                    if message_type == "video":
                        video = message.get("video", {})
                        media_id = video.get("id")

                        if message_id and media_id:
                            received_videos[message_id] = {
                                "media_id": media_id,
                                "sender": sender,
                                "mime_type": video.get("mime_type")
                            }

                            logger.info(
                                "Video recibido. ID: %s",
                                message_id
                            )

                    # Detectar el comando enviado como respuesta
                    elif message_type == "text":
                        text = message.get("text", {}).get("body", "")
                        context = message.get("context", {})
                        quoted_id = context.get("id")

                        if text.strip().lower() == "!sticker":
                            if quoted_id in received_videos:
                                logger.info(
                                    "Comando !sticker detectado "
                                    "para el video: %s",
                                    quoted_id
                                )
                            else:
                                logger.info(
                                    "Comando recibido, pero no "
                                    "se encontro el video citado."
                                )

        logger.info("Webhook procesado correctamente.")
        return "EVENT_RECEIVED", 200

    except Exception:
        logger.exception("Error procesando el webhook.")
        return "EVENT_RECEIVED", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
           
