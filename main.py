"""
main.py
✅ YouTube Audio API for Telegram Music Bot
✅ Secure API key check
✅ /info/<vid_id> endpoint for YT -> MP3
✅ Compatible with AnonMusic or HerokuBot type bots
"""

import secrets
import threading
from flask import Flask, request, jsonify, send_from_directory
from uuid import uuid4
from pathlib import Path
import yt_dlp
import access_manager
from constants import *

# 🔐 Your static API key
API_KEY = "VNI0X"

# Flask App
app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    """Simple welcome route"""
    return jsonify(message="✅ YouTube Audio API is running successfully.")


@app.route("/info/<vid_id>", methods=["GET"])
def info_api(vid_id):
    """Return downloadable audio URL for a given YouTube video ID"""
    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        return jsonify(status="error", message="Invalid or missing API key"), 401

    video_url = f"https://www.youtube.com/watch?v={vid_id}"
    filename = f"{vid_id}.mp3"
    output_path = Path(ABS_DOWNLOADS_PATH) / filename

    # yt-dlp settings
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(output_path),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
        'quiet': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0',
            'Accept-Language': 'en-US,en;q=0.9'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        audio_url = f"http://80.211.130.162:7000/download?api_key={API_KEY}&token={vid_id}"
        return jsonify(status="success", audio_url=audio_url)
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify(status="error", message=str(e))


@app.route("/download", methods=["GET"])
def download_audio():
    """Serve audio file by token + API key"""
    api_key = request.args.get("api_key")
    if api_key != API_KEY:
        return jsonify(error="Invalid or missing API key."), 401

    token = request.args.get("token")
    if not token:
        return jsonify(error="Missing 'token' parameter in request."), BAD_REQUEST

    try:
        filename = f"{token}.mp3"
        return send_from_directory(ABS_DOWNLOADS_PATH, filename=filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify(error="Requested file not found."), NOT_FOUND


def main():
    """Start Flask app"""
    Path(ABS_DOWNLOADS_PATH).mkdir(exist_ok=True)
    print("✅ YouTube Audio API started on port 7000")
    app.run(host="0.0.0.0", port=7000, debug=False)


if __name__ == "__main__":
    main()
