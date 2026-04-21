"""
Test endpoint - kiểm tra yt-dlp hoạt động trên Vercel không
"""
from http.server import BaseHTTPRequestHandler
import json
import subprocess
import sys

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        result = {"status": "testing"}
        
        try:
            # Test yt-dlp với tv_embedded client
            import yt_dlp
            
            opts = {
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "format": "bestaudio[ext=m4a]/bestaudio",
                "extractor_args": {
                    "youtube": {"player_client": ["tv_embedded"]}
                },
                "socket_timeout": 20,
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(
                    "https://www.youtube.com/watch?v=Llw9Q6akRo4",
                    download=False
                )
                if info and info.get("url"):
                    result = {
                        "status": "OK",
                        "ext": info.get("ext"),
                        "abr": info.get("abr"),
                        "url_length": len(info.get("url", "")),
                        "client": "tv_embedded"
                    }
                else:
                    result = {"status": "no_url"}
                    
        except Exception as e:
            result = {"status": "error", "detail": str(e)[:300]}
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
