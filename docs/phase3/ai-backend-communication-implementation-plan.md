# Kế hoạch triển khai kết nối Backend với sweep-food-AI

## 1. Mục tiêu

Tài liệu này chuyển thiết kế trong `docs/ai-backend-communicate-solution.md` thành các bước triển khai có thể thực hiện và kiểm tra được.

Kết quả cuối cùng của giai đoạn này:

- `src/backend` gọi được `sweep-food-AI` qua REST trên môi trường local.
- Người phát triển test được bốn API nghiệp vụ từ Swagger của Backend.
- Backend giữ vai trò BFF: xác thực người dùng, đọc dữ liệu nghiệp vụ, chuyển đổi request và chuẩn hóa response.
- `sweep-food-AI` chỉ xử lý AI. Thay đổi trong dự án AI được giới hạn ở phần contract thật sự cần thiết.
- Lỗi timeout, mất kết nối và response sai schema có HTTP status rõ ràng.

## 2. Phạm vi

### Trong phạm vi

| Backend API | AI API | Kết quả cần đạt |
| --- | --- | --- |
| `GET /api/health/ai` | `GET /api/system/status` | Kiểm tra kết nối giữa hai service |
| `POST /api/extractions/ocr/label` | `POST /api/smart-input/ocr-upload` | Upload ảnh nhãn và trả về dữ liệu theo DTO của Backend |
| `POST /api/extractions/ocr/invoice` | `POST /api/smart-input/ocr-upload` | Trả về kết quả `PARTIAL` theo khả năng hiện tại của AI |
| `POST /api/extractions/asr` | `POST /api/smart-input/asr-upload` | Upload audio, đổi tên multipart field và chuẩn hóa kết quả |
| `POST /api/recommendations` | `POST /api/recommend` | Tạo pantry có cấu trúc, gọi AI và trả recipe theo DTO của Backend |

### Ngoài phạm vi của local demo

- CDC, outbox hoặc database riêng cho AI.
- Catalog revision trigger và immutable catalog snapshot.
- Message Queue, WebSocket, gRPC, circuit breaker hoặc service mesh.
- Chuẩn hóa container production và pipeline deploy.
- Retry cho các API `POST`.
- Invoice extraction đầy đủ subtotal, tax, discount và total.
- Thay đổi public schema ASR từ một item sang nhiều item.

Các hạng mục này chỉ triển khai khi local demo ổn định và có yêu cầu production rõ ràng.

## 3. Quyết định kỹ thuật

### Luồng gọi

```text
Swagger / Client
      |
      v
src/backend router
      |
      v
domain service ----> PostgreSQL
      |
      v
SweepFoodAIClient --REST/JSON or multipart--> sweep-food-AI
```

- Chỉ Backend public API cho client.
- Backend gọi AI bằng `httpx.AsyncClient`.
- JSON dùng cho recommendation và health check.
- `multipart/form-data` dùng cho OCR và ASR.
- Backend chuyển đổi schema tại service/mapper. Không đưa DTO nghiệp vụ của Backend vào AI core.
- Không thêm interface, factory hoặc adapter framework khi mới có một AI provider.

### Chính sách lỗi và retry

| Tình huống | Backend trả về | Retry |
| --- | --- | --- |
| Request người dùng không hợp lệ | `422` | Không |
| Không kết nối được AI | `503` | Không |
| AI timeout | `504` | Không |
| AI trả 4xx/5xx hoặc JSON sai contract | `502` | Không |
| AI trả dữ liệu thiếu nhưng vẫn dùng được | `200` và `status = PARTIAL` | Không |
| Health check lỗi tạm thời | Trạng thái unhealthy | Có thể retry một lần |

Backend không tự retry `POST` vì upload hoặc inference có thể tốn tài nguyên và không bảo đảm idempotent.

## 4. Thứ tự phụ thuộc

```text
Phase 0: Preflight
    |
    v
Phase 1: Config + AI client
    |
    v
Phase 2: Health check
    |
    v
Phase 3: OCR label
    |
    +-----------> Phase 4: Invoice + ASR
    |
    +-----------> Phase 5: Recommendation
                         |
                         v
                 Phase 6: E2E + bàn giao
```

Không bắt đầu các route nghiệp vụ trước khi health check chứng minh hai service kết nối ổn định.

## 5. Definition of Done chung

Mỗi Step chỉ hoàn thành khi đáp ứng đủ các điều kiện sau:

- Code chạy theo đúng contract đã ghi trong tài liệu này.
- Có unit test cho happy path và lỗi chính.
- Test không gọi mạng thật; dùng `httpx.MockTransport` hoặc mock dependency.
- Không làm hỏng route cũ ngoài phạm vi thay đổi.
- `ruff` và type check qua trên các file đã sửa.
- Không log token, API key, nội dung file nhạy cảm hoặc raw audio/image.
- Swagger hiển thị đúng request, response và HTTP status.

## 6. Kế hoạch triển khai

## Phase 0 — Xác nhận baseline và khả năng chạy local

Mục tiêu của Phase này là loại bỏ lỗi môi trường trước khi sửa luồng nghiệp vụ.

### Step 0.1 — Xác nhận runtime của hai service

**Công việc**

- Chạy Backend trên `http://127.0.0.1:4000`.
- Chạy AI trên `http://127.0.0.1:8001` bằng môi trường Python hiện có.
- Mở trực tiếp `GET http://127.0.0.1:8001/api/system/status`.
- Ghi lại biến môi trường bắt buộc của AI, đặc biệt là API key của model provider.
- Không xử lý container hoặc dependency lock trong Phase này nếu AI đã chạy được local.

**Acceptance criteria**

- Cả hai process chạy đồng thời và không trùng port.
- AI health endpoint trả HTTP `200` và JSON hợp lệ.
- Backend Swagger mở được tại URL hiện có của dự án.

**Cách kiểm tra**

```bash
curl -i http://127.0.0.1:8001/api/system/status
curl -i http://127.0.0.1:4000/docs
```

**Phụ thuộc:** Không có.

**File dự kiến sửa:** Không có. Chỉ cập nhật `.env` local nếu cần; không commit secret.

**Scope:** S.

### Step 0.2 — Chốt baseline test

**Công việc**

- Chạy các test hiện có của health, extraction và recommendation.
- Ghi nhận lỗi đã tồn tại trước khi tích hợp.
- Sửa fixture `FakeRecipe` trong test recommendation nếu lỗi do thiếu các field hiện tại của model, không phải do tích hợp AI.
- Không mở rộng sang sửa các lỗi không liên quan.

**Acceptance criteria**

- Có danh sách test pass/fail trước khi thay đổi.
- Các lỗi baseline liên quan trực tiếp đến phạm vi đã được sửa hoặc ghi rõ.

**Cách kiểm tra**

```bash
cd src/backend
uv run pytest -q src/test/test_health.py src/test/test_extractions.py \
  src/test/test_recommendation_provider.py src/test/test_recommendation_router.py
```

**Phụ thuộc:** Step 0.1.

**File dự kiến sửa:**

- `src/backend/src/test/test_recommendation_provider.py`

**Scope:** S.

### Checkpoint 0

- Hai service chạy độc lập.
- AI status endpoint hoạt động.
- Baseline test đã được ghi nhận.
- Nếu AI không thể khởi động bằng dependency hiện tại, dừng tại đây và bổ sung một task riêng cho reproducible environment. Không che lỗi bằng mock trong manual demo.

## Phase 1 — Xây nền giao tiếp từ Backend

Mục tiêu của Phase này là tạo một điểm duy nhất chịu trách nhiệm gọi AI và chuyển lỗi hạ tầng.

### Step 1.1 — Thêm cấu hình AI vào Backend

**Công việc**

- Thêm `AI_BASE_URL` với giá trị local mặc định `http://127.0.0.1:8001`.
- Thêm timeout riêng cho connect, recommendation, OCR và ASR.
- Chuẩn hóa URL để tránh lỗi dấu `/` cuối.
- Khai báo `httpx` là dependency trực tiếp và cập nhật lock file. Không phụ thuộc ngầm vào `fastapi[standard]`.
- Cập nhật `.env.example`; không đưa credential thật vào repository.

**Acceptance criteria**

- Backend đọc được toàn bộ cấu hình từ environment.
- Giá trị mặc định đủ để chạy local.
- Cấu hình sai kiểu hoặc timeout không hợp lệ làm ứng dụng fail sớm với thông báo rõ ràng.

**Cách kiểm tra**

- Unit test settings với default và environment override.
- Chạy import/startup của Backend.

**Phụ thuộc:** Checkpoint 0.

**File dự kiến sửa:**

- `src/backend/src/core/setting.py`
- `src/backend/.env.example`
- `src/backend/pyproject.toml`
- `src/backend/uv.lock`
- `src/backend/src/test/test_setting.py`

**Scope:** M.

### Step 1.2 — Tạo `SweepFoodAIClient`

**Công việc**

- Tạo một async client dùng chung cho health, JSON request và multipart upload.
- Tạo nhóm exception nhỏ: unavailable, timeout và bad upstream response.
- Parse JSON an toàn và kiểm tra các field tối thiểu trước khi trả dữ liệu cho domain service.
- Cho phép inject `httpx` transport/client trong test.
- Không thêm retry cho `POST`.

**Acceptance criteria**

- Client không phụ thuộc vào router hoặc database.
- Client phân biệt đúng timeout, lỗi kết nối, HTTP error và JSON sai.
- Test không cần AI process thật.

**Cách kiểm tra**

```bash
cd src/backend
uv run pytest -q src/test/test_sweep_food_ai_client.py
```

**Phụ thuộc:** Step 1.1.

**File dự kiến sửa:**

- `src/backend/src/service/sweep_food_ai_client.py`
- `src/backend/src/test/test_sweep_food_ai_client.py`

**Scope:** M.

### Step 1.3 — Map exception sang HTTP response

**Công việc**

- Đặt exception handler ở lớp dùng chung hiện có của Backend hoặc map tại service/router theo pattern hiện tại.
- Trả `503`, `504`, `502` theo bảng chính sách lỗi.
- Dùng error body ổn định, không trả raw response của AI.
- Gắn request/correlation ID nếu Backend đã có sẵn. Không tự xây tracing framework mới.

**Acceptance criteria**

- Mỗi loại lỗi AI tạo đúng HTTP status.
- Response lỗi không lộ stack trace hoặc secret.
- Các route khác giữ nguyên hành vi.

**Cách kiểm tra**

- API test cho từng exception bằng dependency override.

**Phụ thuộc:** Step 1.2.

**File dự kiến sửa:**

- `src/backend/src/core/exception.py`
- `src/backend/src/main.py`
- `src/backend/src/test/test_sweep_food_ai_client.py`

Tên file có thể điều chỉnh theo exception pattern thực tế của Backend.

**Scope:** S.

### Checkpoint 1

- Backend có một outbound client duy nhất cho AI.
- URL, timeout và lỗi không nằm rải rác trong router.
- Client tests pass.

## Phase 2 — Kết nối health check end-to-end

Mục tiêu của Phase này là chứng minh kết nối thật trước khi triển khai mapping dữ liệu.

### Step 2.1 — Mở rộng health service và DTO

**Công việc**

- Inject `SweepFoodAIClient` qua health dependency hiện có.
- Thêm DTO thể hiện `service`, `status`, `latency_ms` và thông tin lỗi an toàn nếu có.
- Health service gọi `GET /api/system/status` của AI.
- Giữ health check hiện tại của Backend hoạt động.

**Acceptance criteria**

- Health service không khởi tạo `httpx.AsyncClient` trực tiếp.
- AI chạy thì kết quả là healthy.
- AI tắt hoặc timeout thì kết quả phản ánh đúng nguyên nhân.

**Cách kiểm tra**

- Unit test health service với mock AI client.

**Phụ thuộc:** Checkpoint 1.

**File dự kiến sửa:**

- `src/backend/src/module/health/health_dependency.py`
- `src/backend/src/module/health/health_service.py`
- `src/backend/src/module/health/health_dto.py`
- `src/backend/src/test/test_health.py`

**Scope:** M.

### Step 2.2 — Thêm `GET /api/health/ai`

**Công việc**

- Thêm route vào health router.
- Khai báo response model và các response lỗi trong OpenAPI.
- Không yêu cầu người dùng biết URL nội bộ của AI.

**Acceptance criteria**

- Route xuất hiện trên Swagger của Backend.
- Route trả kết quả thật từ AI, không phải hard-coded.
- Test bao phủ AI healthy, unavailable và timeout.

**Cách kiểm tra**

```bash
cd src/backend
uv run pytest -q src/test/test_health.py
```

Sau đó gọi route trên Swagger khi AI đang chạy và khi đã dừng AI.

**Phụ thuộc:** Step 2.1.

**File dự kiến sửa:**

- `src/backend/src/module/health/health_router.py`
- `src/backend/src/test/test_health.py`

**Scope:** S.

### Checkpoint 2

- Swagger của Backend xác nhận được trạng thái kết nối AI.
- Kịch bản AI on/off cho kết quả đúng.
- Chỉ tiếp tục khi checkpoint này pass.

## Phase 3 — Tích hợp OCR label theo vertical slice

OCR label là route nghiệp vụ đầu tiên vì luồng upload và mapping nhỏ nhất.

### Step 3.1 — Thêm OCR upload vào AI client

**Công việc**

- Thêm method gửi file đến `/api/smart-input/ocr-upload` với đúng multipart field mà AI yêu cầu.
- Forward filename và content type hợp lệ.
- Dùng OCR timeout, không dùng recommendation timeout.
- Kiểm tra JSON và danh sách item tối thiểu trước khi trả về service.

**Acceptance criteria**

- Client gửi đúng tên field và bytes.
- File rỗng, AI error, timeout và malformed JSON được phân loại đúng.
- Có test bằng `MockTransport` kiểm tra request multipart.

**Cách kiểm tra**

```bash
cd src/backend
uv run pytest -q src/test/test_sweep_food_ai_client.py -k ocr
```

**Phụ thuộc:** Checkpoint 2.

**File dự kiến sửa:**

- `src/backend/src/service/sweep_food_ai_client.py`
- `src/backend/src/test/test_sweep_food_ai_client.py`

**Scope:** S.

### Step 3.2 — Thay mock OCR label bằng AI client

**Công việc**

- Giữ validation file hiện tại của extraction service.
- Inject AI client vào extraction flow theo dependency pattern của Backend.
- Map item đầu tiên phù hợp sang label DTO hiện tại.
- Chỉ điền field có bằng chứng từ AI response.
- Đánh dấu `PARTIAL` và warning khi AI thiếu field bắt buộc của Backend.
- Không gán ngày hết hạn hoặc số lượng ước đoán thành dữ liệu đã OCR nếu response không chứa chúng.

**Acceptance criteria**

- Route không còn gọi `mock_ocr_label`.
- Response giữ đúng public schema của Backend.
- Dữ liệu thiếu không được bịa hoặc gắn default gây hiểu nhầm.
- Barcode extraction hiện tại không bị thay đổi.

**Cách kiểm tra**

- Unit test mapper với response đầy đủ, thiếu field và danh sách rỗng.
- API test kiểm tra upload thành công và các lỗi `422/502/503/504`.

**Phụ thuộc:** Step 3.1.

**File dự kiến sửa:**

- `src/backend/src/module/extraction/extraction_dependency.py`
- `src/backend/src/module/extraction/extraction_service.py`
- `src/backend/src/module/extraction/extraction_route.py`
- `src/backend/src/module/extraction/extraction_dto.py`
- `src/backend/src/test/test_extractions.py`

Nếu `extraction_dependency.py` chưa tồn tại, tạo file này thay vì khởi tạo client trong router.

**Scope:** M.

### Step 3.3 — Manual test OCR label trên Swagger

**Công việc**

- Đăng nhập Backend và nhập bearer token trong Swagger nếu route yêu cầu auth.
- Upload một ảnh nhãn hợp lệ.
- Lưu sample response đã loại bỏ dữ liệu nhạy cảm.
- Lặp lại với file sai định dạng và khi AI đã tắt.

**Acceptance criteria**

- Happy path trả `200` với DTO của Backend.
- File không hợp lệ trả `422`.
- AI tắt trả `503`; timeout trả `504`.
- Log của Backend đủ để xác định upstream route và thời gian gọi nhưng không chứa raw file.

**Cách kiểm tra:** Swagger của Backend.

**Phụ thuộc:** Step 3.2.

**File dự kiến sửa:** Không có.

**Scope:** S.

### Checkpoint 3

- Một route nghiệp vụ đã chạy end-to-end với AI thật.
- Pattern client, dependency, mapper và test đã ổn định để dùng lại.

## Phase 4 — Hoàn tất invoice và ASR

Phase này tái sử dụng pattern của OCR label. Invoice chỉ đạt mức `PARTIAL` trong MVP.

### Step 4.1 — Tích hợp OCR invoice ở mức `PARTIAL`

**Công việc**

- Dùng lại method OCR upload; không tạo endpoint client trùng lặp.
- Map generic items của AI sang invoice line items có thể chứng minh được.
- Không tự tạo subtotal, tax, discount hoặc total nếu AI không trả dữ liệu tương ứng.
- Trả `status = PARTIAL` và warning mô tả rõ field còn thiếu.
- Loại bỏ lời gọi `mock_ocr_invoice` khỏi route này.

**Acceptance criteria**

- Invoice route gọi AI thật.
- Response luôn thể hiện đúng mức độ hoàn chỉnh.
- Không có giá trị tài chính được suy diễn từ dữ liệu không đủ.
- Test bao phủ nhiều item, danh sách rỗng và malformed item.

**Cách kiểm tra**

```bash
cd src/backend
uv run pytest -q src/test/test_extractions.py -k invoice
```

**Phụ thuộc:** Checkpoint 3.

**File dự kiến sửa:**

- `src/backend/src/module/extraction/extraction_service.py`
- `src/backend/src/module/extraction/extraction_route.py`
- `src/backend/src/module/extraction/extraction_dto.py`
- `src/backend/src/test/test_extractions.py`

**Scope:** M.

### Step 4.2 — Thêm ASR upload vào AI client

**Công việc**

- Thêm method gọi `/api/smart-input/asr-upload`.
- Backend nhận upload field theo public API hiện tại và gửi sang AI bằng field `audio`.
- Dùng ASR timeout.
- Validate transcript và item list tối thiểu.

**Acceptance criteria**

- Multipart field sang AI là `audio`.
- Client giữ filename và content type phù hợp.
- Test bao phủ success, timeout, HTTP error và JSON sai.

**Cách kiểm tra**

```bash
cd src/backend
uv run pytest -q src/test/test_sweep_food_ai_client.py -k asr
```

**Phụ thuộc:** Checkpoint 3.

**File dự kiến sửa:**

- `src/backend/src/service/sweep_food_ai_client.py`
- `src/backend/src/test/test_sweep_food_ai_client.py`

**Scope:** S.

### Step 4.3 — Thay mock ASR bằng AI client

**Công việc**

- Giữ public upload field của Backend để không làm hỏng client hiện tại.
- Map transcript và ingredient đầu tiên sang DTO đơn hiện tại.
- Nếu AI trả nhiều ingredient, trả item đầu tiên cùng warning và trạng thái `PARTIAL`.
- Không gán quantity hoặc expiry ước tính thành dữ liệu đã được nhận diện nếu thiếu source marker.
- Loại bỏ lời gọi `mock_asr` khỏi route này.

**Acceptance criteria**

- ASR route gọi AI thật và public schema không đổi.
- Response nhiều item không bị im lặng làm mất dữ liệu; warning phải xuất hiện.
- Test bao phủ zero, one và many items.

**Cách kiểm tra**

```bash
cd src/backend
uv run pytest -q src/test/test_extractions.py -k asr
```

**Phụ thuộc:** Step 4.2.

**File dự kiến sửa:**

- `src/backend/src/module/extraction/extraction_service.py`
- `src/backend/src/module/extraction/extraction_route.py`
- `src/backend/src/module/extraction/extraction_dto.py`
- `src/backend/src/test/test_extractions.py`

**Scope:** M.

### Step 4.4 — Manual test invoice và ASR trên Swagger

**Công việc**

- Upload một ảnh invoice và một audio sample hợp lệ.
- Kiểm tra trạng thái `PARTIAL` và warning.
- Kiểm tra file sai loại, AI tắt và timeout.

**Acceptance criteria**

- Cả hai route chạy qua Backend Swagger.
- HTTP status và error body đúng chính sách chung.
- Invoice không báo `COMPLETE` trong MVP.

**Phụ thuộc:** Step 4.1 và Step 4.3.

**File dự kiến sửa:** Không có.

**Scope:** S.

### Checkpoint 4

- Ba extraction route đã thay mock bằng AI thật.
- Invoice được ghi rõ là `PARTIAL`.
- Barcode route và các extraction contract ngoài phạm vi không bị ảnh hưởng.

## Phase 5 — Tích hợp recommendation

Recommendation phức tạp hơn vì Backend phải tạo pantry từ database và hai service đang có khác biệt về response semantics.

### Step 5.1 — Chốt contract recommendation trước khi code

**Công việc**

- So sánh request/response DTO của Backend với contract `/api/recommend` hiện tại.
- Chốt tên canonical cho dietary restrictions, allergies, disliked ingredients và preferred cuisines.
- Xác định nguồn thật cho `score`, các score component và `model_version`.
- Nếu AI chưa trả đủ dữ liệu có ý nghĩa, chọn một trong hai cách:
  - bổ sung field tương thích nhỏ tại boundary của AI; hoặc
  - điều chỉnh Backend DTO bằng một thay đổi contract được phê duyệt.
- Không hard-code score component hoặc model version giả để làm demo pass.

**Acceptance criteria**

- Có bảng mapping field một-một cho request và response.
- Mỗi field trong Backend response có nguồn dữ liệu rõ ràng.
- Quyết định contract được ghi lại trước Step 5.3.

**Cách kiểm tra:** Review contract bằng sample JSON hai chiều.

**Phụ thuộc:** Checkpoint 2. Có thể thực hiện song song với Phase 4.

**File dự kiến sửa:**

- `docs/ai-backend-communicate-solution.md` nếu contract thay đổi
- `sweep-food-AI/web/app.py` chỉ khi cần thêm response field ở boundary
- Test endpoint tương ứng trong `sweep-food-AI`

**Scope:** M.

### Step 5.2 — Tạo structured pantry từ database

**Công việc**

- Query inventory đang hoạt động của user/household hiện tại.
- Join dữ liệu ingredient/master data cần thiết để lấy canonical name và unit.
- Chuyển đổi quantity chỉ với các unit có quy tắc chắc chắn, ưu tiên mass unit.
- Gửi expiry date khi có; không bịa ngày hết hạn.
- Map household size và typed preferences theo contract ở Step 5.1.
- Không để router tự query database hoặc tự build AI payload.

**Acceptance criteria**

- Payload phản ánh đúng inventory của request hiện tại.
- Item không thể chuyển unit được xử lý theo rule đã ghi rõ: bỏ qua kèm warning hoặc gửi unit được AI hỗ trợ.
- User A không đọc được inventory/preferences của user B.
- Có test cho pantry rỗng, nhiều batch, item hết hạn và unit không hỗ trợ.

**Cách kiểm tra:** Unit test service/query bằng database test fixture.

**Phụ thuộc:** Step 5.1.

**File dự kiến sửa:**

- `src/backend/src/module/recommendation/recommendation_service.py`
- `src/backend/src/module/recommendation/recommendation_dto.py`
- `src/backend/src/module/recommendation/recommendation_dependency.py`
- `src/backend/src/test/test_recommendation_provider.py`

**Scope:** M.

### Step 5.3 — Thêm recommendation method vào AI client

**Công việc**

- Gửi structured pantry, expiry, household size và preferences đến `/api/recommend`.
- Dùng recommendation timeout.
- Validate danh sách kết quả, recipe identifier và score fields theo contract đã chốt.
- Không retry request.

**Acceptance criteria**

- Client gửi đúng JSON contract.
- Response sai recipe ID hoặc thiếu field bắt buộc trả lỗi upstream rõ ràng.
- Tests bao phủ success, empty result, timeout, upstream error và malformed response.

**Cách kiểm tra**

```bash
cd src/backend
uv run pytest -q src/test/test_sweep_food_ai_client.py -k recommend
```

**Phụ thuộc:** Step 5.1 và Checkpoint 1.

**File dự kiến sửa:**

- `src/backend/src/service/sweep_food_ai_client.py`
- `src/backend/src/test/test_sweep_food_ai_client.py`

**Scope:** S.

### Step 5.4 — Thay recommendation mock bằng AI call

**Công việc**

- Inject AI client vào `RecommendationService`.
- Build request bằng logic Step 5.2 rồi gọi AI client.
- Batch-load recipe từ Backend database bằng các ID AI trả về.
- Dùng dữ liệu Backend làm nguồn chính cho tên, media và recipe detail.
- Giữ thứ tự ranking từ AI.
- Bỏ recipe ID không còn tồn tại và thêm warning/metric; không query từng recipe gây N+1.
- Trả `is_mock = false`.
- Không thêm lưu recommendation history nếu demo không cần.

**Acceptance criteria**

- Route không còn chạy ranking mock trong production path.
- Recipe trả về tồn tại trong database Backend.
- Thứ tự đúng với AI response.
- Không có N+1 query.
- Test bao phủ pantry rỗng, AI trả ID lạ, danh sách rỗng và lỗi upstream.

**Cách kiểm tra**

```bash
cd src/backend
uv run pytest -q src/test/test_recommendation_provider.py \
  src/test/test_recommendation_router.py
```

**Phụ thuộc:** Step 5.2 và Step 5.3.

**File dự kiến sửa:**

- `src/backend/src/module/recommendation/recommendation_service.py`
- `src/backend/src/module/recommendation/recommendation_dependency.py`
- `src/backend/src/module/recommendation/recommendation_router.py`
- `src/backend/src/module/recommendation/recommendation_dto.py`
- `src/backend/src/test/test_recommendation_provider.py`

**Scope:** M.

### Step 5.5 — Manual test recommendation trên Swagger

**Công việc**

- Chuẩn bị user có inventory và preferences trong database local.
- Gọi route từ Swagger bằng access token của user đó.
- Đối chiếu payload đã log ở mức metadata với inventory thực tế.
- Kiểm tra AI trả kết quả, pantry rỗng và AI tắt.

**Acceptance criteria**

- Happy path trả recipe thật và `is_mock = false`.
- Kết quả không chứa recipe ngoài catalog Backend.
- AI tắt trả `503`; timeout trả `504`; response sai contract trả `502`.

**Phụ thuộc:** Step 5.4.

**File dự kiến sửa:** Không có.

**Scope:** S.

### Checkpoint 5
aaaaaa
- Bốn route nghiệp vụ đều gọi AI thật.
- Recommendation có contract rõ ràng và không bịa score.
- Backend vẫn sở hữu dữ liệu nghiệp vụ và authorization.

## Phase 6 — Kiểm thử tích hợp và bàn giao local demo

### Step 6.1 — Chạy quality gate

**Công việc**

- Chạy toàn bộ test liên quan.
- Chạy lint và type check trên file đã sửa.
- Kiểm tra log không chứa raw file, token hoặc API key.
- Kiểm tra OpenAPI schema không có model trùng tên hoặc response chưa khai báo.

**Acceptance criteria**

- Toàn bộ test mục tiêu pass.
- Không có lint/type error mới trong phạm vi thay đổi.
- Không có regression trên health, extraction và recommendation route cũ.

**Cách kiểm tra**

```bash
cd src/backend
uv run pytest -q src/test/test_sweep_food_ai_client.py src/test/test_health.py \
  src/test/test_extractions.py src/test/test_recommendation_provider.py \
  src/test/test_recommendation_router.py
uv run ruff check src/service/sweep_food_ai_client.py src/module/health \
  src/module/extraction src/module/recommendation
```

Chạy type-check theo command hiện có của repository trên cùng nhóm file.

**Phụ thuộc:** Checkpoint 4 và Checkpoint 5.

**File dự kiến sửa:** Chỉ sửa file có lỗi thuộc phạm vi.

**Scope:** M.

### Step 6.2 — Chạy test matrix trên Swagger

**Công việc**

| Case | AI | Input | Kết quả mong đợi |
| --- | --- | --- | --- |
| Health success | On | Không | `200`, healthy |
| Health unavailable | Off | Không | Trạng thái unhealthy hoặc status theo contract health |
| OCR label success | On | Ảnh nhãn hợp lệ | `200`, normalized response |
| OCR invoice partial | On | Ảnh invoice hợp lệ | `200`, `PARTIAL` |
| ASR success/partial | On | Audio hợp lệ | `200`, transcript và item/warning |
| Recommendation success | On | User có inventory | `200`, `is_mock = false` |
| Validation | On | File/request sai | `422` |
| AI unavailable | Off | Request hợp lệ | `503` |
| AI timeout | On nhưng chậm | Request hợp lệ | `504` |

**Acceptance criteria**

- Tất cả case trong bảng có kết quả đúng.
- Người khác có thể lặp lại demo chỉ bằng runbook và sample files.

**Phụ thuộc:** Step 6.1.

**File dự kiến sửa:** Không có.

**Scope:** M.

### Step 6.3 — Viết runbook local

**Công việc**

- Ghi command khởi động AI trước, Backend sau.
- Liệt kê environment variables cần thiết nhưng không ghi secret.
- Ghi URL Swagger, cách login/authorize và thứ tự test bốn route.
- Ghi cách nhận biết lỗi `502/503/504`.
- Ghi rõ invoice là `PARTIAL` trong MVP.

**Acceptance criteria**

- Một developer mới có thể chạy demo từ clean checkout với dependency đã cài.
- Runbook không phụ thuộc vào kiến thức truyền miệng.

**Phụ thuộc:** Step 6.2.

**File dự kiến sửa:**

- `docs/phase3/ai-backend-local-demo-runbook.md`
- `.env.example` của từng service nếu còn thiếu biến

**Scope:** S.

### Checkpoint 6 — Hoàn thành

- Health check và bốn route nghiệp vụ chạy được từ Swagger của Backend.
- Test tự động và test matrix đều pass.
- Mock không còn nằm trên production path của bốn route.
- Local runbook đủ để bàn giao.
- Các giới hạn MVP và backlog production được ghi rõ.

## 7. Rủi ro và cách xử lý

| Rủi ro | Ảnh hưởng | Cách xử lý trong plan |
| --- | --- | --- |
| AI dependency hiện tại không tái tạo được | Không chạy demo trên máy mới | Gate tại Step 0.1; nếu fail thì tạo task environment riêng trước khi tích hợp |
| AI và Backend dùng recipe catalog khác nhau | AI trả ID Backend không biết | Validate ID, batch-load từ Backend và bỏ ID lạ có warning |
| Recommendation score khác nghĩa | API trả dữ liệu gây hiểu nhầm | Chặn tại Step 5.1, không hard-code score giả |
| AI OCR không trả đủ field | Backend schema không đầy đủ | Trả `PARTIAL`, chỉ map field có nguồn |
| ASR trả nhiều item nhưng Backend nhận một item | Mất dữ liệu | Trả item đầu tiên cùng warning; nâng schema để backlog |
| File upload quá lớn | Tốn RAM và timeout | Giữ validation size/type trước khi gọi AI |
| Hai service có timeout không đồng bộ | Request treo lâu | Timeout theo từng use case tại Backend |
| Thay đổi cùng extraction files gây conflict | Chậm merge | Làm label trước; invoice và ASR theo thứ tự hoặc chia ownership rõ ràng |

## 8. Câu hỏi cần chốt

Các câu hỏi sau không chặn Phase 0–4, nhưng câu 1–3 phải có câu trả lời trước Step 5.4:

1. `score` và từng score component trong Backend sẽ lấy chính xác từ field nào của AI?
2. `model_version` là version của model provider, prompt hay recommendation algorithm?
3. Canonical preference fields hiện nằm ở bảng/DTO nào và AI hỗ trợ field nào?
4. Với unit AI không hỗ trợ, Backend bỏ item kèm warning hay AI nhận original unit?
5. Health route sẽ public hay yêu cầu authentication trên local demo?

## 9. Cách chia việc an toàn

- Phase 0, 1 và 2 làm tuần tự vì mọi route phụ thuộc vào AI client và health gate.
- Sau Checkpoint 2, contract recommendation ở Step 5.1 có thể làm song song với OCR label.
- Step 4.1 và Step 4.2 có thể làm song song nếu không cùng sửa extraction service/router. Nếu cùng file, làm tuần tự để tránh conflict.
- Step 5.2 và Step 5.3 có thể làm song song sau khi Step 5.1 chốt contract.
- Phase 6 chỉ bắt đầu khi Checkpoint 4 và 5 cùng pass.

## 10. Backlog sau local demo

Chỉ ưu tiên các mục sau khi demo đã ổn định:

1. Tạo AI container và dependency lock có thể tái tạo.
2. Thêm service-to-service authentication.
3. Thêm structured logging, metrics và distributed tracing.
4. Thiết kế read-only view hoặc API catalog có revision.
5. Thêm request-local immutable catalog snapshot.
6. Dùng CDC/outbox nếu cần database độc lập vật lý.
7. Mở rộng DTO ASR thành danh sách item.
8. Hoàn thiện invoice schema và extraction model.
9. Chỉ thêm retry/circuit breaker dựa trên số liệu lỗi thực tế.

Shared read-only PostgreSQL view, nếu dùng sau này, chỉ tạo **logical service independence**. Nó không tạo physical database independence.
