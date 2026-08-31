# SweepFood API Contract

> **Phiên bản:** M6.2 — 2026-08-31 · *Mục 1 (Auth) đã đối chiếu với code BE thực tế; các mục khác vẫn là bản FE đề xuất*  
> **Tác giả:** Frontend team  
> **Base URL:** `{API_BASE_URL}` (env) — mặc định `http://10.0.2.2:8000/api` · BE dùng prefix `/api`, **không có `/v1`**  
> **Auth:** Bearer token (JWT access token) trong header `Authorization: Bearer <token>`  
> **Định dạng:** JSON (`Content-Type: application/json`)

---

## 1. Authentication — `/auth`, `/users`

> **Khác bản FE đề xuất ban đầu:** BE dùng **số điện thoại E.164 + mật khẩu + OTP**, không phải email/password. Đăng ký là **2 bước** (`register` → `verify/register`), đăng nhập là bước riêng. FE hiện (`auth_dto` / `auth_remote_data_source` / `session_controller`) giả định email + 1 bước → cần chỉnh khi nối.

**OTP (MVP / local):**
- Chưa có SMS gateway thật → OTP trả thẳng trong response body: `{ "otp": "...", "expires_in_seconds": 300 }`.
- `ENV=dev|test`: OTP **luôn là `123456`** (`DEFAULT_OTP`).
- OTP sống 300s · resend cooldown 60s · nhập sai 5 lần thì khoá 900s · tối đa 5 request / số / giờ (`429` khi vượt).

**Token:** access JWT sống 15 phút (`access_expires_in_seconds: 900`), refresh JWT 30 ngày (`2592000`). Endpoint cần đăng nhập: header `Authorization: Bearer <access_token>`.

**Envelope lỗi (mọi endpoint):**
```json
{ "status_code": 409, "detail": "Phone is already registered", "path": "/api/auth/register" }
```
Lỗi validate body → `422`, `detail` dạng `"body.phone: Phone must use E.164 format"` (email sai định dạng → `detail` = `"Email must be valid"`).

---

### POST `/auth/register`

Tạo tài khoản trạng thái `UNVERIFIED` và phát OTP đăng ký. **Không tạo session.**

**Request body:**
```json
{ "phone": "+84901234567", "password": "string (8–128)", "name": "string|null (≤100)", "email": "user@example.com|null (≤254)" }
```

**Response 200:**
```json
{ "otp": "123456", "expires_in_seconds": 300 }
```

**Lỗi:** `409` `"Phone is already registered"` / `"Email is already registered"` · `422` phone không đúng E.164 / password < 8 / email sai.

---

### POST `/auth/register/resend-otp`

Phát lại OTP đăng ký cho tài khoản `UNVERIFIED`.

**Request body:** `{ "phone": "+84901234567" }`
**Response 200:** `{ "otp": "123456", "expires_in_seconds": 300 }`
**Lỗi:** `403` `"Registration cannot be resent"` (không tồn tại / đã kích hoạt) · `429` cooldown / quá số lần.

---

### POST `/auth/verify/register`

Xác thực OTP đăng ký → tài khoản chuyển `ACTIVE`, set `phone_verified_at`. **Không phát token** — client gọi tiếp `/auth/login`.

**Request body:** `{ "phone": "+84901234567", "otp": "123456" }`
**Response 200:** `text/plain` — `verify account successfully`
**Lỗi:** `400` OTP sai / hết hạn / sai mục đích · `429` quá số lần nhập · `403` `"Registration cannot be verified"`.

---

### POST `/auth/login`

Đăng nhập bằng **phone + password** (tài khoản phải `ACTIVE`).

**Request body:**
```json
{ "phone": "+84901234567", "password": "string" }
```

**Response 200:**
```json
{
  "access_token": "jwt",
  "refresh_token": "jwt",
  "token_type": "bearer",
  "access_expires_in_seconds": 900,
  "refresh_expires_in_seconds": 2592000,
  "session_id": "uuid"
}
```
> Không trả về object `user`. Lấy hồ sơ qua `GET /users/profile`.

**Lỗi:** `401` `"Invalid phone or password"` — dùng chung cho sai phone, sai password, hoặc account chưa `ACTIVE` / bị `BANNED` (không tiết lộ nguyên nhân).

---

### POST `/auth/token/refresh`

Đổi refresh JWT lấy access JWT mới. **Không xoay vòng refresh token.**

**Request body:** `{ "refresh_token": "jwt" }`

**Response 200:**
```json
{ "access_token": "jwt", "token_type": "bearer", "access_expires_in_seconds": 900 }
```

**Lỗi:** `401` `"Refresh token is invalid"` (sai chữ ký / hết hạn / session đã thu hồi) · `403` account không còn `ACTIVE`.

---

### POST `/auth/logout`

Thu hồi **một** refresh session. **Cần `Authorization: Bearer <access_token>`.**

**Request body:** `{ "refresh_token": "jwt" }`
**Response 200:** `text/plain` — `Logout successfully`
**Lỗi:** `401` thiếu / sai access token, hoặc refresh token không thuộc user gọi / không tìm thấy.

---

### GET `/auth/sessions`

Danh sách session đang hoạt động của user. **Cần auth.**

**Response 200:**
```json
[
  {
    "id": "uuid",
    "ip_address": "string|null",
    "user_agent": "string|null",
    "expires_at": "2026-09-30T00:00:00Z",
    "created_at": "2026-08-31T00:00:00Z",
    "last_used_at": "2026-08-31T09:00:00Z|null"
  }
]
```

---

### DELETE `/auth/sessions/{session_id}`

Thu hồi một session do user sở hữu. **Cần auth.**

**Response 204:** No content.
**Lỗi:** `401` `"Session was not found"` (không tồn tại / không sở hữu).

---

### POST `/auth/password/reset`

Phát OTP quên mật khẩu. Luôn `200` (không tiết lộ số có tồn tại hay không).

**Request body:** `{ "phone": "+84901234567" }`
**Response 200:** `{ "otp": "123456", "expires_in_seconds": 300 }`

---

### POST `/auth/password/change`

Phát OTP đổi mật khẩu tới phone của user đang đăng nhập. **Cần auth.**

**Response 200:** `{ "otp": "123456", "expires_in_seconds": 300 }`

---

### POST `/auth/verify/change-password`

Xác thực OTP rồi đặt mật khẩu mới và **thu hồi toàn bộ session** của user.

**Request body:**
```json
{ "phone": "+84901234567", "otp": "123456", "purpose": "RESET_PASSWORD", "new_password": "string (8–128)" }
```
`purpose` ∈ `"RESET_PASSWORD" | "CHANGE_PASSWORD"`.

**Response 200:** `{ "message": "Password changed successfully" }`
**Lỗi:** `400` OTP sai / hết hạn / sai mục đích · `403` `"Password cannot be changed"` (account không `ACTIVE`).

---

### GET `/users/me`

Định danh rút từ access JWT — **chỉ `user_id` + `roles`**. **Cần auth.**

**Response 200:**
```json
{ "user_id": "uuid", "roles": ["USER"] }
```

---

### GET `/users/profile`

Hồ sơ đầy đủ của user đang đăng nhập. **Cần auth.**

**Response 200:**
```json
{
  "user_id": "uuid",
  "name": "string|null",
  "phone": "+84901234567",
  "phone_verified_at": "2026-08-31T00:00:00Z|null",
  "email": "string|null",
  "email_verified_at": "datetime|null",
  "preferences": {}
}
```
> Chưa có field riêng cho `dietary_preference` / `avatar_url` — nếu cần thì để trong `preferences` (JSON tự do); phải thống nhất danh sách key với BE.

---

### PATCH `/users/profile`

Cập nhật hồ sơ (chỉ `name` và `preferences`). **Cần auth.**

**Request body:** `{ "name": "string|null", "preferences": {} }` — mọi field optional.
**Response 200:** UserProfile object (như `GET /users/profile`).

---

### POST `/users/me/email/request-verification`

Gửi OTP để thêm / đổi email. **Cần auth.**
**Request body:** `{ "email": "user@example.com" }`
**Response 200:** `{ "otp": "123456", "expires_in_seconds": 300 }`

### POST `/users/me/email/verify`

Xác thực OTP cho email ở request trước rồi lưu. **Cần auth.**
**Request body:** `{ "otp": "123456" }`
**Response 200:** `text/plain` — `Verify Change Email successfully`

### POST `/users/me/phone/request-change`

Gửi OTP tới số điện thoại mới. **Cần auth.**
**Request body:** `{ "phone": "+84909999999" }`
**Response 200:** `{ "otp": "123456", "expires_in_seconds": 300 }`

### POST `/users/me/phone/confirm-change`

Xác thực OTP cho số ở request trước rồi thay số. **Cần auth.**
**Request body:** `{ "otp": "123456" }`
**Response 200:** `text/plain` — `Verify Change Phone succesfully` *(BE đang viết thiếu "s" — "succesfully")*

---

## 2. Catalog — `/ingredients`

### GET `/ingredients`

Tìm kiếm nguyên liệu trong catalog.

**Query params:** `q` (string, optional), `page` (int, default 1), `per_page` (int, default 20)

**Response 200:**
```json
{
  "items": [
    { "id": "uuid", "name": "string", "category": "string", "default_unit": "string", "aliases": ["string"] }
  ],
  "total": 100,
  "page": 1
}
```

---

### GET `/ingredients/{id}`

Chi tiết nguyên liệu.

**Response 200:**
```json
{ "id": "uuid", "name": "string", "category": "string", "default_unit": "string", "shelf_life_days": 7, "aliases": ["string"] }
```

---

## 3. Pantry — `/pantry`

### GET `/pantry/items`

Danh sách nguyên liệu trong kho.

**Query params:** `status` (`active`|`depleted`|`discarded`), `tier` (`fridge|freezer|pantry|immediate`, optional), `sort` (`priority`|`expiry`|`name`), `page` (int)

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "string",
      "category": "string",
      "quantity": 500.0,
      "unit": "g",
      "storage_tier": "fridge|freezer|pantry|immediate",
      "added_at": "2026-08-31T00:00:00Z",
      "source": "manual|label_scan|receipt_scan|voice",
      "status": "active|depleted|discarded",
      "expiry_date": "2026-09-03T00:00:00Z|null",
      "packed_date": "2026-08-28T00:00:00Z|null",
      "reference_shelf_life_days": 4
    }
  ],
  "total": 10
}
```

---

### POST `/pantry/items`

Thêm nguyên liệu thủ công.

**Request body:**
```json
{
  "name": "string",
  "category": "string|null",
  "quantity": 500.0,
  "unit": "g",
  "storage_tier": "fridge",
  "expiry_date": "2026-09-10T00:00:00Z|null",
  "source": "manual"
}
```

**Response 201:** PantryItem object (xem GET `/pantry/items`).

---

### GET `/pantry/items/{id}`

Chi tiết một nguyên liệu.

**Response 200:** PantryItem object.

---

### PATCH `/pantry/items/{id}`

Cập nhật nguyên liệu (partial update).

**Request body:** Các field cần update.

**Response 200:** PantryItem object.

---

### DELETE `/pantry/items/{id}`

Xoá / discard nguyên liệu.

**Response 204:** No content.

---

### POST `/pantry/items/{id}/consume`

Tiêu thụ (trừ) số lượng nguyên liệu.

**Request body:**
```json
{ "quantity": 200.0 }
```

**Response 200:** PantryItem object với `quantity` đã được cập nhật.

---

### POST `/pantry/items:batch`

Lưu nhiều nguyên liệu cùng lúc (từ receipt scan hoặc voice review).

**Request body:**
```json
{
  "items": [
    { "name": "string", "quantity": 1.0, "unit": "string", "storage_tier": "fridge", "source": "receipt_scan" }
  ]
}
```

**Response 201:**
```json
{
  "items": [
    { "id": "uuid", "name": "string", "quantity": 1.0, "unit": "string", "storage_tier": "fridge", "source": "receipt_scan" }
  ]
}
```

---

### GET `/pantry/summary`

Tóm tắt kho (số lượng theo tier, số sắp hết hạn).

**Response 200:**
```json
{
  "total_active": 12,
  "near_expiry_count": 3,
  "by_tier": { "fridge": 6, "freezer": 2, "pantry": 3, "immediate": 1 },
  "waste_saved_kg": 1.4
}
```

---

### POST `/pantry/cooked-food`

Lưu đồ ăn thừa sau khi nấu.

**Request body:**
```json
{ "name": "string", "quantity": 1.0, "unit": "phần", "storage_tier": "fridge", "expiry_date": "2026-09-02T00:00:00Z" }
```

**Response 201:** PantryItem object với `source: "cooked"`.

---

## 4. Multimodal Scan — `/scan`

> Tất cả endpoint scan là `multipart/form-data`. FE upload ảnh/audio, BE trả về `ScanJob` để FE hiển thị để xét duyệt (không tự động lưu vào kho).

### POST `/scan/label`

Quét tem nhãn sản phẩm (OCR).

**Form data:** `file` (image/jpeg hoặc image/png)

**Response 200 — ScanJob:**
```json
{
  "id": "uuid",
  "type": "label",
  "status": "done|processing|failed",
  "parsed": {
    "name": "string",
    "quantity": 500.0,
    "unit": "g",
    "expiry_date": "2026-09-10T00:00:00Z|null",
    "packed_date": "2026-08-28T00:00:00Z|null",
    "storage_tier": "fridge|null",
    "confidence": { "name": 0.95, "quantity": 0.88, "expiry_date": 0.72 },
    "warnings": ["string"]
  }
}
```

---

### POST `/scan/receipt`

Quét hoá đơn (OCR nhiều dòng).

**Form data:** `file` (image)

**Response 200 — ScanJob:**
```json
{
  "id": "uuid",
  "type": "receipt",
  "status": "done",
  "parsed": {
    "items": [
      { "name": "string", "quantity": 1.0, "unit": "string", "storage_tier": "fridge|null" }
    ]
  }
}
```

---

### POST `/scan/voice`

Ghi âm giọng nói (ASR).

**Form data:** `file` (audio/m4a hoặc audio/wav)

**Response 200 — ScanJob:**
```json
{
  "id": "uuid",
  "type": "voice",
  "status": "done",
  "parsed": {
    "transcript": "string",
    "items": [
      { "name": "string", "quantity": 1.0, "unit": "string" }
    ]
  }
}
```

---

### GET `/scan/jobs/{id}`

Poll trạng thái scan job (nếu BE xử lý bất đồng bộ).

**Response 200:** ScanJob object.

---

### POST `/scan/jobs/{id}/confirm`

Xác nhận lưu kết quả scan vào kho.

**Request body:**
```json
{ "items": [ { "name": "string", "quantity": 1.0, "unit": "string", "storage_tier": "fridge" } ] }
```

**Response 201:**
```json
{ "created": ["uuid"] }
```

---

## 5. Suggestions & Dishes — `/suggestions`, `/dishes`

### POST `/suggestions/dishes`

Gợi ý món ăn dựa trên kho hiện tại.

**Request body:**
```json
{ "filters": { "max_time_min": 30, "cuisine": "string|null", "difficulty": "string|null" } }
```

**Response 200:**
```json
{
  "items": [
    {
      "score": 95,
      "availability_ratio": 0.8,
      "to_buy_count": 2,
      "near_expiry_ingredients": ["string"],
      "breakdown": { "e": 0.92, "a": 0.8, "p": 0.74, "u": 0.78 },
      "dish": {
        "id": "uuid",
        "name": "string",
        "servings": 2,
        "prep_time_min": 15,
        "cook_time_min": 10,
        "cuisine": "string",
        "difficulty": "Dễ|Trung bình|Khó",
        "nutrition_per_serving": { "energy_kcal": 320, "protein_g": 28, "carb_g": 30, "lipid_g": 14 }
      }
    }
  ]
}
```

---

### GET `/dishes/{id}`

Chi tiết món ăn (nguyên liệu, công thức).

**Response 200:**
```json
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "servings": 2,
  "prep_time_min": 15,
  "cook_time_min": 10,
  "cuisine": "string",
  "difficulty": "string",
  "nutrition_per_serving": { "energy_kcal": 320, "protein_g": 28, "carb_g": 30, "lipid_g": 14 },
  "ingredients": [
    { "id": "uuid", "name": "string", "quantity": 200.0, "unit": "g", "in_pantry": true, "pantry_quantity": 300.0 }
  ],
  "steps": ["string"]
}
```

---

### POST `/dishes/{id}/cook`

Thực hiện nấu ăn (trừ nguyên liệu khỏi kho).

**Request body:**
```json
{ "servings": 2, "consumption_mode": "exact|half|all|custom", "custom_quantities": { "ingredient_id": 150.0 } }
```

**Response 200:**
```json
{
  "dish_id": "uuid",
  "dish_name": "string",
  "changes": [
    { "name": "string", "unit": "g", "before": 300.0, "after": 100.0, "near_expiry_used": true }
  ],
  "updated_pantry_items": ["uuid"],
  "depleted_item_ids": ["uuid"],
  "total_waste_saved_kg": 0.2
}
```

---

## 6. Meal Plan — `/meal-plans`

### GET `/meal-plans`

Danh sách meal plan của tuần hiện tại / tuần được query.

**Query params:** `week_start` (`YYYY-MM-DD`, optional)

**Response 200:**
```json
{
  "id": "uuid",
  "week_start": "2026-08-31",
  "slots": [
    { "id": "uuid", "date": "2026-09-01", "meal": "lunch|dinner|breakfast", "dish_id": "uuid", "dish_name": "string", "servings": 2 }
  ]
}
```

---

### PUT `/meal-plans/{weekStart}`

Tạo / cập nhật meal plan cho tuần cụ thể.

**Request body:**
```json
{ "week_start": "2026-08-31", "date": "2026-09-01", "meal": "lunch", "dish_id": "uuid", "servings": 2 }
```

**Response 200:** MealPlan object.

---

## 7. Shopping List — `/shopping-lists`

### GET `/shopping-lists`

Danh sách mua sắm hiện tại.

**Response 200:**
```json
{
  "id": "uuid",
  "source_label": "string|null",
  "items": [
    {
      "id": "uuid",
      "name": "string",
      "quantity": 150.0,
      "unit": "g",
      "category": "string",
      "checked": false,
      "already_in_pantry": false,
      "is_manual": false
    }
  ]
}
```

---

### POST `/shopping-lists/generate`

Tạo shopping list từ meal plan tuần này.

**Request body:**
```json
{ "week_start": "2026-08-31" }
```

**Response 200:** ShoppingList object.

---

### PATCH `/shopping-lists/{id}/items/{itemId}`

Tick / untick một mục.

**Request body:**
```json
{ "checked": true }
```

**Response 200:** ShoppingListItem object.

---

### DELETE `/shopping-lists/{id}/items/{itemId}`

Xoá mục thủ công khỏi danh sách.

**Response 204:** No content.

---

## 8. Devices & Notifications

### POST `/devices`

Đăng ký FCM device token (gọi sau login, sau khi có token FCM).

> FE hiện đang gửi `fcm_token` theo mock implementation.

**Request body:**
```json
{ "fcm_token": "string", "platform": "android|ios" }
```

**Response 201:**
```json
{ "fcm_token": "string", "platform": "string" }
```

---

### DELETE `/devices/{token}`

Huỷ đăng ký device token (gọi khi logout).

**Response 204:** No content.

---

### GET `/notifications`

Danh sách thông báo của user.

**Query params:** `page` (int, default 1), `per_page` (int, default 20)

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "type": "near_expiry|waste_win|meal_plan_ready",
      "title": "string",
      "body": "string",
      "created_at": "2026-08-31T08:00:00Z",
      "read": false,
      "pantry_item_id": "uuid|null",
      "dish_ids": ["uuid"]
    }
  ]
}
```

---

### POST `/notifications/{id}/read`

Đánh dấu thông báo đã đọc.

**Response 200:** AppNotification object.

---

## 9. Reports — `/reports`

### GET `/reports/waste-reduction`

Báo cáo giảm lãng phí thực phẩm.

**Query params:** `period` (`week|month|year`, default `month`)

**Response 200:**
```json
{
  "total_saved_kg": 1.4,
  "period": "month",
  "weekly_series": [0.2, 0.5, 0.3, 0.4],
  "top_saved_ingredients": [
    { "name": "string", "saved_kg": 0.5 }
  ]
}
```

---

## 10. Subscription — `/subscription`

### GET `/subscription`

Trạng thái gói premium hiện tại (MVP: luôn free).

**Response 200:**
```json
{ "plan": "free|premium", "expires_at": "string|null" }
```

---

### POST `/subscription/premium-interest`

Đăng ký quan tâm premium (chỉ ghi nhận, không thu tiền).

**Response 200:**
```json
{ "registered": true }
```

---

## Ghi chú cho Backend

| # | Endpoint | Ghi chú |
|---|---|---|
| 1 | Auth flow | Mục 1 đã viết lại theo code BE thật (phone + OTP, đăng ký 2 bước). FE code hiện giả định email / 1 bước → cần chỉnh `auth_dto`, `auth_remote_data_source`, `session_controller`. Quên mật khẩu = `POST /auth/password/reset` → `POST /auth/verify/change-password`, **không** phải `/auth/forgot-password`. |
| 2 | `POST /scan/*` | FE gọi multipart; BE trả về ScanJob ngay (sync) hoặc polling qua `/scan/jobs/{id}` |
| 3 | `POST /pantry/items:batch` | FE hiện đọc `response.items` thay vì `response.created`; nếu BE đổi schema, cần cập nhật DTO |
| 4 | `GET /meal-plans` | FE sử dụng query `week_start`; mock implementation dùng `PUT /meal-plans/{weekStart}` |
| 5 | `POST /devices` | FE mock dùng `fcm_token` thay vì `token` |
| 6 | Field `is_manual` trong ShoppingListItem | FE dùng để quyết định có cho phép swipe-to-delete không |
| 7 | `DELETE /pantry/items/{id}` | FE hiểu là soft-delete (status → discarded); nếu BE hard-delete, cần thống nhất |
| 8 | Score fields trong suggestions | `e`, `a`, `p`, `u` tương ứng công thức `0.4E + 0.3A + 0.2P + 0.1U` trong PRD |
