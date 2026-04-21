# Xiaozhi Music Server

Server Python dùng `yt-dlp` để tìm và lấy stream nhạc từ YouTube.  
Deploy miễn phí lên **Render.com** hoặc **Vercel**.

## API

| Endpoint | Mô tả |
|----------|-------|
| `GET /stream?name=<bài hát>&artist=<ca sĩ>` | Tìm và trả về stream URL (dùng cho ESP32) |
| `GET /search?q=<query>` | Chỉ tìm kiếm |
| `GET /audio/<videoId>` | Lấy stream từ videoId |
| `GET /health` | Health check |

## Deploy lên Render.com (Khuyến nghị)

1. Tạo tài khoản tại [render.com](https://render.com)
2. New → Web Service → Connect GitHub repo
3. Chọn thư mục `music-server/`
4. Render tự đọc `render.yaml` và deploy
5. Sau deploy, bạn nhận được URL dạng: `https://xiaozhi-music-server.onrender.com`

## Deploy lên Vercel

```bash
cd music-server
npm i -g vercel
vercel --prod
```

## Test

```bash
# Tìm bài hát
curl "https://your-server.onrender.com/stream?name=lac+troi&artist=son+tung+mtp"

# Kết quả:
# {
#   "audio_url": "https://...",
#   "title": "Lạc Trôi",
#   "duration": 245,
#   "format": "m4a",
#   "bitrate": 128
# }
```

## Cấu hình ESP32

Sau khi deploy, sửa file `esp32_music.cc`:

```cpp
// Thay YOUR_SERVER_URL bằng URL thực của bạn
static const std::string MUSIC_SERVER_URL = "https://xiaozhi-music-server.onrender.com";
```
