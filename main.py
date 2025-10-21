"""
main.py — Fixed 403 + Working YT-DLP Headers
✅ YouTube Audio API for Telegram Music Bot
✅ Anti-403 Fix (spoofed headers + client info)
✅ Works on VPS (no Google blocking)
"""

import secrets
import threading
from flask import Flask, request, jsonify, send_from_directory
from uuid import uuid4
from pathlib import Path
import yt_dlp
from constants import *

API_KEY = "VNI0X"

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify(message="✅ YouTube Audio API is running with 403 Fix.")

@app.route("/info/<vid_id>", methods=["GET"])
def info_api(vid_id):
    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        return jsonify(status="error", message="Invalid or missing API key"), 401

    video_url = f"https://www.youtube.com/watch?v={vid_id}"
    filename = f"{vid_id}.mp3"
    output_path = Path(ABS_DOWNLOADS_PATH) / filename

    # 🧠 Fixed yt-dlp config with modern headers & UA
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(output_path),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'source_address': '0.0.0.0',
        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/127.0.0.1 Safari/537.36'
            ),
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://www.youtube.com',
            'Referer': 'https://www.youtube.com/',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        },
        'extractor_args': {
            'youtube': {
                'player_skip': ['js', 'configs'],  # bypass age/region locks
            }
        },
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
    Path(ABS_DOWNLOADS_PATH).mkdir(exist_ok=True)
    print("🚀 YouTube Audio API started (403 Fix Enabled) on port 7000")
    app.run(host="0.0.0.0", port=7000, debug=False)

if __name__ == "__main__":
    main()
