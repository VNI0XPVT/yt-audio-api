"""
main.py
Developed by Alperen Sümeroğlu - YouTube Audio Converter API
Modified & optimized for VPS by ChatGPT (Public Access Enabled + 403 Fix)
"""

import secrets
import threading
from flask import Flask, request, jsonify, send_from_directory
from uuid import uuid4
from pathlib import Path
import yt_dlp
import access_manager
from constants import *

# Initialize the Flask application
app = Flask(__name__)


@app.route("/", methods=["GET"])
def handle_audio_request():
    """
    Main endpoint to receive a YouTube video URL, download the audio in MP3 format,
    and return a unique token for accessing the file later.
    """
    video_url = request.args.get("url")
    if not video_url:
        return jsonify(error="Missing 'url' parameter in request."), BAD_REQUEST

    filename = f"{uuid4()}.mp3"
    output_path = Path(ABS_DOWNLOADS_PATH) / filename

    # yt-dlp configuration with User-Agent and cookies fix
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
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        'geo_bypass': True,
        'source_address': '0.0.0.0'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify(error="Failed to download or convert audio.", detail=str(e)), INTERNAL_SERVER_ERROR

    return _generate_token_response(filename)


@app.route("/download", methods=["GET"])
def download_audio():
    """Serve an audio file associated with a valid token."""
    token = request.args.get("token")
    if not token:
        return jsonify(error="Missing 'token' parameter in request."), BAD_REQUEST

    if not access_manager.has_access(token):
        return jsonify(error="Token is invalid or unknown."), UNAUTHORIZED

    if not access_manager.is_valid(token):
        return jsonify(error="Token has expired."), REQUEST_TIMEOUT

    try:
        filename = access_manager.get_audio_file(token)
        return send_from_directory(ABS_DOWNLOADS_PATH, filename=filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify(error="Requested file not found."), NOT_FOUND


def _generate_token_response(filename: str):
    """Generate a secure download token and return it as JSON."""
    token = secrets.token_urlsafe(TOKEN_LENGTH)
    access_manager.add_token(token, filename)
    return jsonify(token=token)


def main():
    """Start cleanup thread and Flask app."""
    token_cleaner_thread = threading.Thread(target=access_manager.manage_tokens, daemon=True)
    token_cleaner_thread.start()

    # Run the app publicly on port 7000
    app.run(host="0.0.0.0", port=7000, debug=False)


if __name__ == "__main__":
    main()
