# SweepFood API Contract

> **Phiên bản:** M7 — 2026-09-05 · Đối chiếu trực tiếp với code BE (`src/backend/src/module/**`) cho **Auth, Users, Catalog, Recipes, Inventory, Cooking, Recommendations, Meal Plans, Shopping Lists, Favorites, Devices & Notifications**. Chỉ còn **Reports** và **Subscription** là chưa có endpoint BE — giữ nguyên bản FE đề xuất, đánh dấu rõ **[MOCK ONLY]**.
> **Tác giả:** Frontend team, đối chiếu BE ngày 2026-09-05
> **Base URL:** `{API_BASE_URL}` (env) — BE chạy cổng **`4000`**, prefix `/api`, **không có `/v1`**. Local: `http://localhost:4000/api` (web/desktop) hoặc `http://10.0.2.2:4000/api` (Android emulator) / `http://127.0.0.1:4000/api` (USB + `adb reverse tcp:4000 tcp:4000`). Cổng `8000` trong `docker-compose.yaml` là WireMock, không phải API.
> **Auth:** Bearer token (JWT access token) trong header `Authorization: Bearer <token>` cho mọi route trừ `POST /auth/register`, `/auth/register/resend-otp`, `/auth/verify/register`, `/auth/login`, `/auth/token/refresh`, `/auth/password/reset`.
> **Định dạng:** JSON (`Content-Type: application/json`). Ghi (POST/PATCH/DELETE) trên `Inventory` và `Shopping Lists` **bắt buộc** header `Idempotency-Key: <uuid bất kỳ, duy nhất theo request>`.
> **Envelope lỗi (mọi endpoint):** `{ "status_code": 409, "detail": "...", "path": "/api/..." }`. Lỗi validate body → `422`.

---

## 1. Catalog — `/ingredients`

> **[CẬP NHẬT]** Khác bản trước: `category` là **object**, param search là `q` (không phải `query`), nutrition/shelf-life chỉ có ở detail.

### GET `/ingredients`

**Query:** `q` (string, optional — khớp tên hoặc alias), `category` (string, optional — khớp tên category, không phân biệt hoa/thường), `page` (default 1), `per_page` (default 20, tối đa 100).

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Spinach",
      "category": { "id": "uuid", "name": "Vegetables" },
      "default_unit": "GRAM",
      "default_storage_mode": "REFRIGERATED",
      "aliases": ["Rau bina"]
    }
  ],
  "total": 4,
  "page": 1,
  "per_page": 20
}
```

`default_unit` ∈ `KG|GRAM|LITER|ML|PIECE|PACK|OTHER`. `default_storage_mode` ∈ `ROOM_TEMPERATURE|REFRIGERATED|FROZEN|DRY_SHELF|null`.

### GET `/ingredients/{id}`

**Response 200:** như trên, cộng thêm:
```json
{
  "description": "Fresh leafy spinach.",
  "default_media_url": null,
  "nutrition": {
    "calories": 23.0, "protein_g": 2.9, "fat_g": 0.4, "carbs_g": 3.6,
    "sugar_g": 0.4, "sodium_mg": 79.0, "other_nutrients": { "fiber_g": 2.2 }
  },
  "shelf_life_rules": [
    { "scope": "INGREDIENT", "storage_mode": "REFRIGERATED", "min_days": 3, "max_days": 5, "default_days": 4 }
  ]
}
```
`scope` ∈ `INGREDIENT|CATEGORY`. Danh sách có thể trống. **Không có field phẳng `reference_shelf_life_days` hay `nutrition_per_100g`** — FE tự suy ra 1 con số nếu cần (chọn rule khớp `default_storage_mode`, fallback rule đầu).

---

## 2. Recipes — `/recipes`

> **[CẬP NHẬT]** Thay cho mục "Suggestions & Dishes" cũ. Đây là API duy nhất cho chi tiết món ăn — **không có** `/dishes/{id}`.

### GET `/recipes`

**Query:** `q` (tên, optional), `tag` (khớp trong `tags.values`, optional), `max_cooking_minutes` (optional), `page`, `per_page`.

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid", "name": "Grilled chicken breast", "description": "...",
      "media_url": null, "default_servings": 2.0, "estimated_cooking_minutes": 25,
      "estimated_cost": 75000.0, "tags": { "values": ["high-protein", "quick"] }
    }
  ],
  "total": 4, "page": 1, "per_page": 20
}
```
`default_servings`/`servings` là `Decimal` — **có thể serialize dạng string** (`"2.00"`), FE phải parse tolerant.

### GET `/recipes/{id}?servings=<số>`

Không truyền `servings` → BE dùng `default_servings`. Trả về **định lượng đã scale theo servings yêu cầu**, `nutrition` là **tổng cho số servings đó** (không phải per-serving — chia lại nếu cần):
```json
{
  "...(như list item)...",
  "servings": 2.0,
  "instructions": { "steps": ["Season chicken", "Grill until cooked"] },
  "nutrition": { "calories": 330.0, "protein_g": 62.0, "fat_g": 7.2, "carbs_g": 0.0, "sugar_g": 0.0, "other_nutrients": {} },
  "ingredients": [
    {
      "recipe_ingredient_id": "uuid", "master_ingredient_id": "uuid",
      "name": "Chicken breast", "required_quantity": 300.0, "unit": "GRAM",
      "is_optional": false, "preparation_note": null
    }
  ]
}
```
**Không có** `cuisine`, `difficulty`, tách `prep_time`/`cook_time` (chỉ có 1 số `estimated_cooking_minutes`), và **không cross-reference kho** — không có `in_pantry`/`pantry_quantity` mỗi ingredient.

---

## 3. Recommendations — `POST /recommendations`

> **[MỚI — thay `/suggestions/dishes`]** BE hiện là **mock provider** (`analysis.is_mock: true`)

**Request:**
```json
{ "request": "Tôi muốn nấu món có ức gà, dưới 30 phút" }
```
Một chuỗi tự do duy nhất — **không có** field filter cấu trúc (`meal_type`, `max_time_min`...). BE tự diễn giải.

**Response 200:**
```json
{
  "request": "Tôi muốn nấu món có ức gà, dưới 30 phút",
  "analysis": { "intent": "string", "summary": "string", "is_mock": true },
  "items": [
    {
      "recipe_id": "uuid", "recipe_name": "Grilled chicken breast",
      "rank": 1, "score": 0.82,
      "score_components": {
        "expiration_utilization": 0.9, "availability": 0.8,
        "preference_fit": 0.7, "purchase_minimization": 0.6
      },
      "missing_ingredients": [
        { "master_ingredient_id": "uuid", "name": "Olive oil", "quantity": 15.0, "unit": "ML" }
      ],
      "near_expiry_ingredients": ["Chicken breast"],
      "explanation": "string",
      "provider": "string",
      "model_version": "string"
    }
  ]
}
```
`score_components` ↔ công thức PRD `0.4E + 0.3A + 0.2P + 0.1U`: `e=expiration_utilization`, `a=availability`, `p=preference_fit`, `u=purchase_minimization`. **Chỉ trả `recipe_id`+`recipe_name`, không nhúng recipe đầy đủ** — FE cần gọi thêm `GET /recipes/{recipe_id}` để lấy nutrition/instructions/ingredients cho card/detail.

Yêu cầu tối cao: vẫn thực hiện việc mock dữ liệu response trả về 
---

## 4. Cooking — `/cooking`

> **[CẬP NHẬT]** Thay cho `/dishes/{id}/cook`. Luồng 3 bước, **bắt buộc đi qua Meal Plan** — không có cách nấu trực tiếp 1 recipe mà không tạo meal-plan item trước.

```text
POST /cooking/preview                                  (auth) { meal_plan_item_id } -> xem trước, KHÔNG ghi dữ liệu
POST /cooking/sessions                                  (auth) { meal_plan_item_id } -> tạo session PLANNED (201) hoặc 409 nếu thiếu nguyên liệu
POST /cooking/sessions/{id}/complete                    (auth, Idempotency-Key header) { consumption_mode, consumptions? } -> hoàn tất, trừ kho
POST /cooking/sessions/{id}/leftovers                   (auth) { quantity, unit, storage_mode?, expires_at?, note? } -> tạo batch COOKED_FOOD (201)
GET  /cooking/history                                   (auth) -> danh sách session đã hoàn tất
GET  /cooking/history/{id}                              (auth) -> chi tiết 1 session
```

`consumption_mode` ∈ `EXACT|HALF|USE_ALL_MATCHED|CUSTOM`. `EXACT`/`HALF` không cần `consumptions`; `USE_ALL_MATCHED`/`CUSTOM` bắt buộc mảng `consumptions: [{ recipe_ingredient_id, inventory_batch_id, quantity? }]` (`quantity` bắt buộc khi `CUSTOM`).

**`preview` response** (đọc, không ghi):
```json
{
  "recipe_id": "uuid", "recipe_name": "string", "servings": 2.0,
  "scaled_ingredients": [{ "recipe_ingredient_id": "uuid", "master_ingredient_id": "uuid", "ingredient_name": "string", "required_quantity": 300.0, "unit": "GRAM" }],
  "proposed_deductions": [{ "recipe_ingredient_id": "uuid", "master_ingredient_id": "uuid", "batch_id": "uuid", "quantity": 300.0, "unit": "GRAM", "recipe_quantity": 300.0, "recipe_unit": "GRAM", "expires_at": "2026-09-10T00:00:00Z" }],
  "missing_ingredients": [{ "recipe_ingredient_id": "uuid", "master_ingredient_id": "uuid", "ingredient_name": "string", "missing_quantity": 50.0, "unit": "GRAM" }],
  "nutrition_estimate": { "calories": 330.0, "protein_g": 62.0, "fat_g": 7.2, "carbs_g": 0.0, "sugar_g": 0.0, "other_nutrients": {} },
  "warnings": [{ "code": "EXPIRED_BATCH_EXCLUDED|UNKNOWN_EXPIRATION_BATCH|INCOMPATIBLE_UNIT_BATCH", "message": "string", "batch_id": "uuid", "master_ingredient_id": "uuid" }]
}
```

**Vì `preview`/`sessions` chỉ nhận `meal_plan_item_id`, muốn "nấu ngay 1 recipe" từ màn Dish detail thì FE phải:** tạo (hoặc tái dùng) 1 meal plan → thêm recipe vào làm 1 item → lấy `meal_plan_item_id` đó → gọi `preview`/`sessions`. Không thể bỏ qua bước Meal Plan.

Mỗi meal-plan item chỉ được complete một lần: completion chuyển item từ `PLANNED` sang `COMPLETED` cùng transaction trừ kho. Item đã có cooking session hoặc đã `COMPLETED` không thể PATCH/DELETE (409); direct cooking vẫn không được hỗ trợ.

---

## 5. Meal Plans — `/meal-plans`

> **[CẬP NHẬT]** Không có khái niệm "tuần hiện tại" hay `PUT` cả plan. Mỗi plan có `id`, khoảng ngày tự chọn (`starts_on`/`ends_on`), và các item được thêm/sửa/xoá riêng lẻ.

```text
POST   /meal-plans                       (auth) { name?, starts_on, ends_on } -> plan rỗng (201)
GET    /meal-plans/                      (auth, ?limit=&offset=) -> danh sách plan (không kèm items)
GET    /meal-plans/{id}                  (auth) -> plan + items
POST   /meal-plans/{id}/items            (auth) { recipe_id, planned_for, meal_slot, servings, recommendation_run_id? } -> item (201)
PATCH  /meal-plans/{id}/items/{item_id}  (auth) { recipe_id?, planned_for?, meal_slot?, servings? } -> item
DELETE /meal-plans/{id}/items/{item_id}  (auth) -> 204
```

`meal_slot` ∈ `BREAKFAST|LUNCH|DINNER|SNACK` (**4 giá trị**, có thêm `SNACK` so với bản FE cũ 3 giá trị). Item:
```json
{ "id": "uuid", "recipe_id": "uuid", "recipe_name": "string", "recommendation_run_id": null, "planned_for": "2026-09-10", "meal_slot": "DINNER", "servings": 2.0, "status": "PLANNED" }
```
`status` ∈ `PLANNED|COMPLETED|SKIPPED`. Plan:
```json
{ "id": "uuid", "name": "string|null", "starts_on": "2026-09-08", "ends_on": "2026-09-14", "items": [...] }
```

**FE muốn hiển thị "thực đơn tuần" phải tự quản lý:** tạo 1 plan bao trọn tuần (`starts_on`=thứ 2, `ends_on`=chủ nhật), lưu `plan_id` cục bộ (hoặc gọi `GET /meal-plans/` để tìm plan có khoảng ngày trùng tuần đang xem), rồi thêm/sửa/xoá từng item.

---

## 6. Shopping Lists — `/shopping-lists`

> **[CẬP NHẬT]** **Không có** `GET /shopping-lists` (danh sách "hiện tại"). Chỉ có generate-từ-plan và đọc theo `id`. Mọi lệnh ghi cần header `Idempotency-Key`.

```text
POST   /shopping-lists/generate                (auth, Idempotency-Key) { meal_plan_id } -> ShoppingList (201)
GET    /shopping-lists/{list_id}                (auth) -> ShoppingList
POST   /shopping-lists/{list_id}/items          (auth, Idempotency-Key) { master_ingredient_id?|custom_name?, quantity, unit, estimated_cost? } -> item (201)
PATCH  /shopping-lists/{list_id}/items/{item_id} (auth, Idempotency-Key) { checked?, quantity?, estimated_cost?, purchase? } -> item
DELETE /shopping-lists/{list_id}/items/{item_id} (auth, Idempotency-Key) -> 204
```

**Check 1 item generated (tick "đã mua") bắt buộc gửi kèm `purchase`** — đây là bước tạo inventory batch thật:
```json
{ "checked": true, "purchase": { "storage_mode": "REFRIGERATED", "purchased_at": "2026-09-05T10:00:00Z", "expires_at": null, "unit_cost": 15000, "note": null } }
```
`purchase` **bắt buộc khi `checked: true`** trên item generated, **cấm** khi bỏ tick. Response item:
```json
{
  "id": "uuid", "master_ingredient_id": "uuid", "custom_name": null, "name": "Chicken breast",
  "required_quantity": 300.0, "available_quantity": 0.0, "missing_quantity": 300.0, "unit": "GRAM",
  "estimated_cost": 15000, "is_checked": false, "is_generated": true,
  "source_recipe_ids": ["uuid"], "inventory_batch_id": null
}
```
List: `{ "id", "meal_plan_id", "status": "ACTIVE|ARCHIVED", "generated_at", "items": [...] }`.

Shopping list đã generate là snapshot: hoàn tất meal-plan item không tự tính lại, xóa hoặc thay item trong ACTIVE list. Khi tạo list mới theo luồng hiện có, chỉ meal-plan item còn `PLANNED` mới đóng góp requirement.

**FE muốn màn "Danh sách mua sắm hiện tại" cần tự lưu `list_id` cục bộ** (từ response `generate`) — không có endpoint "lấy list đang active của tôi".

---

## 7. Inventory (Kho) — `/inventory`

> **[CẬP NHẬT — thay toàn bộ mục "Pantry" `/pantry/*` cũ]** Model theo **batch** (không phải 1 hàng phẳng mỗi nguyên liệu), có ledger bất biến. **Mọi lệnh ghi bắt buộc header `Idempotency-Key`.**

```text
POST   /inventory/batches                        (auth, Idempotency-Key) -> tạo batch (201)
GET    /inventory/batches                         (auth, ?status=&storage_mode=&master_ingredient_id=&page=&per_page=) -> danh sách
GET    /inventory/batches/{id}                    (auth) -> 1 batch
PATCH  /inventory/batches/{id}                     (auth, Idempotency-Key) -> sửa metadata (không đổi số lượng/định danh)
DELETE /inventory/batches/{id}                     (auth, Idempotency-Key, X-Reason header) -> archive (204)
POST   /inventory/batches/{id}/adjustments         (auth, Idempotency-Key) { event_type, quantity_delta?, reason } -> batch đã cập nhật
POST   /inventory/batches/{id}/consume             (auth, Idempotency-Key) { quantity, reason } -> batch đã cập nhật
POST   /inventory/batches/{id}/move                (auth, Idempotency-Key) { storage_mode, reason } -> batch đã cập nhật
GET    /inventory/summary                          (auth) -> gộp theo ingredient (không phải theo tầng bảo quản)
GET    /inventory/ledger                           (auth, ?batch_id=&event_type=&created_from=&created_to=&page=&per_page=) -> lịch sử ghi bất biến
```

**Tạo batch:**
```json
{
  "master_ingredient_id": "uuid",           // hoặc "custom_name": "string" — bắt buộc đúng 1 trong 2
  "quantity": 300.0, "unit": "GRAM",
  "storage_mode": "REFRIGERATED",           // ROOM_TEMPERATURE|REFRIGERATED|FROZEN|DRY_SHELF — KHÔNG phải storage_tier (fridge/freezer/pantry/immediate) của FE cũ
  "purchased_at": "2026-09-05T10:00:00Z", "packaged_at": null, "stored_at": null,
  "expires_at": "2026-09-10T00:00:00Z", "unit_cost": 15000, "note": null, "media_url": null
}
```
Mọi datetime **bắt buộc có timezone**. Response batch:
```json
{
  "id": "uuid", "master_ingredient_id": "uuid", "custom_name": null, "ingredient_name": "Chicken breast",
  "batch_type": "RAW_INGREDIENT", "initial_quantity": 300.0, "current_quantity": 300.0, "unit": "GRAM",
  "storage_mode": "REFRIGERATED", "status": "ACTIVE",
  "purchased_at": "...", "packaged_at": null, "stored_at": null, "expires_at": "...",
  "expiration_source": "MANUFACTURER", "freshness": "SAFE",
  "unit_cost": 15000, "note": null, "media_url": null,
  "source": "MANUAL", "source_cooking_session_id": null,
  "created_at": "...", "updated_at": "...", "archived_at": null
}
```
`batch_type` ∈ `RAW_INGREDIENT|COOKED_FOOD`. `status` ∈ `ACTIVE|DEPLETED|DISCARDED|ARCHIVED`. `expiration_source` ∈ `MANUFACTURER|ESTIMATED|USER_OVERRIDE|UNKNOWN`. `freshness` (tính lúc đọc) ∈ `EXPIRED|EXPIRING_SOON|SAFE|UNKNOWN`. `source` ∈ `MANUAL|LEFTOVER`.

**`GET /inventory/summary`** gộp theo `master_ingredient_id`/`custom_name`, **không có** tổng theo tầng bảo quản, không có "sắp hết hạn" / "kg tránh lãng phí" — FE tự tính từ danh sách batch nếu cần.

**Ledger entry:**
```json
{ "id": "uuid", "inventory_batch_id": "uuid", "event_type": "INITIAL_STOCK", "quantity_before": 0, "quantity_delta": 300.0, "quantity_after": 300.0, "unit": "GRAM", "cooking_session_id": null, "idempotency_key": "string|null", "reason": "string|null", "created_at": "..." }
```
`event_type` ∈ `INITIAL_STOCK|MANUAL_ADJUSTMENT|MANUAL_CONSUMPTION|COOKING_CONSUMPTION|DISCARDED|LEFTOVER_CREATED|CORRECTION|METADATA_UPDATED|MOVED|ARCHIVED`.

**Đối với "quét nhãn/hóa đơn → lưu vào kho":** không có endpoint "confirm hàng loạt" — FE gọi `POST /inventory/batches` từng dòng sau khi review kết quả `/extractions/*`.

---

## 8. Extractions (Quét OCR/ASR/Barcode) — `/extractions`

> **[CẬP NHẬT — thay mục "Multimodal Scan" `/scan/*` cũ]** Envelope chung, **`persisted` luôn `false`** — không endpoint nào ghi kho. `label`/`invoice`/`asr` là `multipart/form-data`; `barcode` là **query param**, không upload.

```text
POST /extractions/ocr/label     (auth) multipart file=<image> -> ExtractionResponse
POST /extractions/ocr/invoice   (auth) multipart file=<image> -> InvoiceExtractionResponse
POST /extractions/asr           (auth) multipart file=<audio> -> ExtractionResponse
POST /extractions/barcode?barcode=<string>  (auth, không upload) -> BarcodeExtractionResponse
```

**`ExtractionResponse`** (label + asr):
```json
{
  "request_id": "uuid", "status": "SUCCEEDED|FAILED|PARTIAL", "provider": "string", "raw_text": "string",
  "fields": { "ingredient_name": null, "quantity": null, "unit": null, "packaged_at": null, "expires_at": null, "price": null, "currency": null, "barcode": null },
  "confidence": { "ingredient_name": 0.9 }, "warnings": [], "persisted": false
}
```
**`InvoiceExtractionResponse.fields`:** `{ "line_items": [{ "name", "quantity", "unit", "unit_price", "total_price" }], "total_amount", "currency", "invoice_date", "vendor_name" }`.
**`BarcodeExtractionResponse.fields`:** `{ "barcode", "product_name", "brand", "category", "ingredient_name", "quantity", "unit", "expires_at", "price", "currency" }` — không tìm thấy vẫn trả `200` với field rỗng, **không phải `404`**.

---

## 9. Devices & Notifications

> **[CẬP NHẬT]** Path device đổi, `read: bool` đổi thành `status` 3 trạng thái.

```text
POST   /users/me/devices                (auth) { fcm_token, platform: "ANDROID"|"IOS"|"WEB" } -> { device_id, platform, is_enabled, last_seen_at } (201)
DELETE /users/me/devices/{device_id}    (auth) -> 204   // theo device_id trả về ở trên, KHÔNG theo token
GET    /notifications                   (auth, ?limit=&before=) -> { items: [...], next_before }
PATCH  /notifications/{notification_id} (auth) { status: "READ"|"DISMISSED" } -> notification
```

Notification item:
```json
{
  "notification_id": "uuid", "inventory_batch_id": "uuid|null",
  "type": "EXPIRING_SOON|EXPIRES_TODAY|EXPIRED|LEFTOVER_REMINDER",
  "title": "string", "body": "string", "payload": {},
  "status": "UNREAD|READ|DISMISSED", "delivery_status": "PENDING|SENT|RETRYING|FAILED",
  "scheduled_at": "...|null", "sent_at": "...|null", "created_at": "..."
}
```
Notification chỉ được BE tạo tự động bởi job quét hạn hàng ngày (`notification_worker`) — không có endpoint nào để FE tự tạo notification cho chính mình.

---

## 10. Reports — `/reports`

`GET /reports/waste-reduction?period=week|month|year` yêu cầu Bearer token. `period` mặc định là `month`; giá trị khác trả 422 error envelope chung. Endpoint trả số liệu thật từ evidence snapshot, không dùng mock hoặc suy ngược hạn dùng hiện tại từ inventory batch.

Metric `near-expiry-v1` là **ước tính khối lượng nguyên liệu thô đã được dùng khi sắp hết hạn**. Một event chỉ được cộng khi là `COOKING_CONSUMPTION` đã snapshot lúc completion, batch là `RAW_INGREDIENT`, hạn dùng đã biết, chưa qua ngày hết hạn theo `Asia/Ho_Chi_Minh`, nằm trong warning window và unit là `GRAM` hoặc `KG`. `GRAM` chia 1000; `KG` giữ nguyên. Không quy đổi `ML`, `LITER`, `PIECE`, `PACK` hoặc `OTHER` khi chưa có density/mass. Không cộng leftover cooked food, manual consumption, discard hoặc ledger event khác.

Thứ tự lý do loại là: `COOKED_FOOD` → `UNKNOWN_EXPIRATION` → `EXPIRED` → `OUTSIDE_WARNING_WINDOW` → `UNSUPPORTED_UNIT`. Evidence vẫn được ghi cho event bị loại để phân biệt với lịch sử chưa có evidence. `warning_days` là cấu hình inventory hiện hành tại lúc completion; ngày hết hạn trùng ngày local của completion vẫn chưa bị xem là expired.

Kỳ luôn là kỳ lịch hiện tại theo `Asia/Ho_Chi_Minh`: tuần bắt đầu thứ Hai, tháng từ ngày 1, năm từ 01/01. Khoảng query là nửa mở `[period_start, period_end)`, với `period_end` là thời điểm request. `weekly_series` gom theo các tuần thứ Hai giao với kỳ, gồm số 0 cho mọi tuần đã bắt đầu chưa có event; `weekly_labels` là ngày Thứ Hai tương ứng và có thể nằm trước ngày đầu tháng/năm. Mọi kilogram công khai làm tròn `ROUND_HALF_UP` đến 0,001 kg sau khi cộng tổng. `top_saved_ingredients` lấy tối đa 5 identity theo kg giảm dần, phá hòa ổn định theo identity và hiển thị tên snapshot mới nhất trong kỳ; `total_saved_kg` vẫn là tổng của mọi ingredient hợp lệ, không chỉ top 5.

```json
GET /reports/waste-reduction?period=month
-> {
     "total_saved_kg": "1.601",
     "period": "month",
     "weekly_series": ["1.601"],
     "top_saved_ingredients": [
       { "name": "Cà chua", "saved_kg": "1.5" },
       { "name": "Rau bina", "saved_kg": "0.101" }
     ],
     "weekly_labels": ["2026-08-31"],
     "period_start": "2026-09-01T00:00:00+07:00",
     "period_end": "2026-09-03T12:00:00+07:00",
     "timezone": "Asia/Ho_Chi_Minh",
     "coverage": {
       "data_from": "2026-09-01T08:00:00Z",
       "missing_evidence_count": 2,
       "unsupported_unit_count": 1
     }
   }
```

Các giá trị kg là Decimal, nên client phải chấp nhận JSON number hoặc string Decimal. `coverage.data_from` là `consumed_at` evidence v1 sớm nhất của user, hoặc `null` khi chưa có evidence. `missing_evidence_count` là số negative `COOKING_CONSUMPTION` của session completed trong kỳ chưa có evidence v1. `unsupported_unit_count` đếm mọi event v1 trong kỳ có `mass_kg=null`, kể cả khi một lý do loại có priority cao hơn unsupported unit.

Ví dụ tính tay với warning window 3 ngày:

- Không có evidence: tổng 0, top rỗng, series vẫn có 0 cho các tuần đã bắt đầu và `data_from=null`.
- Dùng 500 GRAM raw, hết hạn cùng ngày hoặc sau 2 ngày: eligible, đóng góp 0,5 kg.
- Dùng raw KG nhưng hạn dùng ở ngày local trước completion: `EXPIRED`, không đóng góp.
- Dùng raw KG không có hạn: `UNKNOWN_EXPIRATION`, không đóng góp.
- Dùng raw LITER trong warning window: `UNSUPPORTED_UNIT`, `mass_kg=null`, không đóng góp.
- Dùng cooked leftover, dù có/không có hạn hoặc unit không đổi được: `COOKED_FOOD`, không đóng góp.

FE tiếp tục giữ mock cho tới Checkpoint Phase 5: migration DB-02 phải được người phụ trách tạo và áp dụng, sau đó evidence writer/reader cần được kiểm chứng trên database test biệt lập.

## 11. Subscription — `/subscription` — **[MOCK ONLY, BE chưa có]**

```json
GET  /subscription -> { "plan": "free|premium", "expires_at": "string|null" }
POST /subscription/premium-interest -> { "registered": true }
```
MVP mở hết tính năng (không gating) — 2 endpoint trên chỉ phục vụ trang "quan tâm premium", không có logic thanh toán.

---

## Ghi chú cho Backend

| # | Endpoint / mục | Ghi chú |
|---|---|---|
| 2 | `GET /shopping-lists` (list-all) | FE cần 1 cách lấy "shopping list đang active của tôi" mà không phải tự nhớ `list_id` (ví dụ sau khi cài lại app / đổi máy). Đề xuất: thêm `GET /shopping-lists?status=ACTIVE` trả list mới nhất theo user, hoặc field `active_shopping_list_id` trong response `GET /meal-plans/{id}`. |
| 3 | `POST /cooking/sessions` yêu cầu `meal_plan_item_id` | Xác nhận đây là chủ đích sản phẩm (không "nấu nhanh" ngoài kế hoạch)? Nếu đúng, FE sẽ luôn tạo/dùng 1 meal-plan item ẩn khi user bấm "Đã nấu món này" từ màn Dish detail — xin BE xác nhận việc tự tạo meal-plan item kiểu này không vi phạm ràng buộc nghiệp vụ nào khác (ví dụ báo cáo/thống kê theo meal plan thật). |
| 4 | `PATCH /shopping-lists/{list}/items/{item}` khi check item generated | Yêu cầu object `purchase` đầy đủ ngay trong request check — FE cần 1 form nhập tối thiểu (storage_mode + hạn dùng) trước khi tick, sẽ tăng số bước thao tác. Có thể chấp nhận default `storage_mode` theo `default_storage_mode` của ingredient để giảm bước? |
| 5 | `GET /recommendations` không nhúng recipe | Với danh sách 3-5 gợi ý, FE phải gọi thêm N lần `GET /recipes/{id}` để hiện đủ thumbnail/thời gian nấu/dinh dưỡng. Cân nhắc BE nhúng thẳng 1 bản rút gọn recipe (name, media_url, estimated_cooking_minutes) trong mỗi `item` để tránh N+1? |
| 6 | Reports / Subscription | Chưa có endpoint — FE tiếp tục mock 2 mục này cho tới khi BE lên lịch (không chặn MVP theo PRD). |
| 7 | `POST /extractions/barcode` là query param | FE hiện gọi multipart cho 3 loại quét còn lại; xác nhận barcode luôn là query string (không upload ảnh mã vạch) để FE không thiết kế nhầm luồng nhập liệu. |
