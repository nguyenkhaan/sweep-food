Type help for instructions on how to use fish
cloud@cloud ~/w/p/m/sweep-food (dev)> cd sweep-food-AI/
cloud@cloud ~/w/p/m/s/sweep-food-AI (dev)> conda activate ocr_env

EnvironmentNameNotFound: Could not find conda environment: ocr_env
You can list all discoverable environments with `conda info --envs`

# 🥗 SweepFood AI — Hướng Dẫn Cài Đặt & Khởi Động Web Application

Tài liệu này hướng dẫn chi tiết cách thiết lập môi trường và khởi động ứng dụng Web **SweepFood AI** (giao diện hiện đại xây dựng trên nền tảng **FastAPI**, **Tailwind CSS v4**, mô hình xếp hạng **XGBoost Ranker LTR** và bộ nhập liệu đa phương thức **Smart Input OCR/ASR**).

---

## 📌 1. Yêu Cầu Hệ Thống & Môi Trường

- **Hệ điều hành:** Windows 10/11, Linux hoặc macOS.
- **Python:** Khuyến nghị Python 3.10.
- **Môi trường Conda:** Đã cài đặt môi trường `ocr_env` (hoặc môi trường chứa các thư viện PyTorch, XGBoost, FastAPI, OpenCV, VietOCR, Uvicorn).
- **Phần cứng GPU (Tùy chọn nhưng khuyến nghị):**
  - Card đồ họa rời hỗ trợ NVIDIA CUDA (ví dụ: NVIDIA GeForce RTX 3050/4060 trở lên, CUDA 12.x).
  - *Lưu ý:* Nếu máy tính không có GPU rời, hệ thống sẽ tự động chuyển sang chế độ **CPU Fallback** an toàn và tiếp tục hoạt động bình thường.
- **Xử lý âm thanh (FFmpeg):** Đã tích hợp sẵn qua `imageio-ffmpeg` hoặc binary FFmpeg trong hệ thống để phục vụ luồng nén 16kHz mono FLAC cho ASR.

---

## 🚀 2. Các Bước Khởi Động Web Server

### Bước 1: Mở Terminal (PowerShell hoặc Command Prompt)

Mở cửa sổ dòng lệnh tại thư mục gốc của dự án:

```powershell
cd g:\github\sweep-food-AI
```

### Bước 2: Kích hoạt môi trường Conda

Kích hoạt môi trường `ocr_env`:

```powershell
conda activate ocr_env
```

*(Nếu dùng Linux/WSL: `source activate ocr_env` hoặc `conda activate ocr_env`)*

### Bước 3: Khởi động Web Server với Uvicorn

Chạy server bằng một trong hai cách sau:

#### Cách 1: Khởi động qua Uvicorn CLI (Khuyến nghị cho Development / Production)

```powershell
python -m uvicorn web.app:app --host 127.0.0.1 --port 8000
```

> **Mẹo:** Khi đang phát triển và chỉnh sửa mã nguồn, bạn có thể thêm cờ `--reload`:
>
> ```powershell
> python -m uvicorn web.app:app --host 127.0.0.1 --port 8000 --reload
> ```

#### Cách 2: Khởi động trực tiếp file Python

```powershell
python web/app.py
```

---

## 🖥️ 3. Truy Cập Ứng Dụng

Khi server khởi động thành công, màn hình terminal sẽ hiển thị thông báo:

```text
============================================================
 SweepFood AI — Initializing GPU Hardware Acceleration...
============================================================
[GPU] XGBoost Ranker successfully loaded on CUDA (NVIDIA GeForce RTX 4060 Laptop GPU)
[GPU] Smart Input OCR: PaddleOCR+VietOCR (CUDA) (Allocated VRAM: 145.68 MB)
============================================================
 All models active in GPU VRAM. Zero cold-start latency achieved!

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Mở trình duyệt web bất kỳ (Chrome, Edge, Brave, Firefox) và truy cập đường dẫn:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)** hoặc **[http://localhost:8000](http://localhost:8000)**

---

## ⚡ 4. Tính Năng & Cơ Chế Khởi Động Sẵn GPU (GPU Warm-Up)

1. **Khởi động sẵn GPU (Zero Cold-Start):**
   - Ngay trong sự kiện khởi động server (`@app.on_event("startup")`), hệ thống tự động:
     - Nạp mô hình **XGBoost Ranker** lên CUDA và chạy suy luận giả định để biên dịch kernel.
     - Khởi tạo kiến trúc VGG-Transformer của **VietOCR** lên thiết bị `cuda:0` và khóa sẵn **~162 MB VRAM**.
     - Giúp toàn bộ các request OCR và gợi ý món ăn đầu tiên của người dùng phản hồi ngay tức thì (dưới 5ms cho gợi ý món, không bị trễ 2-3 giây khởi tạo CUDA).
2. **Kiểm tra trạng thái hệ thống thời gian thực:**
   - Bạn có thể kiểm tra trạng thái GPU và bộ nhớ VRAM bất kỳ lúc nào qua endpoint:
     ```bash
     curl http://127.0.0.1:8000/api/system/status
     ```
   - Phản hồi JSON mẫu:
     ```json
     {
       "cuda_available": true,
       "device_name": "NVIDIA GeForce RTX 4060 Laptop GPU",
       "xgb_device": "cuda",
       "ocr_device": "PaddleOCR+VietOCR (CUDA)",
       "vram_allocated_mb": 0.0,
       "warmed_up": true,
       "vram_reserved_mb": 162.0
     }
     ```

---

## 📱 5. Hướng Dẫn Sử Dụng Các Phân Hệ Trên Giao Diện

### 🍽️ Tab 1: Gợi Ý Thực Đơn Thông Minh (Recommendation)

- Nhập nguyên liệu có sẵn trong tủ lạnh (hỗ trợ gợi ý tự động Autocomplete theo Viện Dinh Dưỡng Quốc Gia VDD).
- Điền khối lượng (gram) và thời gian bảo quản còn lại (giờ).
- Điều chỉnh số người ăn và thời gian nấu tối đa bằng thanh trượt.
- Nhấn **"Gợi Ý Thực Đơn Thông Minh"** để nhận Top món ăn được tối ưu theo mô hình toán học *Continuous Quantity Elasticity* và xếp hạng bởi *XGBoost Ranker*.
- Nhấn vào từng món để xem chi tiết hướng dẫn nấu từng bước, tỷ lệ dinh dưỡng (Calo, Đạm, Béo, Tinh bột) và liên kết công thức gốc.

### 📸 Tab 2: Quét Hóa Đơn & Nhãn Mác (Smart OCR)

- **Chế độ Tải ảnh:** Tải hóa đơn siêu thị (WinMart, Bách Hóa Xanh, Co.opmart...) hoặc ảnh chụp nhãn dán khay thực phẩm (VietGAP, Thịt heo CP Chilled...).
  - *Tối ưu:* Trình duyệt tự động nén kích thước ảnh xuống tối đa 1600px trước khi gửi (tiết kiệm >90% dung lượng mạng). Server áp dụng thuật toán tăng tương phản cục bộ CLAHE để làm rõ chữ mờ trên hóa đơn in nhiệt.
- **Chế độ Camera:** Bật webcam/camera điện thoại để chụp trực tiếp. Frame ảnh tự động nén nhẹ và gửi đến pipeline nhận diện.
- Nhấn **"Thêm Thực Phẩm Vào Tủ Lạnh"** để tự động chuyển toàn bộ nguyên liệu vừa nhận diện sang kho tủ lạnh.

### 🎙️ Tab 3: Nhập Liệu Bằng Giọng Nói (Smart ASR)

- **Tùy chọn Engine:**
  - `⚡ Groq Whisper Turbo`: Nhận diện siêu tốc đám mây qua mô hình `whisper-large-v3-turbo` (<500ms phản hồi).
  - `🚀 Gipformer Local`: Nhận diện cục bộ qua mô hình nén Gipformer 16kHz FLAC.
- **Cách nhập:** Bấm vào nút micro để nói (ví dụ: *"Tủ lạnh có nửa con gà tầm bảy trăm gam và một mớ rau muống"*) hoặc tải file ghi âm lên.
- Hệ thống tự động cắt khoảng lặng chết, nén FLAC 16kHz mono (giảm 93.4% dung lượng) và bóc tách thực thể khẩu ngữ tiếng Việt, quy đổi chính xác ra gram.

---

## 🛠️ 6. Xử Lý Sự Cố Thường Gặp (Troubleshooting)

### Lỗi 1: Cổng 8000 đã bị chiếm dụng (`Address already in use` hoặc `WinError 10048`)

Nếu trước đó có một tiến trình web server đang chạy ngầm:

- **Trên Windows PowerShell:**
  ```powershell
  # Tìm PID đang chiếm cổng 8000
  netstat -ano | findstr :8000
  # Tắt tiến trình (thay <PID> bằng mã số thực tế)
  taskkill /PID <PID> /F
  ```
- **Hoặc đổi sang cổng khác khi khởi động:**
  ```powershell
  python -m uvicorn web.app:app --host 127.0.0.1 --port 8080
  ```

### Lỗi 2: Trình duyệt không mở được Camera / Microphone

- Đảm bảo bạn đang truy cập bằng địa chỉ `http://127.0.0.1:8000` hoặc `http://localhost:8000` (trình duyệt chỉ cho phép truy cập thiết bị truyền thông trên giao thức an toàn `https` hoặc miền cục bộ `localhost`/`127.0.0.1`).
- Bấm vào biểu tượng ổ khóa/cài đặt trên thanh địa chỉ của trình duyệt và chọn **Cho phép (Allow)** Camera và Microphone.

### Lỗi 3: Kiểm tra CUDA không nhận diện GPU

Chạy lệnh kiểm tra nhanh:

```powershell
python -c "import torch; print('CUDA Available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

Nếu hiển thị `False`, hãy kiểm tra lại driver NVIDIA trên máy hoặc cài đặt PyTorch phiên bản hỗ trợ CUDA:

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

---

## 🧪 7. Chạy Kiểm Thử Hệ Thống (Automated Testing)

Để kiểm tra toàn diện tất cả API endpoints, bộ lọc dữ liệu, pipeline OCR/ASR và cơ chế GPU warm-up:

```powershell
pytest tests/ -v
```

Toàn bộ 21/21 bài kiểm thử tự động cần báo xanh (`PASSED`).
