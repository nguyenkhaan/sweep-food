# Feature: Nhập nguyên liệu → smart parser → hạn sử dụng (FreshCheck tùy chọn)

Luồng thêm nguyên liệu (nhập tay, OCR nhãn/hóa đơn, ASR) và cách một món có hạn sử dụng.

## 1. Nguyên tắc đã chốt

- **Smart parser chạy trước khi hiện cho người dùng.** OCR, ASR và nhập tay đều qua smart parser để chuẩn hóa tên và khớp `master_ingredient_id`. Response extraction chỉ trả trường cốt lõi; enrichment (nutrition, freshness_guide, ...) không trả ra.
- **Có đúng 3 cách để một món có hạn sử dụng:**
  1. OCR / ASR đọc được hạn (`expires_at`).
  2. Người dùng nhập tay.
  3. FreshCheck (trả lời dấu hiệu cảm quan).
- **Không tự đoán hạn.** FE không điền hạn theo `referenceShelfLifeDays` nữa; BE không còn ước lượng hạn theo luật shelf-life khi tạo batch. Thiếu cả 3 cách → món không có hạn (`expiration_source = UNKNOWN`).
- FreshCheck là **tùy chọn**, chỉ hiện khi món chưa có hạn và có `master_ingredient_id`. Nguyên liệu chưa có mapping FreshCheck → ẩn nút, không báo lỗi.

## 2. Contract BE

| Endpoint | Vai trò |
|---|---|
| `POST /extractions/text` `{ text }` | Chữ gõ tay → smart parser (tier từ điển/regex, không LLM) → cùng `ExtractionResponse` như label/ASR |
| `POST /extractions/ocr/label` | Một món: `ingredient_name`, `raw_name`, `master_ingredient_id`, `quantity`, `unit`, `packaged_at`, `expires_at` |
| `POST /extractions/ocr/invoice` | `line_items[]`: `name`, `raw_name`, `master_ingredient_id`, `quantity`, `unit`, `unit_price`, `total_price` (không có trường hạn) |
| `POST /extractions/asr` | Như label; không bao giờ có `expires_at` |
| `GET /freshness/questions?master_ingredient_id=` | Bộ câu hỏi dấu hiệu theo nguyên liệu |
| `POST /freshness/previews` | Xem trước hạn ước tính, **không ghi dữ liệu** |
| `POST /freshness/batches/{id}/assessment` | Chấm trên batch đã lưu, ghi hạn `ESTIMATED` + audit; không ghi đè hạn `MANUFACTURER`. Cần `purchased_at` (body hoặc batch) nếu batch chưa có `purchased_at`/`stored_at` |

`master_ingredient_id` được BE resolve từ mã catalog của AI qua `master_ingredients.source_code`; `null` nếu không khớp.

## 3. Luồng UX

```
Nhập tay: gõ tên → rời ô tên → POST /extractions/text → chuẩn hóa tên + master id (+ số lượng nếu text có)
OCR / ASR: smart parser đã chạy ở BE → màn review
   ├─ có hạn (OCR đọc được hoặc người dùng nhập)        → lưu
   └─ thiếu hạn → "Nhập hạn" | "Kiểm tra hạn nhanh" (nếu có master id + KB hỗ trợ)
        FreshCheck: GET questions → chọn dấu hiệu → POST previews → "Dùng hạn này"
        Lưu: POST /inventory/batches (KHÔNG gửi hạn của FreshCheck)
             → POST /freshness/batches/{id}/assessment với cùng answers (best-effort)
```

- Hạn từ FreshCheck **không** gửi trong `expires_at` lúc tạo batch (BE sẽ đánh dấu `MANUFACTURER` và các lần chấm sau bị bỏ qua). Hạn chỉ được ghi `ESTIMATED` qua assessment sau khi lưu.
- Assessment lỗi **không chặn** việc lưu: món vẫn vào kho, không có hạn.
- Hạn nhập tay và ước tính FreshCheck loại trừ nhau; đổi tên món hoặc đổi tầng bảo quản sẽ bỏ ước tính FreshCheck (và bỏ liên kết catalog khi đổi tên).
- Kết quả preview `blocked` (hỏng) không thể chấp nhận làm hạn.

## 4. Triển khai FE

- `ExpiryFreshnessRow` (`features/pantry/presentation/widgets/`): một widget dùng chung cho nhập tay, `label_review`, `voice_review`, `receipt_review` (mỗi dòng hóa đơn một widget).
- `FreshnessPreviewSheet`: hỏi dấu hiệu, gọi preview, trả `FreshnessEstimate` đã chấp nhận.
- `FreshnessEstimate` (domain) nằm trong `PantryItemDraft` / `ParsedItemDraft`; `PantryRepositoryImpl` gọi assessment sau `POST /inventory/batches`.
- `ParsedItemDraft.ingredientId` mang `master_ingredient_id` từ extraction tới body `POST /inventory/batches`.
- `FreshCheckSheet` ở màn chi tiết kho giờ gửi `purchased_at = item.addedAt`: trước đây request thiếu `purchased_at` nên BE trả `FRESHCHECK_ASSESSMENT_INPUT_INVALID` với batch tạo từ FE.

## 5. Giới hạn đã biết

- **Còn một nhánh BE ước lượng theo luật shelf-life:** đổi tầng bảo quản (`move_batch`) hoặc sửa mốc ngày của batch `ESTIMATED`/`UNKNOWN` vẫn gọi `_recalculate_estimated_expiration`. Nó có thể gán hạn theo luật seed cho batch `UNKNOWN`, hoặc thay ước tính FreshCheck bằng luật seed. Chưa đổi vì ngoài yêu cầu; cần quyết định riêng nếu muốn bỏ.
- `/extractions/text` chỉ trả món đầu tiên (kèm warning `ADDITIONAL_ITEMS_OMITTED` nếu nhập nhiều món).
- Nhập tay chỉ chạy smart parser khi rời ô tên và món chưa chọn từ gợi ý danh mục; không chạy khi sửa món đã lưu.
- Số lượng không có trong text → `quantity = null` (BE không điền số ước lượng); form giữ số người dùng đã nhập.
- Test FE `test/unit/reports/analytics_repository_test.dart` (3 test) fail vì `ReportRemoteDataSource.usageHistory` chủ động `throw UnsupportedError` (BE chưa có endpoint usage-history); test cũ không khớp code. Không liên quan thay đổi này, chưa sửa.

## 6. Kiểm chứng đã chạy

| Hạng mục | Kết quả |
|---|---|
| Backend `pytest src/test` | 510 passed, 21 skipped |
| FE `flutter analyze` | 3 issue có sẵn (directive ordering ở `dish_detail_screen.dart`, import thừa ở `recipe_image_test.dart`, warning analyzer plugin) |
| FE `flutter test test/unit test/widget` | 170 passed, 1 skipped, 3 failed (analytics, xem mục 5); các test mới đều pass |
| Luồng nhập tay → smart parser → FreshCheck → lưu → assessment | `test/widget/pantry/add_ingredient_freshcheck_flow_test.dart` (UI thật, chỉ giả HTTP client) |
| Chưa chạy | App trên thiết bị/emulator; test `test/live/*` (cần backend thật) |
