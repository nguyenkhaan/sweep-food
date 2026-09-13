Đã chốt được source release và contract chuẩn hóa. Tôi đề xuất output dùng **JSON Lines (`.jsonl`)**, không dùng `.py` và không dùng một JSON array lớn: mỗi dòng là một record, phù hợp batch import 62 nghìn recipe ingredient, dễ ghi rejection theo từng dòng và không phải nạp toàn bộ file vào bộ nhớ.

## 1. Input raw được dùng

Chỉ dùng sáu file sau:

| File | Vai trò | Count hiện tại |
|---|---|---:|
| `food_nutrition_raw.json` | Nutrition catalog + category | 853 food, 15 category |
| `canonical_recipes.json` | Recipe canonical | 5.479 |
| `canonical_recipe_ingredients.json` | Ingredient theo recipe canonical | 62.023 |
| `recipe_canonical_mapping.json` | Audit mapping raw → canonical | 5.641 mapping |
| `recipes.json` | `nutrition_status` | 5.641 |
| `recipes_raw_scraped.json` | Description, steps, media | 5.879 |

Các checksum source đã được ghi nhận để làm baseline release. Những file còn lại chỉ dùng audit, không được đọc để import nhằm tránh duplicate.

Kết quả audit quan trọng:

- 5.479 recipe canonical đều có `source_url`, UUID riêng và đều join được với scraped detail.
- 62.023 recipe ingredient đều thuộc một recipe canonical.
- 61.973 dòng có `estimated_weight_g > 0`; 19 dòng có quantity hợp lệ nhưng không có gram; 31 dòng không có quantity dùng được và phải vào rejection report.
- Không có dòng nào thiếu `cleaned_name`.
- Có 8.159 recipe ingredient không có `master_ingredient_code`/`master_ingredient_name`; chúng sẽ tạo master từ `cleaned_name` nếu tên hợp lệ.
- Có 1 recipe canonical thiếu instructions; output dùng `{"steps":[]}`.
- Có 397 description chỉ là hashtag; sẽ sinh description factual.
- Nutrition catalog có một cặp trùng tên/category: `Thịt trâu, đùi, tươi`; phải gộp thành một master.

## 2. Quy tắc normalize dùng chung

- Text: Unicode NFC, bỏ ký tự zero-width, trim, gộp nhiều khoảng trắng thành một.
- Natural key: dùng chuỗi sau normalize + `casefold()`; không bỏ dấu tiếng Việt để tránh gộp sai nguyên liệu.
- Tên master tự tạo: phải dài 2–120 ký tự, có chữ cái, không chỉ là số/đơn vị/quantity/chú thích như `vừa đủ`, `tùy thích`, `gia vị`.
- URL: trim, bỏ fragment `#...`, lowercase scheme/host; giữ nguyên path và query. Dùng URL đã chuẩn hóa để join recipe với scraped detail.
- Decimal: parse bằng `Decimal`, không qua float; servings làm tròn 2 chữ số, nutrition/quantity 3 chữ số; output dưới dạng string như `"10.000"`.
- UUID:
  - Giữ nguyên UUID của canonical recipe và canonical recipe ingredient.
  - Category/master dùng UUIDv5 với namespace cố định và normalized natural key.
  - `master_ingredient_code` chỉ là khóa join nội bộ, tuyệt đối không xuất hiện trong output.
- Master tự tạo hợp lệ có `is_verified=true`; không đủ điều kiện thì reject riêng recipe ingredient, không loại recipe.

## 3. Format output đã chốt

```text
data/normalized/
├── ingredient_categories.jsonl
├── master_ingredients.jsonl
├── recipes.jsonl
├── recipe_ingredients.jsonl
├── rejected_records.jsonl
└── manifest.json
```

- Bốn file `.jsonl` đầu: mỗi dòng là một object đúng cấu trúc một record của bảng DB tương ứng.
- `rejected_records.jsonl`: mỗi dòng là lỗi một record, gồm `entity`, `source_id`, `reason`, `details`.
- `manifest.json`: một JSON object chứa `schema_version`, checksum input/output, timestamp và counts.
- File được sort theo `id`, key theo thứ tự cố định, UTF-8, newline cuối file để cùng raw input luôn cho output xác định.

Ví dụ `recipe_ingredients.jsonl`:

```json
{"id":"7af23757-8525-4c03-b0d5-ebb52b4161a8","recipe_id":"000f5f77-b69f-47f9-90a3-a0ca3b57d86f","master_ingredient_id":"8de83c62-2f87-4aae-b43d-c8b60f5e61da","required_quantity":"10.000","unit":"GRAM","display_quantity":"2.000","display_unit":"muỗng cà phê","is_optional":false,"preparation_note":"băm"}
```

Bước kế tiếp là triển khai `transform` theo contract này, bắt đầu từ category và master ingredient để có đầy đủ khóa ngoại trước khi sinh `recipe_ingredients`.