# Runbook demo local Backend ↔ SweepFood AI

Tài liệu này dùng để chạy hai service trực tiếp trên máy local. Cách chạy này cố ý dành cổng `8000` cho WireMock và chạy SweepFood AI ở `8001`.

## 1. Điều kiện cần

- Python và `pip` cho `sweep-food-AI`.
- Python 3.11 và `uv` cho `src/backend`.
- Docker Compose cho Redis, WireMock và Mailpit.
- Một PostgreSQL database mà máy local truy cập được.
- `ffmpeg` trong `PATH` nếu demo upload audio ASR.
- Một `GROQ_API_KEY` hợp lệ nếu demo upload audio thật. Không commit key vào Git.

Các cổng local:

| Thành phần | URL/cổng |
| --- | --- |
| SweepFood AI | `http://127.0.0.1:8001` |
| Backend API | `http://127.0.0.1:4000` |
| Backend Swagger | `http://127.0.0.1:4000/docs` |
| WireMock | `http://127.0.0.1:8000` |
| Redis | `127.0.0.1:6379` |
| Mailpit UI | `http://127.0.0.1:8025` |

## 2. Chuẩn bị SweepFood AI

Từ thư mục gốc repository:

    cd sweep-food-AI
    python -m venv venv
    source venv/bin/activate
    python -m pip install -r requirements.txt
    python -m pip install fastapi uvicorn python-multipart opencv-python-headless pillow ctranslate2 tokenizers
    cp .env.example .env

Sửa `.env` và thay placeholder bằng secret local, không commit file này:

    GROQ_API_KEY=<local-secret>

`GROQ_API_KEY` chỉ bắt buộc cho luồng upload audio đang dùng Groq Whisper. OCR, recommendation và ASR từ transcript/sample không cần key này.

Artifact `smart_input/correction/weights/model.bin` là tùy chọn và bị Git ignore. Nếu artifact không có, text corrector trả nguyên văn đầu vào; OCR/ASR parser vẫn chạy. Nếu cần correction model đầy đủ, đặt CTranslate2 artifact hợp lệ vào thư mục weights trước khi khởi động.

## 3. Chuẩn bị Backend và hạ tầng phụ trợ

Mở terminal khác:

    cd src/backend
    cp .env.example .env
    uv sync
    docker compose up -d redis wiremock mailpit

Không chạy service `api` bằng Compose trong runbook này. Backend chạy trực tiếp trên host để `AI_BASE_URL=http://127.0.0.1:8001` hoạt động.

Điền các biến sau trong `src/backend/.env`. Dùng giá trị local riêng cho database, JWT và tài khoản seed; không dùng lại placeholder trong môi trường chia sẻ:

    DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:5432/<database>
    TEST_DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:5432/<test-database>
    SEED_ADMIN_NAME=<local-admin-name>
    SEED_ADMIN_PHONE_E164=<local-e164-phone>
    SEED_ADMIN_EMAIL=<local-admin-email>
    SEED_ADMIN_PASSWORD=<local-admin-password>
    JWT_ACCESS_SECRET=<local-random-secret-at-least-32-bytes>
    JWT_REFRESH_SECRET=<different-local-random-secret-at-least-32-bytes>
    REDIS_URL=redis://127.0.0.1:6379/0
    WIREMOCK_URL=http://127.0.0.1:8000
    EMAIL_SMTP_HOST=127.0.0.1
    EMAIL_SMTP_PORT=1025
    AI_BASE_URL=http://127.0.0.1:8001
    AI_CONNECT_TIMEOUT_SECONDS=3
    AI_RECOMMEND_TIMEOUT_SECONDS=10
    AI_OCR_TIMEOUT_SECONDS=30
    AI_ASR_TIMEOUT_SECONDS=60

Tạo schema và dữ liệu seed:

    uv run alembic upgrade head
    uv run python scripts/seed.py

Tài khoản dùng để login là `SEED_ADMIN_PHONE_E164` và `SEED_ADMIN_PASSWORD` vừa cấu hình. Để recommendation trả danh sách có ý nghĩa, tài khoản demo cần có inventory batch `ACTIVE`, số lượng lớn hơn 0 và unit `GRAM` hoặc `KG`.

## 4. Khởi động đúng thứ tự

### 4.1. Khởi động AI trước

Trong terminal AI đã activate venv:

    cd sweep-food-AI
    source venv/bin/activate
    python -m uvicorn web.app:app --host 127.0.0.1 --port 8001

Từ terminal khác, đợi readiness trả `warmed_up: true`:

    curl -fsS http://127.0.0.1:8001/api/system/status

### 4.2. Khởi động Backend sau

Trong terminal Backend:

    cd src/backend
    uv run main.py

Kiểm tra liveness và kết nối AI qua Backend:

    curl -fsS http://127.0.0.1:4000/api/health/liveness
    curl -fsS http://127.0.0.1:4000/api/health/ai

`GET /api/health/ai` là public. Các route extraction và recommendation cần Bearer access token.

## 5. Login và Authorize trong Swagger

1. Mở `http://127.0.0.1:4000/docs`.
2. Gọi `POST /api/auth/login` với:

       {
         "phone": "<SEED_ADMIN_PHONE_E164>",
         "password": "<SEED_ADMIN_PASSWORD>"
       }

3. Sao chép `access_token` từ response.
4. Chọn **Authorize**, nhập riêng giá trị token vào `BearerAuth`. Swagger tự thêm prefix `Bearer`; không dán refresh token.

## 6. Thứ tự demo các route

1. `GET /api/health/ai`

   Kỳ vọng `200`, `status: "ready"`, `provider: "SWEEP_FOOD_AI"`.

2. `POST /api/extractions/ocr/label`

   Upload một file JPEG, PNG hoặc WebP hợp lệ bằng field `file`. Response không persist inventory; kiểm tra `provider`, `fields`, `confidence` và `warnings`.

3. `POST /api/extractions/ocr/invoice`

   Upload ảnh invoice bằng field `file`. Trong MVP, response luôn có `status: "PARTIAL"` vì AI hiện chưa cung cấp đầy đủ price, total, currency và invoice date. Warning chuẩn là `INVOICE_FINANCIAL_FIELDS_NOT_AVAILABLE`.

4. `POST /api/extractions/asr`

   Upload MP3, WAV hoặc OGG bằng field `file`. Luồng upload hiện dùng Groq Whisper nên cần `GROQ_API_KEY` và kết nối ra ngoài. Backend chỉ map item đầu tiên; nếu AI trả nhiều item sẽ có warning `ADDITIONAL_ITEMS_OMITTED`.

5. `POST /api/recommendations`

   Body mẫu:

       {
         "request": "Gợi ý món nhanh từ thực phẩm sắp hết hạn"
       }

   Kỳ vọng `200`, `analysis.is_mock: false`, `provider: "SWEEP_FOOD_AI"` trên từng item, score/component thật và recipe ID tồn tại trong catalog Backend. Nếu user không có inventory phù hợp, danh sách có thể rỗng.

Request upload rỗng, sai MIME type, quá kích thước hoặc body recommendation không hợp lệ phải trả `422` trước khi gọi AI.

## 7. Phân biệt lỗi upstream

| Status | Ý nghĩa tại Backend | Kiểm tra đầu tiên |
| --- | --- | --- |
| `502 Bad Gateway` | AI trả non-2xx, JSON lỗi hoặc response sai contract | Xem response trực tiếp từ AI và version/schema hai service |
| `503 Service Unavailable` | Không kết nối được AI hoặc readiness chưa warm | AI process, cổng `8001`, `AI_BASE_URL` |
| `504 Gateway Timeout` | AI vượt timeout của use case | Tải model, kích thước file và các biến `AI_*_TIMEOUT_SECONDS` |

Backend chỉ trả thông báo an toàn; không log raw upload, Bearer token hoặc API key.

## 8. Quality gate tự động

Mọi lệnh test dưới đây có timeout 100 giây.

Backend:

    cd src/backend
    timeout 100s uv run pytest -q src/test/test_setting.py src/test/test_sweep_food_ai_client.py src/test/test_ai_health.py src/test/test_health.py src/test/test_test_email_route.py src/test/test_extractions.py src/test/test_recommendation_provider.py src/test/test_recommendation_ai_service.py src/test/test_recommendation_router.py

AI:

    cd sweep-food-AI
    source venv/bin/activate
    python -m pip install pytest
    timeout 100s python -m pytest -q tests/test_smart_input.py tests/test_api_endpoints.py

Nếu một lệnh trả exit code `124`, dừng và thực hiện phần đó thủ công. Swagger matrix ở Step 6.2 vẫn là bước manual: cần sample image/audio thật, account có inventory và thao tác bật/tắt hoặc làm chậm AI.

## 9. Giới hạn MVP

- Invoice chỉ trả tập field chứng minh được và luôn là `PARTIAL`.
- ASR public contract Backend hiện trả một item; các item bổ sung được báo bằng warning.
- AI correction weight là artifact tùy chọn; dependency/container lock tái lập hoàn toàn vẫn thuộc backlog production.
- Chưa có service-to-service authentication; chỉ dùng topology local tin cậy.
- Không dùng runbook này làm cấu hình production và không commit các file `.env`.
