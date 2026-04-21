"""
Xiaozhi Music Server v3.0 - Deploy lên Render.com (free tier)
Dùng yt-dlp + YouTube cookies để bypass bot detection
"""

from flask import Flask, jsonify, request
import yt_dlp
import os
import logging
import re
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ============================================================
# Cookies - tạo file ngay khi khởi động
# ============================================================
COOKIES_FILE = None

def _init_cookies():
    """Khởi tạo cookies file từ env var khi app start"""
    global COOKIES_FILE
    cookies_content = os.environ.get("YOUTUBE_COOKIES", "")
    if not cookies_content:
        logger.warning("YOUTUBE_COOKIES not set")
        return
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                      delete=False, prefix='yt_cookies_')
    tmp.write(cookies_content)
    tmp.close()
    COOKIES_FILE = tmp.name
    logger.info(f"Cookies initialized: {COOKIES_FILE} ({len(cookies_content)} chars)")

# Khởi tạo ngay khi import
_init_cookies()

def get_cookies_file():
    """Trả về cookies file path, tạo lại nếu cần"""
    global COOKIES_FILE
    if COOKIES_FILE and os.path.exists(COOKIES_FILE):
        return COOKIES_FILE
    # File bị mất (restart) - tạo lại
    _init_cookies()
    return COOKIES_FILE


def make_ydl_opts(extra: dict = None) -> dict:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
        },
        "socket_timeout": 30,
    }

    # Thêm cookies nếu có
    cookies_file = get_cookies_file()
    if cookies_file:
        opts["cookiefile"] = cookies_file

    if extra:
        opts.update(extra)
    return opts


def search_song(song_name: str, artist_name: str = "") -> dict | None:
    query = song_name
    if artist_name:
        query += f" {artist_name}"
    logger.info(f"Searching: {query}")

    opts = make_ydl_opts({
        "extract_flat": True,
        "extractor_args": {"youtube": {"player_client": ["tv_embedded"]}},
    })

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            result = ydl.extract_info(f"ytsearch5:{query}", download=False)
            if not result or "entries" not in result:
                return None
            for entry in result["entries"]:
                if entry and entry.get("duration", 0) > 0:
                    logger.info(f"Found: {entry.get('title')} [{entry.get('id')}]")
                    return {
                        "videoId": entry["id"],
                        "title": entry.get("title", ""),
                        "duration": entry.get("duration", 0),
                    }
    except Exception as e:
        logger.error(f"Search error: {e}")
    return None


def get_stream_url(video_id: str) -> dict:
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    logger.info(f"Getting stream for: {video_id}")

    # Thử các client theo thứ tự
    clients = [["tv_embedded"], ["web_embedded"], ["web"], ["mweb"]]
    fmt = "bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio[ext=webm]/bestaudio"

    last_error = ""
    for client in clients:
        opts = make_ydl_opts({
            "format": fmt,
            "extractor_args": {"youtube": {"player_client": client}},
        })
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                if not info or not info.get("url"):
                    last_error = f"{client}: no URL"
                    continue
                logger.info(f"Stream OK via {client}: ext={info.get('ext')} abr={info.get('abr')}")
                return {
                    "url": info["url"],
                    "ext": info.get("ext", "unknown"),
                    "bitrate": info.get("abr", 0),
                    "codec": info.get("acodec", "unknown"),
                    "title": info.get("title", ""),
                    "duration": info.get("duration", 0),
                    "client": str(client),
                }
        except yt_dlp.utils.DownloadError as e:
            last_error = f"{client}: {str(e)[:300]}"
            logger.warning(f"Client {client} failed: {str(e)[:200]}")
        except Exception as e:
            last_error = f"{client}: {str(e)[:200]}"
            logger.error(f"Unexpected: {e}")

    return {"_error": last_error}


# ============================================================
# Endpoints
# ============================================================

@app.route("/", methods=["GET"])
def index():
    has_cookies = bool(os.environ.get("YOUTUBE_COOKIES"))
    return jsonify({
        "status": "ok",
        "service": "Xiaozhi Music Server",
        "version": "3.0.0",
        "cookies_configured": has_cookies,
        "endpoints": {
            "/stream": "GET ?name=<song>&artist=<artist>",
            "/search": "GET ?q=<query>",
            "/audio/<videoId>": "GET",
            "/health": "GET",
        }
    })


@app.route("/health", methods=["GET"])
def health():
    cookies_content = os.environ.get("YOUTUBE_COOKIES", "")
    return jsonify({
        "status": "ok",
        "cookies_env_length": len(cookies_content),
        "cookies_file": COOKIES_FILE,
        "cookies_file_exists": bool(COOKIES_FILE and os.path.exists(COOKIES_FILE)),
    })


@app.route("/stream", methods=["GET"])
def stream():
    song_name = request.args.get("name", "").strip()
    artist_name = request.args.get("artist", "").strip()

    if not song_name:
        return jsonify({"error": "Missing 'name' parameter"}), 400

    logger.info(f"=== /stream: name='{song_name}' artist='{artist_name}' ===")

    found = search_song(song_name, artist_name)
    if not found:
        return jsonify({"error": "Song not found", "query": song_name}), 404

    stream_info = get_stream_url(found["videoId"])
    if stream_info.get("_error"):
        return jsonify({
            "error": "Cannot get stream URL",
            "detail": stream_info["_error"],
            "videoId": found["videoId"],
            "title": found.get("title"),
        }), 500

    return jsonify({
        "audio_url": stream_info["url"],
        "title": stream_info.get("title") or found.get("title"),
        "duration": stream_info.get("duration") or found.get("duration"),
        "format": stream_info.get("ext", "unknown"),
        "bitrate": stream_info.get("bitrate", 0),
        "video_id": found["videoId"],
        "client": stream_info.get("client"),
    })


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Missing 'q' parameter"}), 400
    parts = query.split(" - ", 1)
    result = search_song(parts[0].strip(), parts[1].strip() if len(parts) > 1 else "")
    if not result:
        return jsonify({"error": "Not found"}), 404
    return jsonify(result)


@app.route("/audio/<video_id>", methods=["GET"])
def audio(video_id: str):
    if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
        return jsonify({"error": "Invalid videoId"}), 400
    stream_info = get_stream_url(video_id)
    if stream_info.get("_error"):
        return jsonify({"error": "Cannot get stream", "detail": stream_info["_error"]}), 500
    return jsonify(stream_info)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
