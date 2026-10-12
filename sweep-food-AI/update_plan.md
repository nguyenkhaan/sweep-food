
Có thể cập nhật đầy đủ theo hướng lấy commit `a060b7f` trong `references/sweep-food-AI` làm nguồn chuẩn, nhưng thực hiện merge có kiểm soát thay vì chép đè toàn thư mục.

## Kiến trúc mục tiêu

```text
Frontend (chưa sửa)
        │
        ▼
Backend API
  DTO/adapter contract v2
        │
        ▼
SweepFood AI v2
  Pantry resolver
  Candidate filtering
  Scenario constraints
  LightGBM ranking
  Groq OCR / ASR
        │
        ▼
Processed datasets + model artifacts
```

## Giai đoạn 1 — Đồng bộ SweepFood AI v2

### 1.1. Đồng bộ recommendation engine

Bổ sung và tích hợp:

- `pantry_resolver.py`
- `contextual_features.py`
- `life_scenarios.py`
- Candidate quota theo từng nguyên liệu.
- Exact alias/master-code resolution.
- Multi-urgent round-robin ranking.
- Hard filters cho ăn chay, tiểu đường, cao huyết áp, gout, keto và đau dạ dày.
- Ingredient role `accompaniment`.
- Correct master codes trong pantry simulator.
- LightGBM ranker và training script mới.

Giữ lại các sửa lỗi đang có trong bản hiện tại:

- Xử lý `None` an toàn trong expiry.
- Word-boundary matching tránh false-positive.
- Deterministic ordering.
- Các fallback cần thiết khi dữ liệu thiếu role.

### 1.2. Đồng bộ Smart Input v2

- Thêm Groq Vision OCR.
- Thêm `smart_parser` làm parser pantry chuẩn duy nhất.
- Làm giàu kết quả bằng master code, category và nutrition.
- Đồng bộ label parser mới.
- Sửa lỗi `raw` chưa được gán trong text-input.
- Giữ `quantity_source` và xác định rõ:
  - `extracted`: đọc được định lượng.
  - `estimated`: dùng giá trị mặc định.
- Không sao chép `smart_input/pantry_parser.py` bị trùng chức năng.
- Chỉ xóa Paddle/VietOCR/ProtonX sau khi Groq flow và test đã chạy thành công.

`GROQ_API_KEY` tiếp tục lấy từ môi trường; không ghi secret vào repository.

### 1.3. Đồng bộ pipeline dữ liệu

Thêm các script:

- `merge_duplicate_dishes.py`
- `rebuild_recipe_aggregates.py`
- `tag_accompaniments.py`
- `train_recommendation_ranker.py`

Không sửa hoặc xóa `data/raw` và `data/interim`.

### 1.4. Khôi phục runtime artifacts cần thiết

Để “đầy đủ tính năng mới”, chỉ cập nhật code là chưa đủ. Cần lấy từ Git tree của bản tham chiếu:

- `recipes.json`
- `recipe_ingredients.json`
- `recipe_canonical_mapping.json`
- `master_ingredients_nutrition.csv`
- `lgbm_contextual.txt`
- `metadata.json`

Giữ `recipes_restructured_detailed.json` hiện tại nếu toàn bộ recipe ID còn hợp lệ.

FreshCheck KB không tồn tại trong cả dự án lẫn commit tham chiếu, vì vậy `freshness_guide` sẽ tiếp tục là tùy chọn cho tới khi có artifact này.

### Checkpoint AI

Chỉ chuyển sang backend khi:

- AI service khởi động được.
- LightGBM model được load, không âm thầm fallback.
- `/api/recommend`, OCR text/image và ASR chạy được.
- Recipe ID là UUID hợp lệ và không trùng.
- Các scenario filter có test.
- Không còn regression false-positive của receipt parser.
- Toàn bộ test AI hiện tại và test mới đều qua.

## Giai đoạn 2 — Chốt API contract v2

Không nên sử dụng nguyên response lỏng lẻo hiện tại của bản tham chiếu. Đề xuất contract nội bộ mới:

### Request

```json
{
  "items": [
    {
      "name": "thịt bò",
      "code": "7001",
      "quantity_g": 300,
      "hours_to_expire": 12,
      "is_staple": false
    }
  ],
  "household_size": 4,
  "max_cooking_time_min": 45,
  "scenario_type": "custom",
  "dietary_restrictions": [],
  "allergies": [],
  "disliked_ingredients": [],
  "preferred_cuisines": []
}
```

Các trường allergy/restriction được giữ và chuyển thành hard filter. Không nên loại bỏ tính năng an toàn này theo bản tham chiếu.

### Response

```json
{
  "status": "success",
  "contract_version": "2",
  "model_version": "lgbm-contextual-v1",
  "catalog_revision": "...",
  "ranker_model": "LightGBM LambdaMART",
  "timings": {
    "total_ms": 20.1,
    "candidate_ms": 2.3,
    "ranker_ms": 4.8
  },
  "recommendations": [
    {
      "id": "recipe-uuid",
      "name": "Tên món",
      "rank_score": 1.284,
      "ranking_features": {
        "core_coverage": 0.8,
        "core_missing_count": 1,
        "secondary_coverage": 0.6,
        "shopping_gap_items": 1,
        "rescue_weight_g": 300,
        "nutrition_confidence": 0.9,
        "kcal_per_serving": 450,
        "protein_per_serving": 25,
        "prep_complexity": 3.2
      },
      "matched_ingredients": [],
      "missing_ingredients": [],
      "optional_ingredients": [],
      "rescued_items": [],
      "status_badge": "ready"
    }
  ]
}
```

`rank_score` là điểm xếp hạng thô, không giả định nằm trong `0..1`. Thứ tự kết quả mới là thông tin chính xác.

Response `empty` vẫn phải chứa `contract_version`, model metadata và mảng `recommendations: []`.

## Giai đoạn 3 — Sửa backend theo contract v2

### 3.1. AI HTTP client

Cập nhật [sweep_food_ai_client.py](/home/cloud/workspace/project/mobile/sweep-food/src/backend/src/service/sweep_food_ai_client.py):

- DTO request/response v2.
- `rank_score` không giới hạn `0..1`.
- Thay E/A/P/U bằng chín contextual features.
- Nhận matched/missing/optional/rescued ingredients.
- Validate contract version và UUID.
- Giữ timeout, lỗi provider và response validation hiện tại.

### 3.2. Recommendation domain

Cập nhật:

- `recommendation_dto.py`
- `recommendation_ai_service.py`
- Router/dependency liên quan.

Backend sẽ:

- Ánh xạ recipe UUID từ AI sang recipe trong database.
- Giữ cảnh báo `UNKNOWN_RECIPE_ID`.
- Trả `rank_score`, ranking features và model metadata.
- Không tự tính lại điểm AI.
- Không còn tạo E/A/P/U giả từ response mới.

Chưa cần migration database. Các cột E/A/P/U hiện tại được giữ để tránh mở rộng phạm vi; chúng chưa cần dùng trong đường tích hợp v2.

### 3.3. Extraction contract

Điều chỉnh OCR/ASR DTO để giữ:

- `quantity_source`
- `raw_name`
- Master code/category.
- Nutrition/freshness nếu có.
- Không lưu quantity ước lượng như quantity được OCR xác nhận.

### 3.4. Đồng bộ recipe identity

- So sánh toàn bộ recipe ID mà AI có thể trả với catalog backend.
- Không tự động xóa recipe backend bị loại khỏi AI dataset.
- Backend bỏ qua và cảnh báo ID chưa được import.
- Chỉ chạy lại pipeline import/seed nếu độ phủ ID không đạt yêu cầu.

### Checkpoint tích hợp

- Backend client contract tests qua.
- Recommendation service/router tests qua.
- OCR/ASR extraction tests qua.
- Một test end-to-end gọi AI v2 thật qua HTTP hoặc ASGI test server.
- Các scenario `custom`, `chay`, `gout` và multi-urgent trả đúng.
- Không có chỉnh sửa trong `src/frontend`.

## Giai đoạn 4 — Dọn mã cũ

Chỉ thực hiện sau khi hai checkpoint đều xanh:

- Xóa XGBoost model loader cũ.
- Xóa feature extractor 30 chiều nếu không còn caller.
- Xóa Paddle/VietOCR/ProtonX và dependency tương ứng nếu Groq đã thay thế hoàn toàn.
- Không xóa test cũ; chuyển chúng thành regression tests khi còn giá trị.
- Kiểm tra dead code bằng toàn bộ caller trước khi xóa.

## Thứ tự thực hiện đề xuất

1. Đồng bộ code và artifact vào `sweep-food-AI`.
2. Sửa các regression đã xác định trong bản tham chiếu.
3. Hoàn thành test và checkpoint AI.
4. Chốt contract v2 bằng test/schema.
5. Cập nhật client và recommendation service backend.
6. Chạy checkpoint tích hợp AI–BE.
7. Dọn mã cũ.
8. Báo cáo diff, test, artifact và `git status`.

Mình đề xuất thực hiện đúng thứ tự này; không sửa frontend và không thay đổi database schema trong đợt này.

Đã bỏ qua: tương thích `src/frontend` và FreshCheck enrichment đầy đủ vì KB chưa tồn tại.
Rủi ro chính: cập nhật processed dataset/model là bắt buộc để LightGBM v2 hoạt động đúng; chỉ đồng bộ mã nguồn sẽ không đạt mục tiêu “đầy đủ tính năng mới”.
