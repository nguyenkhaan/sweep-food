# Kế hoạch chuẩn hóa và import dữ liệu catalog

## 1. Mục tiêu

Xây dựng một pipeline có thể chạy lặp lại để:

1. Đồng bộ schema database với dữ liệu sản phẩm cần giữ lại.
2. Đọc dữ liệu nguồn trong `data/raw/` mà không sửa file gốc.
3. Sinh bốn file JSON chuẩn hóa, sẵn sàng import vào bốn bảng:
   - `ingredient_categories`
   - `master_ingredients`
   - `recipes`
   - `recipe_ingredients`
4. Import dữ liệu theo batch, có dry-run, transaction, upsert và báo cáo lỗi.
5. Ưu tiên độ phủ: import toàn bộ recipe; nếu một recipe ingredient không thể chuẩn hóa thì chỉ bỏ dòng đó, không bỏ cả recipe.
6. Bảo đảm không tạo khóa ngoại mồ côi và không đưa các trường trung gian của crawler vào database.

`ingredient_aliases` không thuộc phạm vi đợt import này. `cleaned_name` vẫn được dùng trong quá trình ánh xạ/tạo master ingredient nhưng không được lưu vào bốn bảng đích.

## 2. Phạm vi và số lượng dự kiến

Baseline hiện tại:

| Dữ liệu | Số lượng dự kiến |
|---|---:|
| Ingredient categories | 16 |
| Master ingredients | 6.494 |
| Recipes | 5.479 |
| Recipe ingredients | 61.992 |
| Recipe ingredients bị loại vì không có quantity dùng được | 31 |

Chi tiết master ingredient:

| Nguồn | Số lượng sau gộp |
|---|---:|
| Nutrition catalog | 852 |
| Có mã/tên ổn định nhưng không có nutrition catalog | 99 |
| Sinh từ `cleaned_name` chưa xác định được master | 5.543 |
| Tổng | 6.494 |

Các số trên là acceptance baseline của bộ raw hiện tại. Mỗi lần nguồn thay đổi, `manifest.json` và báo cáo validation là kết quả chính thức.

## 3. Các quyết định dữ liệu

### 3.1. Chính sách độ phủ

- Import cả 5.479 recipe canonical.
- Không loại recipe chỉ vì thiếu một số recipe ingredient.
- Tạo master ingredient mới từ `cleaned_name` khi không tìm được master có sẵn.
- Master được sinh tự động thuộc category `Chưa phân loại` khi chưa xác định được category phù hợp và có `is_verified = true` sau khi vượt qua toàn bộ quy tắc validation tên.
- Nutrition được phép `null`.
- Recipe thiếu instructions vẫn được import với `{"steps": []}` và dùng `source_url` làm fallback.
- Chỉ loại recipe ingredient khi không có cả trọng lượng chuẩn hóa lẫn quantity gốc hợp lệ.

### 3.2. Chính sách khóa ngoại

Không bao giờ insert một `recipe_ingredients.master_ingredient_id` chưa tồn tại.

```text
Đã có master
→ dùng UUID hiện có

Chưa có master nhưng có cleaned_name
→ tạo master "Chưa phân loại"
→ lấy UUID mới
→ tạo recipe ingredient

Không tạo được master hoặc không có quantity
→ ghi rejection
→ bỏ riêng recipe ingredient
```

### 3.3. Vai trò của `master_ingredient_code`

`master_ingredient_code` là khóa nối tạm thời giữa các file raw, không phải trường database.

```text
source code
→ xác định master ingredient
→ sinh/tra master UUID
→ thay code bằng master_ingredient_id
→ không ghi code vào output hoặc database
```

### 3.4. Tính xác định của ID

- Giữ nguyên UUID của recipe canonical.
- Giữ nguyên UUID của canonical recipe ingredient.
- Category và master ingredient dùng UUID sinh xác định từ một namespace cố định của pipeline.
- Với catalog/coded master, code chỉ được dùng làm seed nội bộ để sinh UUID; code không xuất hiện trong output.
- Với derived master, UUID được sinh từ `normalized cleaned_name`.
- Output được sort theo `id` để cùng một input luôn sinh cùng một output.
- Nếu hai source identity gộp vào cùng natural key, chọn một UUID canonical và remap tất cả tham chiếu về UUID đó.

## 4. Nguồn dữ liệu

### 4.1. File được sử dụng

| File | Vai trò |
|---|---|
| `data/raw/food_nutrition_raw.json` | Nutrition catalog và 15 category nguồn |
| `data/raw/recipes/canonical_recipes.json` | 5.479 recipe canonical |
| `data/raw/recipes/canonical_recipe_ingredients.json` | 62.023 recipe ingredient đã remap về canonical recipe |
| `data/raw/recipes/recipe_canonical_mapping.json` | Kiểm tra mapping 5.641 recipe nguồn sang 5.479 recipe canonical |
| `data/raw/recipes/recipes.json` | `nutrition_status` của recipe được chọn |
| `data/raw/recipes_raw_scraped.json` | Description, instructions, media và source metadata |
| `data/raw/qwen_extracted_map.json` | Quyết định reviewed `raw_text` → extracted ingredient cho các dòng `QWEN_LLM_MATCH` |

### 4.2. File chỉ dùng để audit, không import

- `data/raw/recipe_ingredients.json`
- `data/raw/recipes/recipe_ingredients.json`
- `data/raw/recipes_crawled_cleaned.json`
- `data/raw/recipes/recipe_name_alias_decisions.json`
- `data/raw/recipes/recipe_canonicalization_summary.json`

Không đọc đồng thời file ingredient gốc và `canonical_recipe_ingredients.json` để tránh import trùng.

## 5. Kế hoạch thực hiện

| Phase | Công việc | Output | Điều kiện hoàn thành |
|---|---|---|---|
| 0 | Xác nhận Alembic baseline/head và database test | Migration tree hợp lệ | Không còn missing revision; target là DB test |
| 1 | Cập nhật model và migration | Schema bốn bảng đã chốt | Upgrade/downgrade chạy được trên DB test |
| 2 | Viết transformer | Bốn JSON normalized + rejections + manifest | Cùng input sinh cùng checksum |
| 3 | Viết validator | Báo cáo lỗi đầy đủ | Không có FK mồ côi, ID trùng, quantity sai |
| 4 | Viết batch importer | CLI `load --dry-run` và `load` | Chạy lại không sinh bản ghi trùng |
| 5 | Kiểm thử trên DB biệt lập | Báo cáo post-import | Count đúng baseline, toàn vẹn dữ liệu đạt |
| 6 | Import môi trường đích | Catalog release được ghi nhận | Có manifest, log tổng hợp và phương án rollback |

## 6. Phase 0 — Xác nhận Alembic baseline

Trước khi tạo migration mới:

1. Kiểm tra `src/backend/alembic/versions/` và revision đang được database ghi nhận.
2. Không autogenerate khi migration tree đang thiếu revision cha.
3. Không dùng `stamp` để bỏ qua migration nếu chưa đối chiếu schema thật.
4. Chỉ thử migration trên database/branch test biệt lập.
5. Không in `DATABASE_URL` ra terminal hoặc log.

Lệnh kiểm tra, chạy từ `src/backend/`:

```bash
uv run alembic heads
uv run alembic current
uv run alembic history
```

## 7. Phase 1 — Chỉnh sửa database

### 7.1. `ingredient_categories`

Không cần thêm cột.

Giữ:

```text
id
name
description
created_at
updated_at
```

### 7.2. `master_ingredients`

Thay đổi:

| Thay đổi | Kiểu | Mục đích |
|---|---|---|
| `description` chuyển thành nullable | `VARCHAR NULL` | Raw data không có mô tả cho mọi master |
| Thêm `is_verified` | `BOOLEAN NOT NULL DEFAULT true` | Đánh dấu master đã vượt qua validation của pipeline và được phép sử dụng |

Không thêm `code`, `cleaned_name`, `match_method` hoặc `match_confidence`.

### 7.3. `recipes`

Thêm:

| Cột | Kiểu | Ràng buộc |
|---|---|---|
| `source_platform` | `VARCHAR(50)` | `NOT NULL` sau backfill |
| `source_url` | `VARCHAR` | `NOT NULL`, unique |
| `nutrition_status` | `VARCHAR(20)` | `NOT NULL`, `COMPLETE\|PARTIAL\|INCOMPLETE` |

Index/constraint:

- Unique index `uq_recipes_source_url`.
- Check constraint cho `nutrition_status`.

Không thêm `ingredients_count`; số ingredient đã import được tính từ quan hệ. Số ingredient bị loại nằm trong manifest/rejection report.

### 7.4. `recipe_ingredients`

Giữ `required_quantity` và `unit` làm giá trị chuẩn hóa dùng cho inventory/cooking.

Thêm:

| Cột | Kiểu | Ràng buộc |
|---|---|---|
| `display_quantity` | `NUMERIC(12,3)` | nullable, dương nếu có |
| `display_unit` | `VARCHAR(50)` | nullable |

Không thêm `raw_text`, `cleaned_name`, `master_ingredient_code`, nutrition theo dòng hoặc matching metadata.

### 7.5. Trình tự migration

1. Sửa SQLAlchemy models.
2. Tạo revision mới sau khi Alembic baseline hợp lệ.
3. Đọc và sửa migration được autogenerate; không chạy mù.
4. Với database đã có dữ liệu, thêm cột nullable/default trước, backfill, sau đó mới siết `NOT NULL`/unique.
5. Kiểm tra upgrade và downgrade trên DB test.

Lệnh dự kiến:

```bash
cd src/backend
uv run alembic revision --autogenerate -m "prepare catalog data import"
uv run alembic upgrade head
```

Không chạy hai lệnh trên môi trường dùng chung trước khi migration được review.

## 8. Phase 2 — Cấu trúc output

```text
data/normalized/
├── ingredient_categories.json
├── master_ingredients.json
├── recipes.json
├── recipe_ingredients.json
├── rejected_records.json
└── manifest.json
```

Bốn file đầu tương ứng một-một với bốn bảng đích. Hai file cuối là báo cáo, không import.

### 8.1. `ingredient_categories.json`

Một phần tử:

```json
{
  "id": "9340576b-4ccc-4ac5-999f-441c359d9f67",
  "name": "Thủy sản và sản phẩm chế biến",
  "description": null
}
```

Quy tắc:

- Lấy distinct category từ nutrition catalog.
- Chuẩn hóa Unicode NFC và khoảng trắng.
- Gộp theo `lower(name)`.
- Thêm category `Chưa phân loại`.
- Kỳ vọng 16 dòng.

### 8.2. `master_ingredients.json`

Một phần tử verified:

```json
{
  "id": "8de83c62-2f87-4aae-b43d-c8b60f5e61da",
  "name": "Tôm biển",
  "description": null,
  "category_id": "9340576b-4ccc-4ac5-999f-441c359d9f67",
  "default_media_url": null,
  "canonical_unit": "GRAM",
  "calories": "82.000",
  "protein_g": "17.600",
  "fat_g": "0.900",
  "carbs_g": "0.900",
  "sugar_g": null,
  "sodium_mg": null,
  "other_nutrients": {},
  "default_storage_mode": null,
  "is_verified": true
}
```

Một phần tử derived:

```json
{
  "id": "7db2341a-35f2-52de-b5f1-60daafe84130",
  "name": "Giò sống",
  "description": null,
  "category_id": "4fbec67f-a08e-5ddd-b636-d0c57d855f94",
  "default_media_url": null,
  "canonical_unit": "GRAM",
  "calories": null,
  "protein_g": null,
  "fat_g": null,
  "carbs_g": null,
  "sugar_g": null,
  "sodium_mg": null,
  "other_nutrients": {},
  "default_storage_mode": null,
  "is_verified": true
}
```

Quy tắc tạo master:

1. Nutrition catalog:
   - Tên từ `name_vi`.
   - Category từ catalog.
   - Nutrition được map về các cột chuẩn; các chất còn lại vào `other_nutrients`.
   - `is_verified = true`.
2. Có source code/name nhưng không có nutrition catalog:
   - Giữ canonical name đã làm sạch.
   - Category `Chưa phân loại`.
   - Nutrition `null`.
   - `is_verified = true` sau khi tên vượt qua validation.
3. Không có master tương ứng:
   - Dùng `cleaned_name` sau normalize làm `name`.
   - Category `Chưa phân loại`.
   - Nutrition `null`.
   - `is_verified = true` sau khi tên vượt qua validation.
4. Một tên chỉ được dùng để tạo master tự động khi:
   - Đã chuẩn hóa Unicode NFC, trim và gộp khoảng trắng.
   - Dài từ 2 đến 120 ký tự và chứa ít nhất một chữ cái.
   - Không chỉ gồm số, quantity, đơn vị đo hoặc dấu câu.
   - Không phải placeholder như `vừa đủ`, `tùy thích`, `để trang trí` hoặc `nguyên liệu`; tên nhóm có code và nutrition catalog, ví dụ `Gia vị`, vẫn được giữ.
   - Không chứa instruction thay cho tên nguyên liệu.
5. Trước khi tạo mới, tra cứu theo normalized name và alias đã xác định. Không tạo master thứ hai nếu đã có natural key tương ứng.
6. Không tự suy đoán một master cụ thể bằng substring khi có nhiều khả năng; giữ tên sạch làm master riêng hợp lệ để tránh nối sai.
7. Giữ chính tả tiếng Việt của nguồn, chỉ viết hoa ký tự đầu; không tự đổi sang một nguyên liệu khác khi không có mapping chắc chắn.
8. Master không vượt qua các điều kiện trên không được tạo; recipe ingredient tương ứng được ghi vào rejection report, không làm mất recipe.
9. Gộp theo `(category_id, lower(name))` để khớp unique constraint database.
10. Khi coded master và derived master trùng natural key, ưu tiên coded master.
11. Gộp hai bản ghi nutrition `Thịt trâu, đùi, tươi` và ánh xạ cả hai source identity về một UUID.
12. Kỳ vọng 6.494 dòng; transformer phải báo chênh lệch nếu quy tắc validation làm thay đổi baseline.

### 8.3. `recipes.json`

Một phần tử:

```json
{
  "id": "000f5f77-b69f-47f9-90a3-a0ca3b57d86f",
  "name": "Nấm bào ngư kho tiêu",
  "description": "Món chính chế biến theo phương pháp kho, phù hợp cho 2 khẩu phần.",
  "instructions": {
    "steps": [
      {
        "step_number": 1,
        "title": "Bước 1",
        "content": "Nội dung hướng dẫn"
      }
    ]
  },
  "media_url": null,
  "source_platform": "dienmayxanh",
  "source_url": "https://www.dienmayxanh.com/vao-bep/...",
  "default_servings": "2.00",
  "estimated_cooking_minutes": 40,
  "estimated_cost": null,
  "total_calories": "248.700",
  "total_protein_g": "10.600",
  "total_fat_g": "16.200",
  "total_carbs_g": "21.300",
  "total_sugar_g": null,
  "other_nutrients": {},
  "nutrition_status": "COMPLETE",
  "tags": {
    "cooking_method": "Kho",
    "dish_type": "Món chính",
    "diet": ["Ăn chay", "Món cơm gia đình"]
  }
}
```

Quy tắc:

- Join canonical recipe với scraped detail bằng exact normalized `source_url`.
- Giữ UUID canonical.
- `description` lấy từ scraped detail.
- Nếu description rỗng hoặc chỉ gồm hashtag, tạo mô tả factual từ `name`, `dish_type`, `cooking_method` và `default_servings`.
- Chuyển instructions array thành `{"steps": [...]}`.
- Recipe duy nhất thiếu instructions dùng `{"steps": []}`.
- Parse `diet_tags` theo dấu `;`, trim và loại chuỗi rỗng.
- `nutrition_status` lấy từ `data/raw/recipes/recipes.json` theo selected canonical ID.
- Giữ numeric hợp lệ; giá trị thiếu/không hợp lệ thành `null` nếu schema cho phép.
- Không mang metadata canonicalization/selection sang output.
- Kỳ vọng 5.479 dòng.

### 8.4. `recipe_ingredients.json`

Một phần tử:

```json
{
  "id": "7af23757-8525-4c03-b0d5-ebb52b4161a8",
  "recipe_id": "000f5f77-b69f-47f9-90a3-a0ca3b57d86f",
  "master_ingredient_id": "8de83c62-2f87-4aae-b43d-c8b60f5e61da",
  "required_quantity": "10.000",
  "unit": "GRAM",
  "display_quantity": "2.000",
  "display_unit": "muỗng cà phê",
  "is_optional": false,
  "preparation_note": "băm"
}
```

Quy tắc master FK:

1. Có master source identity: map sang UUID đã sinh.
2. Thiếu code: map bằng alias duy nhất từ `cleaned_name` nếu có.
3. Vẫn thiếu: map theo tên duy nhất hoặc master derived `Chưa phân loại` đã được sinh ở phase `master_ingredients`.
4. Không tạo master ở phase này; master thiếu hoặc mơ hồ được ghi rejection. Không bao giờ để `master_ingredient_id = null`.
5. Dòng `QWEN_LLM_MATCH` chỉ dùng tên trong `qwen_extracted_map.json`, bỏ hoàn toàn code/name do crawler từng gán. Giá trị `không có nguyên liệu cụ thể` được ghi `QWEN_NO_INGREDIENT`.

Quy tắc quantity:

1. `estimated_weight_g > 0`:
   - `required_quantity = estimated_weight_g`
   - `unit = GRAM`
2. Không có weight nhưng quantity gốc dương:
   - Giữ `GRAM`, `KG`, `PIECE`, `OTHER` nếu đã hợp lệ.
   - Map `LAT_MIENG` thành `OTHER`.
3. Không có cả weight và quantity gốc dương:
   - Không import dòng.
   - Ghi `MISSING_USABLE_QUANTITY` vào rejection report.
4. Quantity/unit gốc được giữ ở `display_quantity` và `display_unit` khi có.
5. Chuỗi rỗng của `preparation_note` thành `null`.
6. `is_optional = false` vì raw data chưa có tín hiệu đáng tin cậy.
7. Số dòng import chính thức là số dòng source trừ rejection của lần chạy; các dòng không có quantity dùng được và Qwen reviewed không phải nguyên liệu đều bị loại riêng, không làm mất recipe.

## 9. Phase 3 — Rejection report và manifest

### 9.1. `rejected_records.json`

Mỗi lỗi phải có cấu trúc máy đọc được:

```json
{
  "entity": "recipe_ingredient",
  "source_id": "source-row-uuid",
  "reason": "MISSING_USABLE_QUANTITY",
  "details": {
    "raw_text": "nguyên liệu vừa đủ"
  }
}
```

Reason code tối thiểu:

- `INVALID_UUID`
- `DUPLICATE_ID`
- `MISSING_RECIPE`
- `MISSING_MASTER_NAME`
- `AMBIGUOUS_MASTER`
- `MISSING_USABLE_QUANTITY`
- `INVALID_NUMERIC`
- `INVALID_UNIT`
- `DUPLICATE_SOURCE_URL`
- `MISSING_REQUIRED_FIELD`

Không ghi stack trace, credential hoặc database URL vào file này.

### 9.2. `manifest.json`

```json
{
  "schema_version": 1,
  "generated_at": "2026-09-13T00:00:00Z",
  "source_checksums": {},
  "output_checksums": {},
  "counts": {
    "ingredient_categories": 16,
    "master_ingredients": 6494,
    "recipes": 5479,
    "recipe_ingredients": 61992,
    "rejected_records": 31
  }
}
```

`generated_at` không được tham gia vào nội dung dùng để kiểm tra tính xác định của bốn output chính.

## 10. Phase 4 — Validation

Transformer kết thúc với exit code khác 0 nếu vi phạm lỗi cấu trúc. Record-level issue được đưa vào rejection nếu policy cho phép bỏ riêng record.

Validation bắt buộc:

### Cấu trúc

- Tất cả output là JSON array hợp lệ.
- Không có unknown field so với contract.
- Numeric dùng chuỗi decimal chuẩn hoặc `null`, không dùng `NaN`/`Infinity`.
- UUID hợp lệ.
- Enum hợp lệ.

### Uniqueness

- Category `lower(name)` duy nhất.
- Master `(category_id, lower(name))` duy nhất.
- Recipe `id`, `lower(name)` và `source_url` duy nhất.
- Recipe ingredient `id` duy nhất.

### Referential integrity

- Mọi `master_ingredients.category_id` tồn tại.
- Mọi `recipe_ingredients.recipe_id` tồn tại.
- Mọi `recipe_ingredients.master_ingredient_id` tồn tại.
- Không có `master_ingredient_code` trong bất kỳ output nào.

### Giá trị

- `default_servings > 0`.
- `estimated_cooking_minutes >= 0`.
- `required_quantity > 0`.
- `display_quantity` phải dương nếu không null.
- Nutrition không âm nếu có.
- Mọi master ingredient output đều có `is_verified = true`.
- `instructions` luôn có key `steps` và `steps` là array.

### Độ phủ

- 5.479 canonical recipe đều xuất hiện trong output.
- Recipe bị mất ingredient vẫn được import; số mất phải xuất hiện trong manifest/rejection.
- Baseline hiện tại kỳ vọng 31 recipe ingredient bị loại, không được thất thoát âm thầm.

## 11. Phase 5 — CLI pipeline

Mỗi phase transform có script riêng để dễ theo dõi. Không thêm framework ETL hoặc dependency mới.

Hai script đã có, chạy từ `src/backend/`:

```bash
# 1. Sinh ingredient_categories.json
uv run python scripts/ingredient_category_import.py

# 2. Sinh master_ingredients.json; bắt buộc dùng category output và Qwen reviewed map
uv run python scripts/master_ingredient_import.py \
  --categories-input ../../data/normalized/ingredient_categories.json \
  --qwen-map-input ../../data/raw/qwen_extracted_map.json

# 3. Sinh recipes.json từ canonical recipe, nutrition status và scraped detail
uv run python scripts/recipe_import.py

# 4. Sinh recipe_ingredients.json và rejected_records.json; chỉ dùng master đã sinh ở bước 2
uv run python scripts/recipe_ingredient_import.py \
  --recipes-input ../../data/normalized/recipes.json \
  --masters-input ../../data/normalized/master_ingredients.json \
  --categories-input ../../data/normalized/ingredient_categories.json \
  --qwen-map-input ../../data/raw/qwen_extracted_map.json
```

Các phase `validate` và `load` sẽ có script riêng khi được triển khai. Script import database chỉ đọc output normalized, không nhận credential trực tiếp trên command line.

## 12. Phase 6 — Cách nạp dữ liệu

Thứ tự bắt buộc:

```text
ingredient_categories
→ master_ingredients
→ recipes
→ recipe_ingredients
```

Yêu cầu loader:

- Validate toàn bộ output trước khi bắt đầu ghi.
- Dùng một transaction cho một catalog release.
- Ghi theo batch 500–1.000 dòng.
- Upsert, không insert mù.
- Flush category/master trước khi tạo FK phụ thuộc.
- `--dry-run` chạy cùng code path nhưng rollback trước commit.
- Không tự động xóa record database không còn xuất hiện trong release mới.
- Chạy lại cùng release phải cho `created = 0` và không tạo duplicate.

Conflict target:

| Bảng | Khóa upsert |
|---|---|
| `ingredient_categories` | `lower(name)` |
| `master_ingredients` | `(category_id, lower(name))` |
| `recipes` | `id`; xác nhận `source_url` không thuộc recipe khác |
| `recipe_ingredients` | `id` |

## 13. Post-import audit

Chạy sau dry-run và sau import thật:

```sql
SELECT count(*) FROM ingredient_categories;
SELECT count(*) FROM master_ingredients;
SELECT count(*) FROM recipes;
SELECT count(*) FROM recipe_ingredients;

SELECT count(*)
FROM master_ingredients mi
LEFT JOIN ingredient_categories ic ON ic.id = mi.category_id
WHERE ic.id IS NULL;

SELECT count(*)
FROM recipe_ingredients ri
LEFT JOIN recipes r ON r.id = ri.recipe_id
LEFT JOIN master_ingredients mi ON mi.id = ri.master_ingredient_id
WHERE r.id IS NULL OR mi.id IS NULL;

SELECT count(*)
FROM recipe_ingredients
WHERE required_quantity <= 0;

SELECT source_url, count(*)
FROM recipes
GROUP BY source_url
HAVING count(*) > 1;
```

Ba truy vấn lỗi cuối phải trả về 0 dòng hoặc count bằng 0.

## 14. Kiểm thử

Tạo test tối thiểu tại:

```text
src/backend/src/test/test_ingredient_category_import.py
src/backend/src/test/test_master_ingredient_import.py
src/backend/src/test/test_recipe_import.py
src/backend/src/test/test_recipe_ingredient_import.py
```

Test bắt buộc:

1. Cùng fixture sinh output byte-for-byte giống nhau.
2. Code được map thành UUID và không lọt vào output.
3. Missing master có tên hợp lệ tạo derived master `is_verified = true` trước recipe ingredient.
4. Missing quantity chỉ loại recipe ingredient, không loại recipe.
5. Description hashtag được thay bằng mô tả factual.
6. Instructions array được bọc trong `{"steps": [...]}`.
7. Duplicate master natural key được gộp.
8. FK output luôn tồn tại.
9. Loader chạy hai lần không tạo duplicate.
10. Dry-run không commit.

Lệnh dự kiến:

```bash
cd src/backend
uv run pytest src/test/test_ingredient_category_import.py src/test/test_master_ingredient_import.py src/test/test_recipe_import.py
uv run ruff check scripts/ingredient_category_import.py scripts/master_ingredient_import.py scripts/recipe_import.py
uv run mypy scripts/ingredient_category_import.py scripts/master_ingredient_import.py scripts/recipe_import.py
```

Integration test chỉ được chạy với `TEST_DATABASE_URL` trỏ đến database/branch có thể bỏ đi và phải khác database ứng dụng.

## 15. Rollback và vận hành an toàn

- Migration có downgrade được kiểm thử trước khi deploy.
- Data load chạy trong transaction; lỗi trước commit phải rollback toàn bộ release.
- Không dùng `TRUNCATE`, `DROP`, reset schema hoặc xóa catalog cũ trong importer.
- Không tự động rollback bằng cách xóa theo khoảng thời gian.
- Nếu cần gỡ một catalog release sau này, bổ sung release tracking riêng trước khi cho phép thao tác đó.
- Raw files là bất biến; mọi sửa chữa được thực hiện ở transformer hoặc source release mới.

## 16. Definition of Done

- [ ] Alembic baseline/head hợp lệ.
- [ ] Models và migration phản ánh schema đã chốt.
- [ ] Migration upgrade/downgrade pass trên DB test.
- [ ] Bốn JSON normalized được sinh thành công.
- [ ] Không có `master_ingredient_code`, `cleaned_name` hoặc crawl metadata trong output.
- [ ] 5.479 recipe được giữ lại.
- [ ] Mọi recipe ingredient output có recipe FK và master FK tồn tại.
- [ ] 31 dòng không có quantity được ghi rõ trong rejection report.
- [ ] Validation pass.
- [ ] Dry-run pass và rollback.
- [ ] Import thật chạy theo batch và commit thành công.
- [ ] Chạy import lần hai không sinh duplicate.
- [ ] Post-import audit không phát hiện orphan hoặc quantity không hợp lệ.
- [ ] Manifest lưu đủ checksum và counts của catalog release.

## 17. Thứ tự triển khai đề xuất

1. Chốt và sửa database models.
2. Khôi phục/xác nhận Alembic baseline rồi tạo migration mới.
3. Viết `transform` và các test thuần dữ liệu.
4. Sinh output thật và review mẫu/ngẫu nhiên.
5. Viết `validate` và khóa acceptance counts.
6. Viết `load --dry-run` và batch upsert.
7. Chạy migration + dry-run trên DB test.
8. Import thật trên DB test và chạy post-import audit.
9. Chỉ sau khi toàn bộ gate pass mới chạy cùng quy trình trên môi trường đích.
