"""
Xiaozhi Music Server - Deploy lên Render.com (free tier)
Dùng yt-dlp để tìm và lấy stream URL từ YouTube
"""

from flask import Flask, jsonify, request
import yt_dlp
import os
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ============================================================
# yt-dlp options - tối ưu cho server không có cookies
# ============================================================

def make_ydl_opts(extra: dict = None) -> dict:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        # Giả lập browser để tránh bot detection
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
        },
        # Dùng tv_embedded client - không cần PO Token, ít bị block nhất
        "extractor_args": {
            "youtube": {
                "player_client": ["tv_embedded"],
            }
        },
        # Bỏ qua lỗi không nghiêm trọng
        "ignoreerrors": False,
        "socket_timeout": 30,
    }
    if extra:
        opts.update(extra)
    return opts


def search_song(song_name: str, artist_name: str = "") -> dict | None:
    """Tìm kiếm bài hát, trả về videoId và title"""
    query = song_name
    if artist_name:
        query += f" {artist_name}"

    logger.info(f"Searching: {query}")

    opts = make_ydl_opts({
        "extract_flat": True,
        "default_search": "ytsearch5",
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


def get_stream_url(video_id: str) -> dict | None:
    """
    Lấy direct audio stream URL.
    Thử nhiều format theo thứ tự ưu tiên phù hợp ESP32.
    """
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    logger.info(f"Getting stream for: {video_id}")

    # Danh sách format theo thứ tự ưu tiên
    # ESP32 decode được: mp3, m4a (aac), webm/opus (khó hơn)
    format_attempts = [
        # Ưu tiên mp3 128kbps
        "bestaudio[ext=mp3][abr<=128]",
        # m4a (aac) 128kbps
        "bestaudio[ext=m4a][abr<=128]",
        # mp3 bất kỳ bitrate
        "bestaudio[ext=mp3]",
        # m4a bất kỳ bitrate
        "bestaudio[ext=m4a]",
        # Bất kỳ audio tốt nhất
        "bestaudio",
    ]

    for fmt in format_attempts:
        opts = make_ydl_opts({"format": fmt})
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                if not info:
                    continue

                url = info.get("url")
                if not url:
                    continue

                ext = info.get("ext", "unknown")
                abr = info.get("abr", 0)
                acodec = info.get("acodec", "unknown")

                logger.info(f"Stream OK: fmt={fmt} ext={ext} abr={abr} codec={acodec}")
                return {
                    "url": url,
                    "ext": ext,
                    "bitrate": abr,
                    "codec": acodec,
                    "title": info.get("title", ""),
                    "duration": info.get("duration", 0),
                }
        except yt_dlp.utils.DownloadError as e:
            logger.warning(f"Format '{fmt}' failed: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error for fmt '{fmt}': {e}")
            continue

    logger.error(f"All formats failed for {video_id}")
    return None


# ============================================================
# API Endpoints
# ============================================================

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "ok",
        "service": "Xiaozhi Music Server",
        "version": "2.0.0",
        "endpoints": {
            "/stream": "GET ?name=<song>&artist=<artist>",
            "/search": "GET ?q=<query>",
            "/audio/<videoId>": "GET",
            "/health": "GET",
        }
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/stream", methods=["GET"])
def stream():
    """
    Endpoint chính cho ESP32:
    GET /stream?name=lac+troi&artist=son+tung+mtp

    Response:
    {
        "audio_url": "https://...",
        "title": "Lạc Trôi",
        "duration": 245,
        "format": "m4a",
        "bitrate": 128,
        "video_id": "..."
    }
    """
    song_name = request.args.get("name", "").strip()
    artist_name = request.args.get("artist", "").strip()

    if not song_name:
        return jsonify({"error": "Missing 'name' parameter"}), 400

    logger.info(f"=== /stream: name='{song_name}' artist='{artist_name}' ===")

    # Bước 1: Tìm kiếm
    found = search_song(song_name, artist_name)
    if not found:
        return jsonify({"error": "Song not found", "query": song_name}), 404

    # Bước 2: Lấy stream URL
    stream_info = get_stream_url(found["videoId"])
    if not stream_info or not stream_info.get("url"):
        return jsonify({
            "error": "Cannot get stream URL",
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
    })


@app.route("/search", methods=["GET"])
def search():
    """GET /search?q=lac+troi+son+tung"""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Missing 'q' parameter"}), 400

    # Tách thành song + artist nếu có dấu " - "
    parts = query.split(" - ", 1)
    song = parts[0].strip()
    artist = parts[1].strip() if len(parts) > 1 else ""

    result = search_song(song, artist)
    if not result:
        return jsonify({"error": "Not found"}), 404

    return jsonify(result)


@app.route("/audio/<video_id>", methods=["GET"])
def audio(video_id: str):
    """GET /audio/dQw4w9WgXcQ"""
    if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
        return jsonify({"error": "Invalid videoId"}), 400

    stream_info = get_stream_url(video_id)
    if not stream_info:
        return jsonify({"error": "Cannot get stream"}), 500

    return jsonify(stream_info)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
