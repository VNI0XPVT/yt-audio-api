from flask import Flask, request, jsonify
import yt_dlp
import subprocess, json, os

app = Flask(__name__)

API_KEY = "VNI0X"

def get_video_info(video_id):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"

        # First try normal yt-dlp extraction
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'dump_single_json': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "status": "ok",
                "title": info.get("title"),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail"),
                "uploader": info.get("uploader"),
                "url": info.get("webpage_url"),
            }

    except Exception as e:
        # Fallback: use youtubei extractor (for latest YT changes)
        try:
            cmd = [
                "yt-dlp", "-J", "--extractor-args", "youtube:player_client=android",
                f"https://www.youtube.com/watch?v={video_id}"
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            data = json.loads(result.stdout)
            return {
                "status": "ok",
                "title": data.get("title"),
                "duration": data.get("duration"),
                "thumbnail": data.get("thumbnail"),
                "uploader": data.get("uploader"),
                "url": data.get("webpage_url"),
            }
        except Exception as e2:
            return {"status": "error", "message": str(e2)}

@app.route("/info/<video_id>", methods=["GET"])
def info(video_id):
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        return jsonify({"status": "error", "message": "Invalid API key"}), 401

    info = get_video_info(video_id)
    return jsonify(info)

if __name__ == "__main__":
    print("🚀 YouTube Audio API started (Patched Version) on port 7000")
    app.run(host="0.0.0.0", port=7000)
