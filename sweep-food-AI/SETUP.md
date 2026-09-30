# 🥗 SweepFood AI — Hướng Dẫn Khởi Động Web Mockup & Host OCR Ra ngrok

Tài liệu này hướng dẫn chi tiết cách:
1. **Khởi động Web Mockup Server** trên máy cục bộ (`http://127.0.0.1:8000`).
2. **Host toàn bộ Web Mockup & Smart Input OCR/ASR API ra internet công khai qua ngrok** để kiểm thử từ điện thoại di động hoặc tích hợp frontend bên ngoài.
3. **Kiểm thử API OCR** bằng ảnh mẫu hóa đơn siêu thị / tem cân thực phẩm.

---

## 📌 1. Yêu Cầu Môi Trường

Hệ thống sử dụng môi trường Conda `ocr_env` đã cài đặt đầy đủ:
- **FastAPI** + **Uvicorn** (Web Server).
- **PyTorch** + **PaddleOCR** + **VietOCR** (Smart Input OCR hỗ trợ GPU CUDA).
- **XGBoost** + **LightGBM** (Mô hình gợi ý thực đơn Learning-to-Rank).
- **pyngrok** + **ngrok v3** (Quản lý đường hầm HTTPS công khai).

Đường dẫn Python thực thi:
```
C:\Users\HUYPNG\miniconda3\envs\ocr_env\python.exe
```

---

## 🚀 2. Bật Web Mockup Server (Local)

Web Server chạy trên cổng `8000`, cung cấp cả giao diện người dùng Web Mockup và toàn bộ các API.

### Cách 1: Click đúp tệp Batch (Nhanh nhất)
* Click đúp vào tệp **`run_web.bat`** tại thư mục gốc của dự án.

### Cách 2: Chạy bằng dòng lệnh Terminal
Mở PowerShell hoặc Command Prompt tại thư mục dự án:
```powershell
# Cách kích hoạt qua conda:
conda activate ocr_env
python -m uvicorn web.app:app --host 127.0.0.1 --port 8000 --reload

# Hoặc gọi trực tiếp binary python:
"C:\Users\HUYPNG\miniconda3\envs\ocr_env\python.exe" -m uvicorn web.app:app --host 127.0.0.1 --port 8000 --reload
```

Khi màn hình xuất hiện:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```
$\rightarrow$ Mở trình duyệt truy cập: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.

---

## 🌐 3. Host Web Mockup & OCR API ra ngrok (Công khai Internet)

### Bước 3.1: Lấy ngrok authtoken (Miễn phí 100%, chỉ làm 1 lần)
Ngrok yêu cầu tài khoản miễn phí để mở cổng:
1. Đăng ký/đăng nhập miễn phí tại: **[https://dashboard.ngrok.com/signup](https://dashboard.ngrok.com/signup)**
2. Lấy mã token của bạn tại: **[https://dashboard.ngrok.com/get-started/your-authtoken](https://dashboard.ngrok.com/get-started/your-authtoken)** (Dạng: `2sXXXXXXXX_YYYYYYYYYYY`).
3. Lưu token vào file `.env` tại thư mục dự án:
   ```env
   NGROK_AUTHTOKEN="mã_token_của_bạn_ở_đây"
   ```
   *Hoặc chạy lệnh cấu hình 1 lần:*
   ```powershell
   "C:\Users\HUYPNG\miniconda3\envs\ocr_env\Scripts\ngrok.exe" config add-authtoken mã_token_của_bạn
   ```

---

### Bước 3.2: Bật ngrok Tunnel

> **Lưu ý:** Đảm bảo Web Server ở Bước 2 đang chạy trước khi bật ngrok.

#### Cách 1: Click đúp tệp Batch
* Click đúp vào tệp **`run_ngrok.bat`** tại thư mục gốc của dự án.

#### Cách 2: Chạy script Python điều phối
```powershell
"C:\Users\HUYPNG\miniconda3\envs\ocr_env\python.exe" scripts/host_ngrok.py
```

Khi tunnel online, terminal sẽ hiển thị bảng URL công khai:
```
======================================================================
   🎉 NGROK TUNNEL ONLINE! CÁC ENDPOINT CÔNG KHAI:
======================================================================
  🌐 Web Mockup UI         : https://xxxx-xx-xx-xx.ngrok-free.app/
  🧾 Smart Input OCR API   : https://xxxx-xx-xx-xx.ngrok-free.app/api/smart-input/ocr-upload
  🎙️ Smart Input ASR API   : https://xxxx-xx-xx-xx.ngrok-free.app/api/smart-input/asr-upload
  🥗 Recommendation API    : https://xxxx-xx-xx-xx.ngrok-free.app/api/recommend
  ⚡ System & GPU Status   : https://xxxx-xx-xx-xx.ngrok-free.app/api/system/status
======================================================================
```

Bây giờ bạn có thể:
- Mở đường link `https://xxxx.ngrok-free.app/` từ điện thoại di động hoặc bất kỳ máy tính nào có internet.
- Dùng đường link này cho Mobile App Flutter/React Native hoặc Frontend bên ngoài gọi vào OCR Backend.

---

## 🧪 4. Hướng Dẫn Test Thử OCR

### Test qua Giao diện Web Mockup
1. Mở link Web Mockup (local hoặc ngrok).
2. Tìm khối **Smart Input OCR**.
3. Bấm **Chọn ảnh hóa đơn / Tem cân** (hoặc chọn tệp mẫu có sẵn `scratch/hoadon.webp`).
4. Hệ thống VietOCR + PaddleOCR chạy trên GPU CUDA sẽ nhận diện văn bản, chuẩn hóa tên thực phẩm Việt Nam và đưa thẳng vào danh sách tủ lạnh.

### Test qua cURL (Terminal / Postman)
Gửi ảnh trực tiếp qua API:
```bash
# Test local:
curl -X POST "http://127.0.0.1:8000/api/smart-input/ocr-upload" -F "file=@scratch/hoadon.webp"

# Test qua ngrok công khai:
curl -X POST "https://xxxx.ngrok-free.app/api/smart-input/ocr-upload" -F "file=@scratch/hoadon.webp"
```

**Ví dụ JSON trả về từ OCR API:**
```json
{
  "detected_items": [
    {
      "raw_line": "Ba rọi heo C.P 500g",
      "extracted_name": "ba rọi heo",
      "quantity": 0.5,
      "unit": "kg",
      "confidence": 0.96
    }
  ],
  "latency_ms": 280.5,
  "device": "cuda"
}
```

---

## 📡 5. Danh Sách Endpoints API Đầy Đủ

| Phương thức | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/` | Giao diện Web Mockup SweepFood (HTML + Tailwind CSS) |
| `POST` | `/api/smart-input/ocr-upload` | Nhận file ảnh hóa đơn (`multipart/form-data`) $\rightarrow$ trả về danh sách nguyên liệu |
| `POST` | `/api/smart-input/ocr` | Nhận ảnh hóa đơn dạng Base64 JSON |
| `POST` | `/api/smart-input/asr-upload` | Nhận file âm thanh giọng nói (`.wav`, `.m4a`) $\rightarrow$ trích xuất nguyên liệu |
| `POST` | `/api/recommend` | Gợi ý thực đơn LTR thông minh dựa trên tủ lạnh, giờ hết hạn và số người ăn |
| `GET` | `/api/system/status` | Kiểm tra trạng thái GPU CUDA, VRAM và các mô hình đang nạp |
| `GET` | `/api/autocomplete` | Tự động hoàn thiện tên nguyên liệu tiếng Việt theo từ điển Viện Dinh Dưỡng |
