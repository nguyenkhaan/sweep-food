# 🥗 SweepFood AI — Hướng Dẫn Khởi Động Web Mockup & Host OCR Ra ngrok

Chi tiết đầy đủ xem tại file [SETUP.md](SETUP.md).

Tóm tắt nhanh:
1. Bật Web Server: Click đúp `run_web.bat` (hoặc chạy `"C:\Users\HUYPNG\miniconda3\envs\ocr_env\python.exe" -m uvicorn web.app:app --host 127.0.0.1 --port 8000`).
2. Điền authtoken ngrok vào `.env`: `NGROK_AUTHTOKEN="your_token"` (lấy miễn phí tại https://dashboard.ngrok.com/get-started/your-authtoken).
3. Bật ngrok tunnel: Click đúp `run_ngrok.bat` (hoặc chạy `"C:\Users\HUYPNG\miniconda3\envs\ocr_env\python.exe" scripts/host_ngrok.py`).
4. Đường link công khai sẽ hiển thị trên màn hình:
   - Web Mockup: `https://xxxx.ngrok-free.app/`
   - OCR Upload API: `https://xxxx.ngrok-free.app/api/smart-input/ocr-upload`
