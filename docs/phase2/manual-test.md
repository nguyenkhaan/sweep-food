# Phase 2 — Manual Test Checklist

---

## Migration Phase 2

API: N/A — Alembic revision `9988f9aa15b0`

Mô tả: Tạo schema cho replay Shopping, Reports evidence và Premium Interest.

Yêu cầu đầu ra:

- Chạy trên database test riêng, không dùng database ứng dụng.
- Có đúng một Alembic head và revision hiện tại tạo đủ ba bảng Phase 2.
- Upgrade không DROP/TRUNCATE/backfill dữ liệu cũ.
- Có các bảng `shopping_mutation_receipts`, `waste_reduction_events`, `premium_interests`; các bảng mới ban đầu rỗng.

---

## Khôi phục Shopping List và retry mutation

API: `GET /api/shopping-lists`, `POST /api/shopping-lists/generate`, `POST /api/shopping-lists/{list_id}/items`, `PATCH|DELETE /api/shopping-lists/{list_id}/items/{item_id}`

Mô tả: Lấy lại list khi đổi thiết bị, mua item với default storage và chống tạo dữ liệu trùng khi retry.

Yêu cầu đầu ra:

- GET chỉ trả list của Bearer user, filter/status/pagination và thứ tự mới nhất đúng.
- Purchase không gửi `storage_mode` chỉ thành công khi catalog có default; không có default trả 422.
- Retry cùng `Idempotency-Key` và payload trả snapshot cũ, không thêm item/batch/ledger.
- Cùng key nhưng payload khác trả 409; retry DELETE vẫn trả 204.

---

## Vòng đời Meal Plan khi nấu

API: `POST /api/cooking/sessions`, `POST /api/cooking/sessions/{session_id}/complete`, `PATCH|DELETE /api/meal-plans/{plan_id}/items/{item_id}`

Mô tả: Một meal-plan item chỉ được hoàn tất một lần và các thay đổi liên quan commit cùng transaction.

Yêu cầu đầu ra:

- Complete session đánh dấu item `COMPLETED`, trừ kho và tạo consumption/ledger cùng lúc.
- Retry completion cùng key trả kết quả cũ; session khác của item đã completed trả 409, không trừ kho thêm.
- PATCH/DELETE item đã được session tham chiếu trả 409.
- Shopping list ACTIVE đã generate giữ snapshot cũ sau khi item completed.

---

## Reports Waste Reduction

API: `GET /api/reports/waste-reduction?period=week|month|year`

Mô tả: Báo cáo khối lượng nguyên liệu thô sắp hết hạn đã dùng, dựa trên evidence lúc complete cooking.

Yêu cầu đầu ra:

- Không có evidence trả 200, total `0`, series có giá trị `0` và coverage rõ ràng.
- Dùng raw `500 GRAM` trong warning window tạo evidence eligible `0.5 kg`; raw expired, unknown expiry, cooked leftover hoặc LITER không được cộng.
- `period` sai trả 422; không có Bearer trả 401; user khác không thấy dữ liệu.
- Kiểm tra `weekly_labels`, Asia/Ho_Chi_Minh, top 5, `missing_evidence_count` và `unsupported_unit_count` đúng evidence đã tạo.

---

## Premium Interest

API: `GET /api/subscription`, `POST /api/subscription/premium-interest`

Mô tả: Ghi một lần đăng ký quan tâm Premium, không thay đổi quyền sử dụng MVP.

Yêu cầu đầu ra:

- GET luôn trả `{ "plan": "free", "expires_at": null }`.
- POST không cần business body, trả 200 `{ "registered": true }` sau commit.
- POST hai lần hoặc đồng thời cho cùng user chỉ có một row và giữ `registered_at` đầu tiên.
- User khác có row riêng; `role` và `preferences` không bị thay đổi.

---

## Mismatch API đã chỉnh sửa

API: `POST /api/extractions/ocr/label`, `POST /api/extractions/ocr/invoice`, `POST /api/extractions/asr`, `POST /api/extractions/barcode`, `POST /api/users/me/devices`, `GET /api/meal-plans/`, `POST /api/recommendations`

Mô tả: Kiểm tra các thay đổi contract của extraction, device, meal-plan và recommendation mock.

Yêu cầu đầu ra:

- Extraction MIME/size/file sai trả 422 envelope có `status_code`, `detail`, `path`; barcode không tìm thấy không ghi kho.
- Đăng ký device trả 201 và không lộ FCM token.
- GET meal plans trả array có timestamp, thứ tự ổn định và không lộ plan user khác.
- Recommendation vẫn là mock, có `recipe_summary` đủ dữ liệu card và không ghi recommendation run/kho.
