# Giải pháp kết nối Backend với SweepFood AI

> Trạng thái: solution design cho local integration. Backend hiện vẫn dùng mock provider. Các endpoint và cấu hình mới trong tài liệu chỉ hoạt động sau khi hoàn thành Giai đoạn 1 và Giai đoạn 2.

## 1. Mục tiêu

Tài liệu này mô tả cách kết nối hai service trong repository:

- `src/backend`: API chính mà mobile app và Swagger gọi vào.
- `sweep-food-AI`: service xử lý recommendation, OCR và ASR.

Tên thư mục đúng trong repository là `sweep-food-AI`.

Mục tiêu đầu tiên:

- Chạy hai service độc lập trên máy local.
- Backend gọi được AI qua HTTP.
- Người phát triển chỉ thao tác trên Swagger của backend.
- Backend giữ nguyên public API hiện tại.
- Backend không trả mock data khi đã bật AI provider.
- Khi AI dừng, backend trả lỗi có kiểm soát thay vì lỗi `500` không rõ nguyên nhân.

Mục tiêu này chưa bao gồm:

- Đồng bộ catalog từ PostgreSQL sang AI.
- Triển khai Docker hoặc Kubernetes cho AI.
- Message queue, distributed tracing hoặc autoscaling.
- Hoàn thiện toàn bộ khả năng đọc hóa đơn.

Các phần trên thuộc giai đoạn production và không chặn demo local.

## 2. Kiến trúc tổng thể

### 2.1. Sơ đồ kết nối local

```text
Swagger UI / Mobile Client
          |
          | HTTP :4000
          v
src/backend
  - xác thực JWT
  - kiểm tra request và file upload
  - đọc inventory của user
  - chuyển đổi contract
  - chuẩn hóa lỗi và response
          |
          | REST/JSON hoặc multipart HTTP :8001
          v
sweep-food-AI
  - recommendation engine
  - OCR
  - ASR
  - static catalog hiện tại
```

Backend chạy tại:

```text
http://127.0.0.1:4000
```

AI chạy tại:

```text
http://127.0.0.1:8001
```

Dùng cổng `8001` cho AI vì WireMock của backend đang dùng cổng `8000`.

### 2.2. Trách nhiệm của từng service

| Thành phần | Trách nhiệm |
|---|---|
| Backend | Public API, Swagger, JWT, user context, input validation, đọc database, chuyển đổi request/response và chuẩn hóa lỗi |
| AI | Candidate generation, ranking, OCR, ASR và model lifecycle |
| PostgreSQL | Dữ liệu user, inventory, recipe, ingredient và recommendation history |
| Mobile/Swagger | Chỉ gọi backend, không gọi AI trực tiếp |

Backend là Backend-for-Frontend. AI là internal service.

AI không cần biết access token, user ID hoặc cấu trúc database của backend trong giai đoạn demo.

### 2.3. Hướng phụ thuộc

Hệ thống chỉ cho phép phụ thuộc một chiều:

```text
backend -> sweep-food-AI
```

AI không gọi ngược lại backend. Quy tắc này tránh circular dependency và giúp hai service khởi động, kiểm thử và triển khai độc lập.

Backend vẫn phải khởi động được khi AI chưa chạy. Các route không dùng AI vẫn hoạt động bình thường. Route dùng AI trả `503` khi không kết nối được AI.

## 3. Giao thức giao tiếp

### 3.1. Lựa chọn giao thức

| Giao thức | Quyết định | Lý do |
|---|---|---|
| REST API | Chọn | Hai service đều dùng FastAPI. REST hỗ trợ JSON, multipart upload và Swagger sẵn có. Đây là phương án ít thay đổi nhất. |
| gRPC | Chưa dùng | Cần thêm Protobuf, code generation và tooling. Lợi ích chưa đủ lớn với bốn route hiện tại. |
| Message Queue | Chưa dùng | Luồng demo cần kết quả ngay để hiển thị trong Swagger. Queue làm tăng số thành phần và yêu cầu job polling. |
| WebSocket | Không dùng | Các request hiện tại là request-response, không cần stream hai chiều. |

Backend gọi AI bằng HTTP bất đồng bộ. Backend nên dùng `httpx.AsyncClient` vì FastAPI đang chạy trên async runtime.

Nếu backend import trực tiếp `httpx`, hãy khai báo `httpx` là dependency trực tiếp trong `src/backend/pyproject.toml`. Không dựa vào dependency bắc cầu.

### 3.2. Kiểu nội dung

| Nghiệp vụ | Content-Type từ backend sang AI |
|---|---|
| Recommendation | `application/json` |
| OCR label | `multipart/form-data` |
| OCR invoice | `multipart/form-data` |
| ASR | `multipart/form-data` |
| Health check | HTTP `GET` |

### 3.3. Mapping endpoint

| Public route của backend | Internal route của AI | Ghi chú |
|---|---|---|
| `GET /api/health/ai` | `GET /api/system/status` | Kiểm tra backend có gọi được AI hay không |
| `POST /api/recommendations` | `POST /api/recommend` | Backend tạo structured pantry từ inventory |
| `POST /api/extractions/ocr/label` | `POST /api/smart-input/ocr-upload` | Multipart field của hai bên đều là `file` |
| `POST /api/extractions/ocr/invoice` | `POST /api/smart-input/ocr-upload` | Demo chỉ trả kết quả `PARTIAL` |
| `POST /api/extractions/asr` | `POST /api/smart-input/asr-upload` | Backend đổi field `file` thành `audio` |

`GET /api/health/ai` không trả nguyên response của `/api/system/status`. Backend chỉ trả trạng thái đã chuẩn hóa:

```json
{
  "status": "ready",
  "provider": "SWEEP_FOOD_AI"
}
```

Endpoint này dùng để kiểm tra kết nối trên Swagger. Nó không thay thế liveness của backend.

## 4. Thiết kế phía backend

### 4.1. Cấu hình

Thêm các biến môi trường sau:

```env
AI_BASE_URL=http://localhost:8001
AI_CONNECT_TIMEOUT_SECONDS=3
AI_RECOMMEND_TIMEOUT_SECONDS=10
AI_OCR_TIMEOUT_SECONDS=30
AI_ASR_TIMEOUT_SECONDS=60
```

Không hard-code URL AI trong service hoặc router.

Khi chạy cả hai process trực tiếp trên máy local, dùng `127.0.0.1`. Nếu sau này chạy backend trong container, `127.0.0.1` sẽ trỏ vào chính container backend. Khi đó phải đặt hai service vào cùng Docker network và dùng service name, ví dụ:

```env
AI_BASE_URL=http://ai:8001
```

### 4.2. AI client

Backend chỉ cần một client, ví dụ:

```text
SweepFoodAIClient
  check_health()
  recommend(payload)
  extract_ocr(file, document_type)
  extract_asr(file, engine)
```

Không tạo interface, factory hoặc nhiều provider class khi mới có một AI provider.

Client chịu trách nhiệm:

- Tạo request HTTP tới AI.
- Chọn timeout theo nghiệp vụ.
- Parse JSON response.
- Kiểm tra các field bắt buộc trước khi trả dữ liệu cho service.
- Chuyển network error thành exception nội bộ có type rõ ràng.
- Không chứa logic đọc inventory hoặc tạo public response.

Trong demo, client chỉ cần kiểm tra các field mà backend thực sự sử dụng. Client có thể bỏ qua field thừa từ AI. Sau khi contract ổn định, hai bên mới chuyển sang validation chặt với versioned schema.

### 4.3. Service và mapper

Router không gọi AI client trực tiếp. Luồng đúng là:

```text
router -> domain service -> AI client -> AI service
```

Domain service chịu trách nhiệm:

- Tạo request phù hợp cho từng route.
- Chuyển AI response sang public DTO của backend.
- Tạo `request_id` của backend.
- Quyết định `SUCCEEDED`, `PARTIAL` hoặc `FAILED`.
- Thêm warning khi AI không trả đủ dữ liệu.

Backend không trả nguyên response của AI cho client. Nếu AI đổi field nội bộ, mapper là nơi duy nhất cần sửa.

## 5. Data flow theo từng route

### 5.1. Health check

```text
Swagger
  -> GET /api/health/ai
  -> backend gọi GET AI /api/system/status
  -> backend kiểm tra HTTP 200
  -> backend trả status đã chuẩn hóa
```

Kết quả mong đợi:

- AI đang chạy: backend trả `200` và `status=ready`.
- AI chưa chạy: backend trả `503`.
- AI phản hồi quá chậm: backend trả `504`.

### 5.2. OCR label

```text
Swagger upload image
  -> backend kiểm tra MIME type và kích thước
  -> backend đọc bytes
  -> backend gửi multipart field "file" sang AI
  -> AI trả raw_text và items
  -> backend lấy item đầu tiên
  -> backend map sang ExtractionResponse
```

Mapping cho demo:

| AI | Backend |
|---|---|
| `items[0].name` | `fields.ingredient_name` |
| `items[0].quantity_g` | `fields.quantity` |
| Hằng số `GRAM` | `fields.unit` |
| `raw_text` | `raw_text` |
| `items[0].confidence` nếu có | `confidence.ingredient_name` |

Nếu AI không trả ngày đóng gói hoặc hạn dùng, backend để `null` và thêm warning. Backend không đọc ngày từ field `note` bằng regex trong giai đoạn demo.

### 5.3. OCR invoice

Backend gửi file đến cùng endpoint OCR của AI. AI hiện chưa trả đủ giá, tổng tiền, ngày hóa đơn và tiền tệ.

Vì vậy backend phải:

- Map các item nhận được thành `line_items`.
- Để field tài chính chưa có thành `null`.
- Trả `status=PARTIAL`.
- Thêm warning `INVOICE_FINANCIAL_FIELDS_NOT_AVAILABLE`.

Backend không được tạo dữ liệu giá giả để làm response trông đầy đủ.

### 5.4. ASR

Backend nhận multipart field `file`, nhưng AI nhận field `audio`.

```text
backend field "file" -> AI field "audio"
```

Backend gửi thêm form field:

```text
engine=groq_whisper
```

AI trả một transcript và nhiều ingredient item. Public DTO hiện tại chỉ có một field `fields`. Để demo mà chưa đổi public contract, backend có thể trả item đầu tiên và thêm warning `ADDITIONAL_ITEMS_OMITTED` khi AI trả nhiều item.

Sau demo, backend nên đổi ASR response sang `items[]` để không mất dữ liệu.

### 5.5. Recommendation

Recommendation cần nhiều logic hơn các route extraction. Backend phải:

1. Xác thực user.
2. Đọc các inventory batch đang `ACTIVE` và có quantity lớn hơn `0`.
3. Join với master ingredient để lấy tên ổn định.
4. Chỉ chuyển `GRAM` và `KG` sang gram trong demo.
5. Bỏ qua unit không chuyển đổi được và thêm warning nội bộ.
6. Dùng default `household_size=4` và `max_cooking_time_min=45`.
7. Gọi `POST /api/recommend`.
8. Kiểm tra recipe ID do AI trả về có tồn tại trong backend database.
9. Map kết quả sang `RecommendationListResponseDTO`.

Free text trong request được giữ để trả lại cho client và phục vụ audit. Demo không dùng free text để phân tích ý định.

Recommendation nên triển khai sau OCR label và ASR vì route này phụ thuộc database, unit conversion và catalog ID.

## 6. Quản lý dependency giữa hai service

### 6.1. Không chia sẻ source code

Không import module Python từ `sweep-food-AI` vào backend và ngược lại.

Hai service chỉ chia sẻ HTTP contract. Cách này mang lại các lợi ích:

- Mỗi service có Python environment riêng.
- Backend không phải cài PyTorch, PaddleOCR hoặc XGBoost.
- AI không phải cài SQLAlchemy model của backend.
- Có thể nâng cấp và restart AI mà không restart backend, miễn là contract không đổi.

### 6.2. Data ownership trong demo

| Dữ liệu | Service sở hữu | Cách sử dụng |
|---|---|---|
| User và JWT | Backend | Không gửi access token sang AI |
| Inventory | Backend | Backend query và gửi structured pantry |
| Public response DTO | Backend | Backend map từ AI response |
| Recipe catalog dùng để inference | AI | Tiếp tục dùng static JSON trong demo |
| Model weights | AI | AI tự load khi khởi động |

Static catalog có thể khác database trong demo. Chấp nhận giới hạn này để kiểm tra kết nối trước. Không dùng kết quả demo để đánh giá độ chính xác cuối cùng của recommendation.

### 6.3. Runtime dependency

Backend không được fail startup chỉ vì AI chưa chạy.

Lý do:

- Developer vẫn cần dùng Swagger cho các module khác.
- AI có thời gian startup dài hơn do load model.
- Việc restart AI không nên kéo backend xuống theo.

Backend chỉ kiểm tra AI khi gọi `/api/health/ai` hoặc một route cần AI.

### 6.4. Contract dependency

Trong giai đoạn demo:

- Backend dùng các route AI hiện tại.
- Backend chỉ validate các field cần dùng.
- Hai repository không chia sẻ Pydantic model.

Sau khi demo ổn định:

- Thêm prefix `/internal/v1` cho AI API.
- Xuất OpenAPI schema của AI.
- Thêm contract test trong backend.
- Chỉ thay đổi breaking contract bằng version mới.

## 7. Error handling

Backend phải giữ một error contract ổn định cho Swagger và mobile client.

| Tình huống | HTTP status của backend | Cách xử lý |
|---|---:|---|
| File sai MIME type hoặc quá lớn | `422` | Backend từ chối trước khi gọi AI |
| Không kết nối được AI | `503` | Trả thông báo AI tạm thời không sẵn sàng |
| AI vượt quá timeout | `504` | Hủy chờ và trả timeout |
| AI trả JSON lỗi hoặc thiếu field bắt buộc | `502` | Xem đây là upstream contract error |
| AI trả `4xx` do payload backend tạo sai | `502` | Không đổ lỗi cho mobile client |
| AI trả `5xx` | `502` | Không lộ stack trace hoặc chi tiết model |
| AI trả thành công nhưng thiếu field tùy chọn | `200` với `PARTIAL` | Map dữ liệu có thật và thêm warning |

Ví dụ lỗi kết nối:

```json
{
  "status_code": 503,
  "detail": "AI service is unavailable.",
  "path": "/api/extractions/ocr/label"
}
```

Backend không được âm thầm trả mock response khi AI gặp lỗi. Việc này làm người test hiểu sai rằng integration đã thành công.

## 8. Timeout và retry

### 8.1. Timeout đề xuất cho local demo

| Operation | Connect timeout | Tổng thời gian chờ |
|---|---:|---:|
| Health check | 3 giây | 5 giây |
| Recommendation | 3 giây | 10 giây |
| OCR | 3 giây | 30 giây |
| ASR | 3 giây | 60 giây |

OCR và ASR cần timeout dài hơn vì AI có thể chạy trên CPU hoặc gặp model cold start.

### 8.2. Retry policy

Không tự động retry các request `POST` trong demo.

Lý do:

- OCR và ASR tốn CPU/GPU.
- Retry có thể chạy cùng một inference hai lần.
- Swagger cho phép người test chủ động bấm Execute lại.
- Hệ thống chưa có idempotency key giữa backend và AI.

Health check là `GET` nên có thể retry một lần khi gặp connection reset. Không retry khi AI đã trả HTTP response.

Chỉ thêm retry tự động sau khi có số liệu cho thấy lỗi mạng ngắn hạn xảy ra thường xuyên.

## 9. Trình tự triển khai

### Giai đoạn 1: Chứng minh kết nối

1. Chạy AI tại cổng `8001`.
2. Thêm `AI_BASE_URL` và timeout vào backend settings.
3. Thêm một AI client dùng `httpx.AsyncClient`.
4. Thêm `GET /api/health/ai`.
5. Kiểm tra endpoint trên Swagger backend.

Kết quả: backend gọi được AI nhưng chưa thay route nghiệp vụ.

### Giai đoạn 2: Vertical slice đầu tiên

1. Thay mock của `POST /api/extractions/ocr/label` bằng AI client.
2. Giữ input validation hiện tại.
3. Map AI response sang `ExtractionResponse`.
4. Thêm một test cho mapper và một test cho trường hợp AI unavailable.

Kết quả: một request đi đủ luồng Swagger -> backend -> AI -> backend.

### Giai đoạn 3: Các route còn lại

Thực hiện theo thứ tự:

1. ASR.
2. OCR invoice với `PARTIAL` response.
3. Recommendation.

Mỗi route phải có mapper riêng. Không gom toàn bộ schema mapping vào generic middleware.

### Giai đoạn 4: Production hardening

Chỉ bắt đầu sau khi demo local chạy ổn:

- Tạo Docker image cho AI.
- Hoàn thiện dependency lock.
- Thêm internal authentication.
- Thêm request ID, tracing và metrics.
- Đưa catalog vào PostgreSQL serving views.
- Thêm catalog revision và refresh snapshot.
- Version hóa internal API contract.
- Thay ASR singular field bằng `items[]`.
- Mở rộng invoice parser để đọc giá và tổng tiền.

## 10. Hướng dẫn chạy local

### 10.1. Terminal 1: chạy AI

Dùng Python environment hiện đang chạy được AI project:

```bash
cd sweep-food-AI
python -m uvicorn web.app:app --host 127.0.0.1 --port 8001
```

Kiểm tra trực tiếp:

```bash
curl http://127.0.0.1:8001/api/system/status
```

Không tiếp tục nếu AI chưa trả HTTP `200`.

### 10.2. Terminal 2: chuẩn bị backend

Trong `src/backend/.env`, thêm:

```env
AI_BASE_URL=http://127.0.0.1:8001
AI_CONNECT_TIMEOUT_SECONDS=3
AI_RECOMMEND_TIMEOUT_SECONDS=10
AI_OCR_TIMEOUT_SECONDS=30
AI_ASR_TIMEOUT_SECONDS=60
```

Backend còn cần PostgreSQL và Redis theo cấu hình hiện tại.

Nếu database local chưa có demo data, chạy:

```bash
cd src/backend
uv run -m src.seed
```

Seed command chỉ cho phép chạy trong local environment.

### 10.3. Terminal 2: chạy backend

```bash
cd src/backend
uv sync
uv run main.py
```

Kiểm tra:

```bash
curl http://127.0.0.1:4000/api/health/liveness
```

### 10.4. Mở Swagger

Mở:

```text
http://127.0.0.1:4000/docs
```

Kiểm tra kết nối AI trước:

1. Mở `GET /api/health/ai`.
2. Chọn **Try it out**.
3. Chọn **Execute**.
4. Xác nhận response là `200` và `status=ready`.

### 10.5. Đăng nhập trên Swagger

Các extraction route và recommendation route yêu cầu JWT.

1. Gọi `POST /api/auth/login`.
2. Nhập phone và password của demo user đã seed.
3. Copy `access_token` từ response.
4. Chọn nút **Authorize** ở đầu trang Swagger.
5. Dán access token vào ô `BearerAuth`.

Payload đăng nhập có dạng:

```json
{
  "phone": "<demo-user-phone-e164>",
  "password": "<demo-user-password>"
}
```

Lấy giá trị từ cấu hình seed local của môi trường đang chạy. Không ghi credential thật vào tài liệu hoặc commit vào Git.

### 10.6. Test OCR label

1. Mở `POST /api/extractions/ocr/label`.
2. Chọn **Try it out**.
3. Upload một file JPEG, PNG hoặc WebP.
4. Chọn **Execute**.
5. Kiểm tra `provider` là `SWEEP_FOOD_AI`, không phải `MOCK_OCR`.
6. Kiểm tra `persisted=false`.
7. Chấp nhận `PARTIAL` nếu AI chưa trả ngày hoặc confidence.

### 10.7. Test OCR invoice

1. Mở `POST /api/extractions/ocr/invoice`.
2. Upload ảnh hóa đơn có các mặt hàng thực phẩm.
3. Chọn **Execute**.
4. Kiểm tra `provider=SWEEP_FOOD_AI`.
5. Kiểm tra `fields.line_items` chứa các item AI nhận diện được.
6. Kiểm tra `status=PARTIAL` khi AI chưa đọc được giá, tổng tiền hoặc ngày hóa đơn.

### 10.8. Test ASR

1. Đảm bảo AI đã có `GROQ_API_KEY` nếu dùng Groq Whisper.
2. Mở `POST /api/extractions/asr`.
3. Upload file MP3, WAV hoặc OGG hợp lệ.
4. Chọn **Execute**.
5. Kiểm tra `raw_text` chứa transcript.
6. Kiểm tra `provider` không còn là `MOCK_ASR`.
7. Nếu AI tìm thấy nhiều ingredient nhưng DTO demo chỉ trả item đầu tiên, kiểm tra warning `ADDITIONAL_ITEMS_OMITTED`.

### 10.9. Test recommendation

1. Đảm bảo demo user có inventory batch đang `ACTIVE` và quantity lớn hơn `0`.
2. Mở `POST /api/recommendations`.
3. Gửi request:

```json
{
  "request": "Gợi ý món ăn từ nguyên liệu sắp hết hạn"
}
```

4. Chọn **Execute**.
5. Kiểm tra mỗi `recipe_id` tồn tại trong backend catalog.
6. Kiểm tra `provider` không còn là `MOCK`.
7. Kiểm tra `analysis.is_mock=false`.

Nếu AI trả recipe ID không tồn tại trong backend database, backend phải trả `502`. Backend không được tạo recipe summary giả.

### 10.10. Test lỗi kết nối

1. Dừng process AI.
2. Gọi lại `GET /api/health/ai`.
3. Xác nhận backend trả `503`.
4. Gọi lại OCR label.
5. Xác nhận backend trả `503`, không trả mock response và không trả raw stack trace.
6. Khởi động lại AI và xác nhận request hoạt động lại mà không restart backend.

## 11. Tiêu chí hoàn thành demo

Demo local hoàn thành khi tất cả điều kiện sau đạt:

- Backend và AI chạy ở hai process riêng.
- Swagger backend hiển thị `GET /api/health/ai`.
- Health endpoint trả `200` khi AI chạy và `503` khi AI dừng.
- Ít nhất OCR label chạy theo luồng backend -> AI -> backend.
- Response nghiệp vụ không còn `provider=MOCK_OCR`.
- Backend giữ public response schema hiện tại.
- Backend không log file upload hoặc raw transcript.
- Backend không cần restart sau khi AI restart.
- Có test tự động cho success mapping và AI unavailable.

## 12. Quyết định kiến trúc

| Quyết định | Kết luận |
|---|---|
| Service boundary | Giữ backend và AI là hai service riêng |
| Public entry point | Chỉ backend public |
| Giao tiếp local | REST qua HTTP |
| Contract adaptation | Backend mapper |
| AI database access trong demo | Chưa thực hiện |
| Retry POST | Không tự động retry |
| Fallback mock | Không fallback âm thầm |
| Message broker | Chưa cần |
| gRPC | Chưa cần |
| Service thứ ba | Không tạo |

Thiết kế này ưu tiên một vertical slice chạy được và quan sát được trên Swagger. Sau khi chứng minh kết nối, nhóm có thể mở rộng từng route mà không thay đổi service boundary.
