 # Hướng dẫn lấy YouTube Cookies cho Render

## Tại sao cần cookies?
Render.com dùng IP datacenter, YouTube nhận ra và yêu cầu đăng nhập.
Cookies từ browser của bạn giúp server "giả vờ" là bạn đang dùng.

## Bước 1: Cài extension lấy cookies

Dùng một trong hai:
- **Chrome**: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
- **Firefox**: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

## Bước 2: Lấy cookies từ YouTube

1. Mở Chrome/Firefox, vào **youtube.com**
2. **Đăng nhập** vào tài khoản Google (quan trọng!)
3. Click vào extension → chọn **"Export cookies for this tab"**
4. Lưu file `cookies.txt`

## Bước 3: Upload lên Render

1. Mở file `cookies.txt` bằng Notepad
2. Copy toàn bộ nội dung (Ctrl+A → Ctrl+C)
3. Vào **Render Dashboard** → service `robot-music-api`
4. Tab **Environment** → **Add Environment Variable**
5. Key: `YOUTUBE_COOKIES`
6. Value: Paste nội dung file cookies (Ctrl+V)
7. Nhấn **Save Changes** → Render tự restart

## Bước 4: Kiểm tra

```
https://robot-music-api.onrender.com/
```
Phải thấy: `"cookies_configured": true`

## Lưu ý
- Cookies hết hạn sau ~1-2 tuần, cần lấy lại
- Không chia sẻ cookies với người khác (chứa thông tin đăng nhập)
- Dùng tài khoản Google phụ nếu lo ngại bảo mật
