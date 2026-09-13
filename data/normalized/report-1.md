# BÁO CÁO QUÁ TRÌNH CHUẨN HÓA DỮ LIỆU

---

- Giai đoạn: phase 1
- Tổng quan công việc: Phân tích toàn bộ pipeline từ raw đến bốn output database bằng các transformer hiện có, chạy trong bộ nhớ; không ghi đè file JSON normalized.
- Ngày: 2026-09-13

---

## category

- Tổng số lượng import: **16** category (15 từ nutrition catalog và `Chưa phân loại`).

### Các vấn đề của file chuẩn hóa

- `description` là `null` ở **16/16 (100%)** vì dữ liệu crawl chỉ có tên category. Trường này nullable nên không chặn import.

### Nhận xét chung

- Thực hiện tự viết description cho 16 cái (Có thể nhờ AI sinh, cái này cứ để cho KA lo)

## ingredient

- Tổng số lượng import: **6.666** master ingredient.

### Các vấn đề của file chuẩn hóa

- **5.814/6.666 (87,2%)** thuộc `Chưa phân loại`: phần lớn được sinh từ ingredient recipe không có catalog nutrition/category đáng tin cậy.
- Nutrition thiếu nhiều: `calories` **5.816 (87,2%)**, `protein_g` **5.853 (87,8%)**, `fat_g` **5.974 (89,6%)**, `carbs_g` **5.988 (89,8%)**, `sugar_g` **6.525 (97,9%)**, `sodium_mg` **6.253 (93,8%)** là `null`.
- `other_nutrients` rỗng ở **5.842 (87,6%)**; nguồn nutrition chỉ bao phủ một phần nhỏ master ingredient.
- `description`, `default_media_url` và `default_storage_mode` là `null` ở **100%** vì crawl không cung cấp các dữ liệu này.

### Nhận xét chung

- Cần ưu tiên cải thiện mapping master ingredient sang category từ nutrition catalog hoặc alias đáng tin cậy, vì 87,2% master hiện thuộc `Chưa phân loại`.
- Nên bổ sung nutrition từ nguồn dinh dưỡng chuẩn, gồm calories, protein, fat, carbs, sugar, sodium và các nutrient có `name`, `value`, `unit`. `other_nutrients` là nơi lưu các nutrient bổ sung, không phải một field để crawl riêng.

## recipe

- Tổng số lượng import: **5.479** recipe canonical.

### Các vấn đề của file chuẩn hóa

- `estimated_cost` là `null` ở **5.479/5.479 (100%)**: crawl không có dữ liệu chi phí.
- `total_sugar_g` là `null` và `other_nutrients` rỗng ở **100%**: nguồn crawl hiện không có tổng sugar/micronutrients để map.
- `media_url` là `null` ở **1.302/5.479 (23,8%)**.
- Có **397** description chỉ chứa hashtag nên phải sinh mô tả factual; có **1** recipe thiếu instructions và dùng `{"steps": []}`.

### Nhận xét chung

- Nên cài thêm dữ liệu cho các trường `estimated_cost`, `other_nutrients` (có thể chơi random luôn)

## recipe_ingredient

- Tổng số lượng import: **61.969/62.023** dòng nguồn; **54** dòng hiện nằm trong rejection report (**0,09%**). Recipe cha vẫn được giữ lại.

### Các vấn đề của file chuẩn hóa

- **50** dòng có `estimated_weight_g = 0.0` đang bị transformer gắn `INVALID_NUMERIC`. Đây là vấn đề của quy tắc normalize: `0.0` phải được hiểu là không có weight để fallback sang quantity gốc, không phải dữ liệu số lỗi. Trong 50 dòng này, **19** có quantity gốc hợp lệ và cần được giữ; **31** thực sự không có quantity dùng được.
- **4** dòng bị `MISSING_MASTER_NAME` vì `cleaned_name` là placeholder hoặc cả câu hướng dẫn, không phải tên nguyên liệu. Việc reject các dòng này là hợp lý.
- `display_quantity` là `null` ở **20.641/61.969 (33,3%)** vì nguồn không ghi quantity hiển thị; các dòng này vẫn có `required_quantity` theo gram ước tính.
- `preparation_note` là `null` ở **56.715/61.969 (91,5%)** vì nguồn hầu như không ghi chú sơ chế.

### Nhận xét chung

- Lần crawl sau cần tách rõ `quantity`, `unit` và `preparation_note` từ text gốc. `estimated_weight_g` nên để `null` khi không ước lượng được, không gửi `0.0`; quantity gốc vẫn phải giữ để pipeline fallback.
- Không được random `required_quantity`, `estimated_weight_g`, tên nguyên liệu hoặc nutrition. Có thể để `null` khi thiếu để tránh làm sai công thức.
- `unit`, `display_quantity` và `display_unit` không cần crawl thêm: có thể chuẩn hóa từ quantity/unit gốc. `is_optional` cũng có thể mặc định `false` đến khi crawler có tín hiệu rõ ràng.
- Cần cải thiện parser để loại placeholder và câu hướng dẫn khỏi `cleaned_name`; chỉ tạo master khi trích được tên nguyên liệu thực sự.
- Nên giữ đầy đủ `raw_text` nội bộ để audit và sửa mapping, nhưng không cần nạp trường này vào bảng `recipe_ingredients`.
