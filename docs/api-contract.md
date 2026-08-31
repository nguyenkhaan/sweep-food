# SweepFood API Contract

> **Phiên bản:** M6.2 — 2026-08-31  
> **Tác giả:** Frontend team  
> **Base URL:** `{API_BASE_URL}` (env) — mặc định `http://10.0.2.2:8000/api/v1`  
> **Auth:** Bearer token (JWT access token) trong header `Authorization: Bearer <token>`  
> **Định dạng:** JSON (`Content-Type: application/json`)

---

## 1. Authentication — `/auth`

### POST `/auth/register`

Đăng ký tài khoản mới (chưa xác thực OTP).

> FE đang dùng mock payload với `email` thay vì `phone` theo implementation hiện tại.

**Request body:**
```json
{ "name": "string", "email": "user@example.com", "password": "string" }
```

**Response 200:**
```json
{
  "user": { "id": "uuid", "name": "string", "email": "string|null", "dietary_preference": "string|null", "avatar_url": "string|null" },
  "access_token": "string",
  "refresh_token": "string"
}
```

---

### POST `/auth/login`

Đăng nhập bằng email + password.

**Request body:**
```json
{ "email": "user@example.com", "password": "string" }
```

**Response 200:** Giống `register`.

---

### POST `/auth/refresh`

Làm mới access token.

**Request body:**
```json
{ "refresh_token": "string" }
```

**Response 200:**
```json
{ "access_token": "string", "refresh_token": "string" }
```

---

### POST `/auth/logout`

Huỷ session.

**Request body:**
```json
{ "refresh_token": "string" }
```

**Response 204:** No content.

---

### GET `/auth/me`

Lấy thông tin user đang đăng nhập.

**Response 200:**
```json
{ "id": "uuid", "name": "string", "email": "string|null", "dietary_preference": "string|null", "avatar_url": "string|null" }
```

---

### POST `/auth/forgot-password` ⚠️ *FE-assumed, chưa được BE stub*

Gửi OTP reset mật khẩu.

**Request body:**
```json
{ "phone": "string" }
```

**Response 200:**
```json
{ "message": "string" }
```

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
| 1 | `POST /auth/forgot-password` | FE-assumed; hiện mock dùng `email`, chưa có trong BE stub |
| 2 | `POST /scan/*` | FE gọi multipart; BE trả về ScanJob ngay (sync) hoặc polling qua `/scan/jobs/{id}` |
| 3 | `POST /pantry/items:batch` | FE hiện đọc `response.items` thay vì `response.created`; nếu BE đổi schema, cần cập nhật DTO |
| 4 | `GET /meal-plans` | FE sử dụng query `week_start`; mock implementation dùng `PUT /meal-plans/{weekStart}` |
| 5 | `POST /devices` | FE mock dùng `fcm_token` thay vì `token` |
| 6 | Field `is_manual` trong ShoppingListItem | FE dùng để quyết định có cho phép swipe-to-delete không |
| 7 | `DELETE /pantry/items/{id}` | FE hiểu là soft-delete (status → discarded); nếu BE hard-delete, cần thống nhất |
| 8 | Score fields trong suggestions | `e`, `a`, `p`, `u` tương ứng công thức `0.4E + 0.3A + 0.2P + 0.1U` trong PRD |
