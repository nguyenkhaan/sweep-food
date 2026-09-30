> **2026-09-10 update ? missing nutrition propagation FIXED for processed recipe ingredients.**
> Master blanks/NaN now remain missing (CSV blank, JSON null); true zero remains zero.
> Historical statements below about downstream NaN becoming zero and processed/interim equality
> describe the pre-fix snapshot. Master incompleteness and unrelated findings remain open.
> See [validated fix details](#missing-nutrition-propagation-fix-2026-09-10) and
> [machine-readable validation](missing_nutrition_validation.json).

# Báo cáo kết quả EDA SweepFood

## 1. Dữ liệu Interim

### 1.1 `recipes_crawled_cleaned.csv`

#### Vấn đề 1: Nhiều công thức có tên giống nhau sau khi chuẩn hóa

**Quan sát**

- Tổng số công thức: 5.641.
- Có 251 dòng có tên món trùng với ít nhất một công thức khác sau khi chuẩn hóa tên bằng cách loại bỏ khoảng trắng đầu/cuối và chuyển về chữ thường.
- Tuy nhiên, các công thức trùng tên thường có:
  - `source_url` khác nhau;
  - nguồn dữ liệu khác nhau;
  - số khẩu phần khác nhau;
  - số lượng nguyên liệu khác nhau;
  - giá trị dinh dưỡng khác nhau.

Ví dụ, món `Bánh mì chảo` xuất hiện 3 lần nhưng đến từ 3 nguồn khác nhau và có lượng calories cũng như số nguyên liệu khác nhau.

**Đánh giá**

Các bản ghi này không nên được xem là dữ liệu trùng lặp hoàn toàn. Nhiều công thức khác nhau có thể cùng đại diện cho một món ăn nhưng khác cách chế biến, thành phần hoặc khẩu phần.

**Hướng xử lý đề xuất**

- Không loại bỏ công thức chỉ dựa trên trường `name`.
- Tiếp tục sử dụng `id` hoặc `source_url` làm định danh của từng công thức.
- Nếu sau này hệ thống cần nhóm các phiên bản khác nhau của cùng một món, có thể bổ sung một trường tên món chuẩn hóa riêng, chẳng hạn `canonical_dish_name`.

---

#### Vấn đề 2: Một số công thức có giá trị dinh dưỡng không nhất quán

**Quan sát**

- Có 102 / 5.641 công thức có mức chênh lệch calories lớn hơn 30% khi so sánh:
  - `total_calories`
  - với lượng calories ước tính từ các chất đa lượng theo công thức:

  `calories ≈ 4 × protein + 4 × carbohydrate + 9 × fat`

- Một số trường hợp có mức chênh lệch rất lớn.

Ví dụ:

- `Bánh rán chocolate đậu đỏ`: `total_calories = 68 kcal`, trong khi calories ước tính từ protein, fat và carbohydrate khoảng `1.570 kcal`.
- `Giò heo kho sả ớt`: `total_calories = 11 kcal`, trong khi giá trị ước tính khoảng `204 kcal`.

**Điều tra thêm**

Khi đối chiếu dữ liệu giữa `recipes_crawled_cleaned.csv` và `recipe_ingredients.csv`, tổng calories, protein, fat và carbohydrate của mỗi công thức khớp hoàn toàn với tổng các nguyên liệu thuộc công thức đó.

Mức chênh lệch ở bước tổng hợp đều bằng 0.

**Đánh giá**

Bước cộng tổng dinh dưỡng từ nguyên liệu lên công thức đang hoạt động đúng.

Vấn đề nhiều khả năng xuất phát từ dữ liệu dinh dưỡng ở cấp độ nguyên liệu hoặc quá trình ánh xạ/tính toán dinh dưỡng trước đó.

**Hướng xử lý đề xuất**

- Không chỉnh trực tiếp `total_calories`, `total_protein_g`, `total_fat_g` hoặc `total_carbs_g` ở bảng recipe.
- Kiểm tra ngược dữ liệu dinh dưỡng ở `recipe_ingredients.csv`.
- Đối chiếu các giá trị dinh dưỡng với bảng dữ liệu dinh dưỡng nguyên liệu gốc.
- Kiểm tra khả năng các cột calories, protein, fat và carbohydrate bị ánh xạ sai trong một số trường hợp.

---

### 1.2 `recipe_ingredients.csv`

#### Vấn đề 3: Giá trị dinh dưỡng của một số nguyên liệu không nhất quán

**Quan sát**

- Tổng số bản ghi nguyên liệu: 63.943.
- Có 3.010 bản ghi, tương đương khoảng 4,71%, có mức chênh lệch calories lớn hơn 30% khi so sánh calories hiện tại với calories ước tính từ protein, fat và carbohydrate.

Kết quả theo phương pháp khớp nguyên liệu:

| Phương pháp khớp | Tổng số | Không nhất quán | Tỷ lệ |
|---|---:|---:|---:|
| `QWEN_LLM_MATCH` | 862 | 79 | 9,16% |
| `PRESET_ALIAS_MATCH` | 40.572 | 2.389 | 5,89% |
| `EXACT_CATALOG_MATCH` | 13.155 | 513 | 3,90% |
| `CLEANED_NAME_MATCH` | 788 | 25 | 3,17% |
| `STANDARDIZED_CURE` | 365 | 1 | 0,27% |
| `UNMATCHED` | 8.194 | 3 | 0,04% |
| `BERT_SEMANTIC_MATCH` | 7 | 0 | 0,00% |

**Ví dụ đáng chú ý**

Một số bản ghi cho thấy dấu hiệu có thể bị sai ánh xạ trường dinh dưỡng.

Ví dụ nguyên liệu `Kem tươi` có trường hợp:

- `estimated_weight_g = 100`
- `calories = 1`
- `protein_g = 335`
- `fat_g = 2.4`
- `carbs_g = 35.5`

Giá trị `335 g protein` trên 100 g nguyên liệu là bất thường, trong khi giá trị `335` lại có khả năng giống một giá trị năng lượng kcal hơn.

**Đánh giá**

Vấn đề không chỉ xảy ra đối với các nguyên liệu được khớp bằng AI.

Ngay cả `EXACT_CATALOG_MATCH` và `PRESET_ALIAS_MATCH` cũng có nhiều bản ghi không nhất quán. Vì vậy, nguyên nhân có thể liên quan đến:

- cách ánh xạ các trường dinh dưỡng;
- dữ liệu nguồn trong bảng dinh dưỡng;
- hoặc quá trình tính toán dinh dưỡng từ khối lượng nguyên liệu.

Không thể kết luận rằng chỉ riêng quá trình matching là nguyên nhân.

**Hướng xử lý đề xuất**

- Đối chiếu `recipe_ingredients` với bảng `master_ingredients_nutrition`.
- Kiểm tra mapping giữa các trường:
  - calories;
  - protein;
  - fat;
  - carbohydrate.
- Kiểm tra công thức scale nutrition theo `estimated_weight_g`.
- Kiểm tra riêng các bản ghi có mức sai lệch lớn.
- Phân tích các bản ghi lỗi theo `match_method` để xác định lỗi có tập trung ở một bước xử lý cụ thể hay không.

---

#### Vấn đề 4: Một số nguyên liệu có toàn bộ giá trị dinh dưỡng bằng 0

**Quan sát**

Có 8.657 bản ghi trong `recipe_ingredients.csv` có đồng thời:

- `calories = 0`
- `protein_g = 0`
- `fat_g = 0`
- `carbs_g = 0`

Trong đó:

- 7.735 bản ghi thuộc nhóm `UNMATCHED`;
- 922 bản ghi đã match được với master ingredient.

Sau khi đối chiếu 922 bản ghi đã match với
`master_ingredients_nutrition.csv`:

- phần lớn trường hợp bằng 0 là hợp lý hoặc do dữ liệu master không đầy đủ;
- 41 bản ghi `Xoài` không có dữ liệu `energy_kcal` trong master;
- có 28 bản ghi mà master có `energy_kcal > 1` nhưng nutrition trong
  `recipe_ingredients` vẫn bị gán toàn bộ bằng 0.

Các nguyên liệu bị ảnh hưởng:

| Nguyên liệu | Energy trong master | Số lần xuất hiện |
|---|---:|---:|
| Chuối, khô | 301 kcal | 25 |
| Hạt sen | 164 kcal | 1 |
| Gia vị | 62,2 kcal | 1 |
| Mọc, từ thịt lợn, nấu canh | 286 kcal | 1 |

**Đánh giá**

Không thể coi toàn bộ 922 bản ghi đã match nhưng nutrition bằng 0 là lỗi.

Tuy nhiên, 28 bản ghi có nutrition trong master nhưng bị chuyển thành toàn bộ 0
cho thấy có khả năng tồn tại lỗi trong bước lấy hoặc scale dữ liệu dinh dưỡng
từ master sang recipe ingredient.

Ngoài ra, các trường hợp như `Xoài` phản ánh vấn đề thiếu dữ liệu ngay từ
master nutrition dataset.

**Hướng xử lý đề xuất**

- Kiểm tra bước ánh xạ và scale nutrition từ master ingredient sang
  `recipe_ingredients` đối với 28 bản ghi bất thường.
- Không mặc định coi dữ liệu nutrition chưa có là giá trị 0.
- Phân biệt rõ:
  - nutrition thực sự bằng 0;
  - nutrition chưa xác định;
  - nutrition bị mất trong quá trình xử lý.
- Bổ sung hoặc cải thiện dữ liệu master đối với các nguyên liệu còn thiếu
  nutrition, ví dụ `Xoài`.

#### Vấn đề 5: Tỷ lệ nguyên liệu không match được với master ingredient còn tương đối cao

**Quan sát**

- Có 7.735 / 63.943 bản ghi không có `master_ingredient_code`, tương đương khoảng 12,10%.
- Toàn bộ 7.735 bản ghi này đều thuộc `match_method = UNMATCHED`.
- `match_confidence` của nhóm này có:
  - trung bình: 0,4424;
  - trung vị: 0,4418;
  - lớn nhất: 0,7789.

Qua quan sát mẫu dữ liệu, nhiều `cleaned_name` vẫn còn chứa:
- nhiều nguyên liệu trong cùng một chuỗi;
- từ mô tả cách chế biến;
- phần ghi chú/thay thế nguyên liệu;
- tên thương hiệu hoặc tên sản phẩm cụ thể.

Ngoài ra vẫn có một số tên tương đối rõ ràng như `tôm nõn`, `muối biển`, `nước tương đậm màu` nhưng chưa match được.

**Đánh giá**

Tỷ lệ `UNMATCHED` 12,10% có thể làm giảm độ phủ dinh dưỡng của dữ liệu recipe.

Một phần nguyên nhân có khả năng đến từ bước làm sạch và chuẩn hóa tên nguyên liệu chưa tách hết thông tin phụ trước khi matching.

**Hướng xử lý đề xuất**

- Cải thiện bước chuẩn hóa `cleaned_name`.
- Tách các chuỗi chứa nhiều nguyên liệu trước khi matching nếu phù hợp.
- Loại bỏ các cụm mô tả như cách chế biến, ghi chú thay thế hoặc tên thương hiệu.
- Kiểm tra các alias phổ biến chưa có trong alias map.
- Xem xét riêng nhóm `UNMATCHED` có confidence cao để tìm các trường hợp có thể match được nếu điều chỉnh threshold hoặc alias.

**Điều tra thêm**

Trong 7.735 bản ghi `UNMATCHED`, chỉ có 122 bản ghi (1,49%) có
`match_confidence >= 0,65`.

Các bản ghi confidence cao cho thấy một số nguyên nhân phổ biến:

- alias hoặc master ingredient chưa bao phủ một số cách gọi phổ biến;
- một chuỗi chứa nhiều nguyên liệu hoặc nhiều lựa chọn thay thế;
- `cleaned_name` vẫn còn chứa từ mô tả hoặc thông tin phụ.

Ví dụ: `bột cà ri`, `bột paprika`, `táo khô`, `thịt chân giò heo` có thể là các trường hợp cần mở rộng alias; trong khi các chuỗi như `nước dùng gà hoặc viên súp gà` cần được xử lý tốt hơn ở bước chuẩn hóa.

**Kết luận bổ sung**

Việc chỉ giảm threshold matching không phải hướng xử lý chính vì nhóm confidence cao chỉ chiếm 1,49% số bản ghi `UNMATCHED`.

Ưu tiên nên là:
- cải thiện chuẩn hóa `cleaned_name`;
- bổ sung alias cho các cách gọi phổ biến;
- xử lý các chuỗi chứa nhiều nguyên liệu/lựa chọn trước khi matching;
- sau đó mới đánh giá lại threshold trên tập validation.

#### Vấn đề 6: Khối lượng ước tính mặc định cho nguyên liệu không có định lượng

**Quan sát**

Có 21.231 bản ghi thiếu `required_quantity`, chiếm 33,20% dữ liệu
`recipe_ingredients`.

Trong số này:

- 21.088 bản ghi có `estimated_weight_g = 10`;
- tương đương 99,33% số bản ghi thiếu định lượng;
- chỉ một số rất nhỏ sử dụng giá trị khác như 1,5g hoặc 0g.

Các trường hợp thiếu định lượng chủ yếu thuộc các đơn vị `OTHER` và `CHUT_IT`,
ví dụ các mô tả như `ít tiêu`, `hành lá`, `vừa đủ`, `dầu ăn`, `nước mắm`.

**Đánh giá**

Việc thiếu `required_quantity` không nhất thiết là lỗi vì nhiều công thức gốc
không cung cấp định lượng cụ thể.

Tuy nhiên, việc gần như toàn bộ các trường hợp này đều được gán
`estimated_weight_g = 10` cho thấy pipeline đang sử dụng một giá trị fallback
cố định.

Giá trị 10g giống nhau cho mọi nguyên liệu có thể gây sai lệch khi tính dinh
dưỡng vì các nguyên liệu khác nhau có mật độ năng lượng rất khác nhau.

**Hướng xử lý đề xuất**

- Không nên sử dụng một khối lượng mặc định duy nhất cho tất cả nguyên liệu.
- Xem xét xây dựng khối lượng mặc định theo loại nguyên liệu hoặc đơn vị
  (`CHUT_IT`, gia vị, rau thơm, dầu, nước sốt,...).
- Nếu không thể ước tính đáng tin cậy, nên đánh dấu khối lượng là chưa xác định
  thay vì mặc định 10g.
- Đánh giá mức độ ảnh hưởng của fallback 10g lên tổng nutrition của recipe
  trước khi thay đổi pipeline.

  **Mức độ ảnh hưởng**

Fallback `estimated_weight_g = 10` xuất hiện trong 4.125 / 5.641 công thức,
tương đương 73,13% toàn bộ dataset recipe.

Trong các công thức bị ảnh hưởng:

- trung bình có 5,11 nguyên liệu sử dụng fallback 10g;
- trung vị là 4 nguyên liệu;
- 25% công thức có từ 8 nguyên liệu fallback trở lên;
- trường hợp cao nhất có 25 nguyên liệu sử dụng fallback.

Điều này cho thấy fallback 10g không phải trường hợp hiếm mà là một quy tắc
có phạm vi ảnh hưởng lớn trong pipeline.

Tuy nhiên, cần đánh giá thêm mức đóng góp dinh dưỡng của các nguyên liệu này
trước khi kết luận mức độ sai lệch của nutrition ở cấp recipe.

**Ảnh hưởng đến giá trị dinh dưỡng**

Trong 21.088 nguyên liệu sử dụng fallback `estimated_weight_g = 10`,
có 18.724 bản ghi (88,79%) thực sự đóng góp calories hoặc các chất dinh dưỡng
vào tổng nutrition của recipe.

Ở cấp độ công thức:

- 1.471 recipe có hơn 20% tổng calories đến từ các nguyên liệu sử dụng fallback 10g;
- 550 recipe có hơn 50% tổng calories đến từ các nguyên liệu fallback.

Điều này cho thấy việc sử dụng một giá trị 10g mặc định có khả năng ảnh hưởng
đáng kể đến kết quả tính nutrition của một phần không nhỏ dataset.

**Đánh giá bổ sung**

Fallback 10g nên được xem là một vấn đề cần ưu tiên trong preprocessing,
vì nó không chỉ ảnh hưởng tới nhiều recipe mà còn có thể chiếm phần lớn
nutrition được tính cho một số công thức.

**Ví dụ mức độ ảnh hưởng**

Khi kiểm tra các công thức bị ảnh hưởng nặng nhất, có nhiều recipe mà
100% `total_calories` được tính từ các nguyên liệu đang sử dụng fallback
`estimated_weight_g = 10`.

Một số ví dụ:

- `Bắp Cải xào Cà Rốt Thịt lợn`: 27 / 27 kcal từ fallback;
- `Củ cải khô xào thịt heo ba chỉ`: 227 / 227 kcal từ fallback;
- `Sườn Bò Ủ Áp Chảo Gang`: 90 / 90 kcal từ fallback;
- `Giò heo kho (hon)dưa cải`: 131 / 131 kcal từ fallback;
- `Thịt bò xào đậu que`: 113 / 113 kcal từ fallback.

Điều này cho thấy nutrition của một số recipe đang phụ thuộc hoàn toàn vào
khối lượng giả định 10g thay vì định lượng thực tế từ công thức.

**Kết luận**

Fallback 10g là vấn đề có mức ảnh hưởng cao và nên được ưu tiên xem xét trong
pipeline preprocessing. Nếu tiếp tục sử dụng fallback, nên xây dựng quy tắc
ước lượng theo từng nhóm nguyên liệu thay vì dùng một giá trị cố định cho tất cả.

### 1.3 So sánh `interim` và `processed/recipes`

**Quan sát**

Hai cặp dữ liệu:

- `data/interim/recipes_crawled_cleaned.csv`
  và `data/processed/recipes/recipes.csv`
- `data/interim/recipe_ingredients.csv`
  và `data/processed/recipes/recipe_ingredients.csv`

được đối chiếu trực tiếp bằng Pandas.

Kết quả cho thấy:

- số dòng và số cột giống nhau;
- schema giống nhau;
- toàn bộ giá trị trong DataFrame giống nhau;
- không có bất kỳ dòng nào khác biệt.

**Đánh giá**

Ở trạng thái dữ liệu hiện tại, `processed/recipes` là bản sao hoàn toàn của
dữ liệu recipe trong `interim`.

Do đó, các vấn đề chất lượng dữ liệu đã phát hiện ở `interim`, bao gồm:

- nutrition không nhất quán;
- nguyên liệu `UNMATCHED`;
- nutrition bằng 0;
- fallback `estimated_weight_g = 10`;

vẫn tồn tại nguyên vẹn trong dữ liệu `processed/recipes`.

Điều này chưa nhất thiết là lỗi nếu pipeline chủ động sử dụng `processed`
như điểm xuất dữ liệu cuối cùng mà không thực hiện thêm bước biến đổi.
Tuy nhiên, nếu `processed` được kỳ vọng là dữ liệu đã được làm sạch và sẵn
sàng cho downstream task thì cần xem xét lại pipeline.

**Hướng xử lý đề xuất**

- Xác nhận mục đích của `data/processed/recipes`.
- Nếu đây là dữ liệu cuối cùng dùng cho recommendation/model, cần xử lý các
  vấn đề đã phát hiện trước khi coi đây là dataset production-ready.
- Tránh thực hiện EDA lặp lại cho hai file này vì chúng hiện giống hoàn toàn
  dữ liệu `interim`.

### 1.4 `qwen_extracted_map.json` và pipeline matching

#### Vấn đề 7: Một số kết quả extract của Qwen vẫn chứa nhiều nguyên liệu hoặc output không hợp lệ

**Quan sát**

`qwen_extracted_map.json` chứa 935 mapping từ raw ingredient text sang
tên nguyên liệu được extract.

Không phát hiện key hoặc value rỗng.

Sử dụng heuristic dựa trên các dấu phân cách (`/`, `+`, `và`, `hoặc`)
và độ dài chuỗi, có 52 / 935 mapping (5,56%) được đánh dấu là output phức tạp.

Một số ví dụ:

- `tỏi/ớt/hành lá`;
- `củ cải trắng và cà rốt`;
- `nước cốt chanh hoặc giấm`;
- `xà lách cà chua cà rốt`;
- `giá đỗ dưa leo rau quế hành phi ngò rí`.

Ngoài ra xuất hiện các output không phải tên nguyên liệu như:

- `không có nguyên liệu cụ thể`;
- `không có danh từ chính duy nhất`.

**Đánh giá**

Trong 44 recipe ingredient rows liên quan tới các output phức tạp:

- 41 dòng được match bằng `QWEN_LLM_MATCH`;
- 3 dòng `UNMATCHED`;
- unmatched rate chỉ 6,82%.

Tuy nhiên, tỷ lệ match cao không đồng nghĩa với chất lượng tốt.

Nhiều chuỗi chứa nhiều nguyên liệu vẫn được gán vào một master ingredient duy nhất
với `match_confidence = 0.98`.

Ví dụ:

- `tỏi/ớt/hành lá` → `Hành hoa, tươi`;
- `xà lách cà chua cà rốt` → `Cà chua`;
- `củ cải trắng và cà rốt` → `Cà rốt`;
- `tiêu hạt/ớt xanh/ớt đỏ` → `Hạt tiêu`.

Điều này có thể làm mất các ingredient còn lại và khiến nutrition của recipe bị
tính dựa trên một ingredient đại diện không đầy đủ.

Do đó vấn đề chính không chỉ là `UNMATCHED`, mà còn là false-positive match với
confidence cao trên các input đa nguyên liệu.

**Hướng xử lý đề xuất**

- Yêu cầu bước extraction trả về một ingredient canonical duy nhất khi có thể.
- Tách các raw text chứa nhiều ingredient thành nhiều thành phần trước khi match.
- Với các lựa chọn dạng `A hoặc B`, cần xác định policy rõ ràng thay vì giữ cả
  chuỗi làm một ingredient.
- Không sử dụng các câu như `không có nguyên liệu cụ thể` làm ingredient name.

**Vấn đề confidence của QWEN_LLM_MATCH**

Trong 862 dòng sử dụng `QWEN_LLM_MATCH`, có 788 dòng
(91,42%) nhận cùng một `match_confidence = 0.98`.

Phân phối confidence bị tập trung mạnh tại 0.98:

- Q1 = 0.98;
- median = 0.98;
- Q3 = 0.98.

Trong khi đó, một số input đa nguyên liệu hoặc mơ hồ vẫn được gán
confidence 0.98 dù kết quả chỉ chọn một master ingredient đại diện.

Điều này cho thấy `match_confidence` của QWEN hiện có khả năng chưa phản ánh
đúng mức độ chắc chắn của từng match và không nên được sử dụng trực tiếp như
một confidence score đã được calibration.

**Nguyên nhân confidence bị tập trung tại 0.98**

Kiểm tra code cho thấy trong
`scripts/run_qwen_line_pipeline.py`, khi một dòng được gán
`QWEN_LLM_MATCH`, pipeline đặt trực tiếp:

`match_confidence = 0.98`.

Do đó 0.98 là giá trị hard-code, không phải confidence được tính hoặc
calibrate từ chất lượng của từng prediction.

Điều này giải thích vì sao cả những input phức tạp, chứa nhiều nguyên liệu
hoặc có khả năng match sai vẫn nhận confidence rất cao.

**Đề xuất**

- Không diễn giải `0.98` hiện tại như xác suất đúng của Qwen match.
- Nếu cần confidence thực sự, cần xây dựng score từ tín hiệu khác như
  similarity, validation rule hoặc model confidence riêng.
- Tạm thời nên coi `match_method` và `match_confidence` là metadata pipeline,
  không phải quality guarantee.

**Nguyên nhân trong bước mapping**

Sau khi Qwen extract `cleaned_name`, hàm `map_clean_to_master()` sử dụng
một chuỗi `if` với phép kiểm tra substring và trả về ngay master ingredient
đầu tiên khớp.

Điều này tạo ra phụ thuộc vào thứ tự rule.

Ví dụ:

- `xà lách cà chua cà rốt` chứa cả `cà chua` và `cà rốt`, nhưng rule
  `cà chua` nằm trước nên kết quả là `Cà chua`;
- `hành lá/hành tím/hành tây` bị bắt bởi rule `hành lá` trước;
- rule tổng quát `ngò` nằm trước rule cụ thể `ngò gai`, nên một số chuỗi
  chứa `ngò gai` có thể bị map thành `Rau mùi (ngò rí)`.

Do đó false-positive match không chỉ đến từ output Qwen phức tạp mà còn từ
logic first-match-wins trong `map_clean_to_master()`.

**Đề xuất**

- Không đưa chuỗi chứa nhiều ingredient trực tiếp vào mapper đơn nguyên liệu.
- Ưu tiên rule cụ thể trước rule tổng quát.
- Tránh các substring rule quá rộng như `ngò`.
- Nếu một cleaned string khớp nhiều candidate, đánh dấu ambiguous thay vì
  tự động chọn candidate đầu tiên.

Toàn bộ 935 entry trong `qwen_extracted_map.json` đều tương ứng với
`raw_text` hiện có trong `recipe_ingredients.csv` (usage rate 100%),
nên không phát hiện stale hoặc unused Qwen extraction entry.

**Kết quả cuối của các input đã qua Qwen**

935 raw text trong Qwen map tương ứng với 1.123 recipe ingredient rows.

Phân bố trạng thái cuối:

- `QWEN_LLM_MATCH`: 862;
- `UNMATCHED`: 255;
- `STANDARDIZED_CURE`: 6.

### Vấn đề 8 – Trạng thái `UNMATCHED` không nhất quán với master ingredient

Pipeline mapping nguyên liệu sử dụng ngưỡng khớp cố định `MATCH_THRESHOLD = 0.78`.

Theo logic trong `nlp/map_crawled_ingredients.py`:

- Nếu `confidence >= 0.78`: giữ `master_ingredient_code`, `master_ingredient_name` và trạng thái match tương ứng.
- Nếu `confidence < 0.78`: đặt `master_ingredient_code = null`, `master_ingredient_name = null` và `match_method = UNMATCHED`.

Tuy nhiên, khi kiểm tra toàn bộ `data/interim/recipe_ingredients.csv`:

- Tổng số dòng `UNMATCHED`: **8.194**
- Số dòng `UNMATCHED` nhưng vẫn có `master_ingredient_code`: **459**
- Tỷ lệ: **5,60%** số dòng `UNMATCHED`

Điều này không phù hợp với invariant được định nghĩa trong pipeline:

`UNMATCHED -> master_ingredient_code và master_ingredient_name phải null`

Khả năng cao một bước hậu xử lý chạy sau giai đoạn mapping đã ghi lại best candidate vào các trường master nhưng không cập nhật lại `match_method`.

**Ảnh hưởng tiềm ẩn:**

Nếu downstream chỉ kiểm tra sự tồn tại của `master_ingredient_code` mà không kiểm tra `match_method`, các candidate có confidence thấp có thể bị xem như match hợp lệ. Điều này có thể làm sai dữ liệu dinh dưỡng hoặc các feature được xây dựng từ master ingredient.

**Đề xuất xử lý:**

- Thống nhất invariant cho dữ liệu cuối:
  `UNMATCHED -> master_ingredient_code/master_ingredient_name = null`.
- Nếu muốn giữ candidate có confidence thấp để review, nên lưu riêng ở các trường như `suggested_master_code`, `suggested_master_name`.
- Kiểm tra các bước hậu xử lý chạy sau `map_crawled_ingredients.py` để xác định bước nào đã đưa candidate trở lại dữ liệu.

## 3. Kiểm tra tính đồng bộ giữa CSV và JSON

Đã đối chiếu các cặp file:

- `data/interim/recipes_crawled_cleaned.csv` và `.json`
- `data/interim/recipe_ingredients.csv` và `.json`
- `data/processed/recipes/recipes.csv` và `.json`
- `data/processed/recipes/recipe_ingredients.csv` và `.json`

Kết quả:

- Số dòng và số cột giữa các cặp file đều khớp.
- Danh sách cột giống nhau.
- Nội dung dữ liệu giống nhau sau khi chuẩn hóa kiểu dữ liệu và giá trị rỗng.
- Không phát hiện sai lệch dữ liệu giữa phiên bản CSV và JSON.

Lưu ý: một số khác biệt ban đầu khi so sánh trực tiếp đến từ cách pandas biểu diễn kiểu dữ liệu, ví dụ `20004.0` trong CSV so với `20004` trong JSON, hoặc `NaN` so với chuỗi rỗng. Đây không phải sai lệch dữ liệu thực tế.

## 2. Dữ liệu Processed – Viện Dinh dưỡng

### 2.1 `master_ingredients_nutrition.csv`

#### Vấn đề 9: Một số master ingredient có tên tiếng Việt trùng nhau nhưng ý nghĩa khác nhau

**Quan sát**

Trong 749 master ingredient có 8 dòng thuộc 4 tên tiếng Việt bị trùng sau khi chuẩn hóa:

- `Cần tây`
- `Nấm kim châm`
- `Thịt trâu, đùi`
- `Tôm đồng`

Qua kiểm tra chi tiết, các trường hợp này không hoàn toàn giống nhau:

- `Cần tây` có một bản ghi ánh xạ sang `Cabbage, common, raw` và một bản ghi sang
  `Celery, raw`, cho thấy khả năng có lỗi mapping tên.
- `Nấm kim châm` có hai bản ghi có giá trị dinh dưỡng khá tương đồng nhưng khác
  mã và nhóm thực phẩm, có khả năng là duplicate từ nhiều nguồn.
- `Thịt trâu, đùi` được ánh xạ sang cả `leg` và `loin`, cho thấy tên tiếng Việt
  chưa đủ chi tiết để phân biệt phần thịt.
- `Tôm đồng` có một bản ghi dạng khô và một bản ghi dạng tươi, với giá trị dinh
  dưỡng khác biệt lớn. Đây là hai trạng thái thực phẩm khác nhau chứ không phải
  duplicate thực sự.

**Đánh giá**

Không nên loại duplicate chỉ dựa trên `name_vi`.

Một số trường hợp phản ánh lỗi mapping, trong khi một số khác là do tên nguyên
liệu chưa biểu diễn đủ trạng thái hoặc loại thực phẩm.

**Hướng xử lý đề xuất**

- Kiểm tra lại mapping của `Cần tây`.
- Xác minh và cân nhắc hợp nhất hai bản ghi `Nấm kim châm` nếu thực sự cùng một
  nguyên liệu.
- Làm rõ tên cho các trường hợp có khác biệt về phần thịt hoặc trạng thái chế
  biến.
- Ví dụ đổi `Tôm đồng` thành các tên cụ thể hơn như `Tôm đồng tươi` và
  `Tôm đồng khô`.
- Không deduplicate master ingredient chỉ dựa vào `name_vi`.

#### Vấn đề 10: Dữ liệu dinh dưỡng cốt lõi của master ingredient chưa đầy đủ

**Quan sát**

Trong 749 nguyên liệu của `master_ingredients_nutrition.csv`:

- 2 bản ghi (0,27%) thiếu `energy_kcal`;
- 39 bản ghi (5,21%) thiếu `protein_g`;
- 146 bản ghi (19,49%) thiếu `fat_g`;
- 142 bản ghi (18,96%) thiếu `carbs_g`.

Có tổng cộng 271 / 749 nguyên liệu (36,18%) thiếu ít nhất một trong bốn
trường dinh dưỡng cốt lõi và có 2 nguyên liệu thiếu toàn bộ bốn trường.

**Đánh giá**

Dữ liệu năng lượng (`energy_kcal`) có độ phủ khá tốt, nhưng protein, fat và
carbohydrate chưa đầy đủ hoàn toàn.

Các giá trị bị thiếu không nên mặc định được hiểu là bằng 0, vì `NaN` có thể
chỉ phản ánh việc nguồn dữ liệu không cung cấp chỉ số đó.

Nếu pipeline chuyển các trường thiếu thành 0 khi tính nutrition cho recipe,
kết quả dinh dưỡng có thể bị đánh giá thấp hoặc làm sai kiểm tra tính nhất quán
giữa calories và macronutrients.

**Hướng xử lý đề xuất**

- Giữ sự phân biệt giữa `NaN` và giá trị dinh dưỡng thực sự bằng 0.
- Kiểm tra cách pipeline xử lý các trường nutrition bị thiếu trước khi scale
  sang `recipe_ingredients`.
- Xác định các nhóm nguyên liệu có tỷ lệ thiếu dữ liệu cao để ưu tiên bổ sung.
- Kiểm tra riêng 2 nguyên liệu thiếu toàn bộ bốn trường dinh dưỡng cốt lõi.

**Phân bố theo nhóm thực phẩm**

Dữ liệu thiếu không phân bố đều giữa các nhóm nguyên liệu mà tập trung mạnh
ở một số nhóm:

- `Dầu, mỡ, bơ`: 86,67% nguyên liệu thiếu ít nhất một trường core nutrition;
- `Nước giải khát`: 70,83%;
- `Đồ hộp`: 60,87%;
- `Thịt và sản phẩm chế biến`: 56,25%;
- `Thủy sản và sản phẩm chế biến`: 49,41%.

Điều này cho thấy mức độ đầy đủ của dữ liệu dinh dưỡng phụ thuộc đáng kể vào
nhóm thực phẩm, thay vì chỉ là các giá trị thiếu rải rác ngẫu nhiên.

Có 2 nguyên liệu thiếu toàn bộ `energy_kcal`, `protein_g`, `fat_g` và
`carbs_g`:

- `Nước giải khát vitamin C`;
- `Nước canh`.

**Đánh giá bổ sung**

Nên ưu tiên kiểm tra hoặc bổ sung dữ liệu cho các nhóm có tỷ lệ thiếu cao,
đặc biệt nếu các nhóm này thường xuyên xuất hiện trong recipe.

**Mẫu thiếu dữ liệu**

Trong 271 nguyên liệu thiếu core nutrition:

- 117 nguyên liệu chỉ thiếu `fat_g`;
- 109 nguyên liệu chỉ thiếu `carbs_g`;
- 13 nguyên liệu thiếu cả `protein_g`, `fat_g` và `carbs_g`;
- 12 nguyên liệu thiếu `protein_g` và `carbs_g`;
- 8 nguyên liệu thiếu `protein_g` và `fat_g`;
- 6 nguyên liệu thiếu `fat_g` và `carbs_g`;
- 4 nguyên liệu chỉ thiếu `protein_g`;
- 2 nguyên liệu thiếu toàn bộ bốn trường.

Đặc biệt, có 269 nguyên liệu vẫn có `energy_kcal` nhưng thiếu ít nhất một
macronutrient.

Điều này có thể tạo ra sự không nhất quán giữa calories và macronutrients
nếu pipeline chuyển các giá trị `NaN` thành 0 khi tạo `recipe_ingredients`.

**Xác minh ảnh hưởng xuống dữ liệu recipe ingredient**

Khi đối chiếu dữ liệu master với `recipe_ingredients.csv`, các giá trị
macronutrient bị thiếu trong master gần như luôn được chuyển thành `0`
ở dữ liệu downstream:

- `protein_g`: 8.589 / 8.620 trường hợp (99,64%);
- `fat_g`: 12.237 / 12.237 trường hợp (100%);
- `carbs_g`: 9.185 / 9.218 trường hợp (99,64%).

**Kết luận**

Pipeline hiện tại gần như đang xử lý giá trị nutrition bị thiếu (`NaN`)
như giá trị dinh dưỡng thực sự bằng `0`.

Điều này làm mất sự khác biệt giữa:

- nguyên liệu thực sự không chứa chất dinh dưỡng đó;
- nguyên liệu chưa có dữ liệu về chất dinh dưỡng đó.

Đây có thể là một trong những nguyên nhân chính tạo ra sự không nhất quán
giữa `calories` và calories ước tính từ protein, fat và carbohydrate ở
`recipe_ingredients`.

**Hướng xử lý đề xuất**

- Không tự động chuyển `NaN` nutrition thành `0` khi scale dữ liệu từ master.
- Giữ `NaN` hoặc trạng thái `unknown` nếu nguồn không cung cấp giá trị.
- Chỉ sử dụng `0` khi dữ liệu nguồn xác nhận giá trị thực sự bằng 0.
- Khi tính nutrition tổng của recipe, cần có thêm thông tin về mức độ đầy đủ
  của dữ liệu thay vì coi tổng hiện tại là hoàn toàn chính xác.

**Mức độ liên quan đến nutrition inconsistency**

Trong 3.010 bản ghi `recipe_ingredients` có mức chênh lệch calories lớn hơn
30%, có 2.398 bản ghi đồng thời bị thiếu ít nhất một macronutrient
(`protein_g`, `fat_g` hoặc `carbs_g`) trong master nutrition dataset.

Tỷ lệ này tương đương 79,67%.

**Kết luận**

Phần lớn vấn đề nutrition inconsistency có thể được giải thích bởi dữ liệu
macronutrient bị thiếu trong master và sau đó được chuyển thành `0` trong
`recipe_ingredients`.

Đây là nguyên nhân chính cần được ưu tiên xử lý trước khi xem xét các nguyên
nhân khác.

#### Vấn đề 11: Một số bản ghi trong master nutrition có calories không nhất quán với macronutrients

**Quan sát**

Trong 478 nguyên liệu có đầy đủ `energy_kcal`, `protein_g`, `fat_g` và
`carbs_g`, có 10 nguyên liệu (2,09%) có mức chênh lệch calories lớn hơn 30%
so với calories ước tính từ macronutrients.

Một số trường hợp có mức sai lệch rất lớn:

- `Kem tươi`: `energy_kcal = 1`, trong khi macro tương ứng khoảng 1.503,6 kcal;
- `Sợi mỳ Quảng`: `energy_kcal = 1`, macro tương ứng khoảng 352,63 kcal;
- `Bột hạt điều (dầu điều)`: `energy_kcal = 1`, macro tương ứng khoảng 234,87 kcal;
- `Sả`: `energy_kcal = 1`, macro tương ứng khoảng 78,2 kcal.

**Đánh giá**

Một số trường hợp có thể có sai số do cách tính năng lượng hoặc thành phần khác,
nhưng các bản ghi có `energy_kcal = 1` trong khi macronutrients cho ra giá trị
năng lượng rất lớn cho thấy khả năng dữ liệu master bị sai hoặc bị ánh xạ sai.

Các nguyên liệu này xuất hiện nhiều lần trong `recipe_ingredients`, do đó một
lỗi nhỏ ở master có thể lan truyền sang nhiều recipe.

**Hướng xử lý đề xuất**

- Kiểm tra lại dữ liệu nguồn của 10 master ingredient bất thường.
- Đặc biệt ưu tiên các bản ghi có `energy_kcal = 1`.
- Không sửa trực tiếp bằng công thức `4P + 9F + 4C` trước khi xác minh nguồn.
- Sau khi sửa master, regenerate nutrition downstream thay vì chỉnh từng
  `recipe_ingredients`.

**Mức độ lan truyền xuống dữ liệu recipe**

Trong nhóm các bản ghi `recipe_ingredients` vẫn không nhất quán sau khi đã
loại các trường hợp master bị thiếu macronutrient, có 431 / 612 bản ghi
(70,42%) liên quan trực tiếp đến các master ingredient mà bản thân
`energy_kcal` không nhất quán với macronutrients.

Các nguyên liệu ảnh hưởng nhiều nhất gồm:

- `Sả`: 293 bản ghi;
- `Ớt bột Hàn Quốc (gochugaru)`: 32;
- `Bột ớt Paprika`: 31;
- `Bột hạt điều (dầu điều)`: 22;
- `Bột quế`: 17;
- `Kem tươi`: 14;
- `Nấm tuyết (Ngân nhĩ)`: 14.

**Đánh giá bổ sung**

Điều này xác nhận rằng lỗi trong master nutrition có khả năng lan truyền trực
tiếp xuống nhiều bản ghi `recipe_ingredients`.

Do đó, việc sửa dữ liệu master và tái tạo dữ liệu downstream sẽ hiệu quả hơn
so với sửa từng bản ghi recipe ingredient riêng lẻ.

#### Kết luận điều tra nutrition inconsistency

Ban đầu phát hiện 3.010 / 63.943 bản ghi `recipe_ingredients`
(4,71%) có mức chênh lệch calories lớn hơn 30% khi so sánh
`calories` với giá trị ước tính từ protein, fat và carbohydrate.

Sau khi điều tra chi tiết, toàn bộ 3.010 trường hợp được giải thích bởi ba nhóm nguyên nhân:

1. **Master nutrition thiếu macronutrient**
   - 2.398 bản ghi, chiếm 79,67%.
   - Các giá trị thiếu trong master gần như luôn bị chuyển thành 0 ở downstream.

2. **Master nutrition bản thân không nhất quán**
   - 431 bản ghi.
   - Liên quan đến các master ingredient có `energy_kcal` không phù hợp với
     protein, fat và carbohydrate, ví dụ `Sả`, `Kem tươi`,
     `Bột hạt điều`, `Bột quế`.

3. **Sai lệch do rounding/scaling**
   - 181 bản ghi.
   - Sau khi tính lại nutrition trực tiếp từ master theo
     `estimated_weight_g`, toàn bộ 181 bản ghi đều nằm trong sai số rounding.
   - Đây không được xem là lỗi dữ liệu thực sự.

**Kết luận**

Nutrition inconsistency không xuất phát từ bước aggregate recipe.

Nguyên nhân chính nằm ở chất lượng và cách xử lý dữ liệu master nutrition,
đặc biệt là:
- macro bị thiếu;
- chuyển `NaN` thành 0;
- một số bản ghi master có giá trị `energy_kcal` bất thường.

Các sai lệch còn lại chỉ là tác động của rounding khi scale nutrition theo
khối lượng nguyên liệu.

### 2.2 `ingredient_categories.csv`

#### Vấn đề 12: Category taxonomy giữa master ingredient và danh mục chuẩn chưa đồng nhất

**Quan sát**

`ingredient_categories.csv` định nghĩa 15 category, trong khi
`master_ingredients_nutrition.csv` đang sử dụng 25 category khác nhau.

Có 11 category được sử dụng trong master nhưng không tồn tại trong danh mục
category chuẩn, ảnh hưởng đến tổng cộng 62 nguyên liệu.

Các category bị ảnh hưởng nhiều nhất gồm:

- `Rau củ quả và sản phẩm chế biến`: 33 nguyên liệu;
- `Gia vị`: 9;
- `Gia vị và nước chấm`: 9;
- một số nhóm khác như `Đậu, đỗ và sản phẩm chế biến`,
  `Hạt và sản phẩm chế biến`, `Đồ ngọt`, `Thủy hải sản`,...

Ngoài ra, category `Thức ăn truyền thống` có trong danh mục chuẩn nhưng
không được sử dụng trong master ingredient.

**Đánh giá**

Dữ liệu đang tồn tại nhiều hệ taxonomy category khác nhau.

Một số category có ý nghĩa gần giống nhau, ví dụ:

- `Gia vị`
- `Gia vị và nước chấm`
- `Gia vị, nước chấm`

Điều này có thể gây khó khăn khi filter, thống kê hoặc sử dụng category
làm feature cho recommendation/model.

Không nên merge category tự động chỉ dựa trên tên gần giống nhau vì một số
nhóm có thể không hoàn toàn tương đương.

**Hướng xử lý đề xuất**

- Xác định một taxonomy chuẩn duy nhất, ưu tiên danh mục trong
  `ingredient_categories.csv`.
- Xây dựng mapping từ các category ngoài danh mục chuẩn về category chuẩn.
- Kiểm tra thủ công các nhóm có ý nghĩa chưa rõ trước khi mapping.
- Sau khi chuẩn hóa, đảm bảo mọi `category_vi` trong master đều tồn tại trong
  `ingredient_categories.csv`.

**Kiểm tra khả năng chuẩn hóa**

Một bảng mapping thử nghiệm được xây dựng từ 11 category ngoài danh mục chuẩn
về 15 category trong `ingredient_categories.csv`.

Kết quả:

- 62 / 62 master ingredient đang dùng category ngoài chuẩn đều được bao phủ;
- sau khi áp dụng mapping đề xuất, không còn category undefined.

Một số mapping có độ chắc chắn cao, ví dụ:

- `Gia vị` → `Gia vị, nước chấm`;
- `Gia vị và nước chấm` → `Gia vị, nước chấm`;
- `Thủy hải sản` → `Thủy sản và sản phẩm chế biến`;
- `Đồ ngọt` → `Đồ ngọt (đường, bánh, mứt, kẹo)`.

Một số mapping như nhóm `Đậu, đỗ`, `Đậu phụ` hoặc `Đồ uống và nước`
nên được xác nhận lại về mặt taxonomy trước khi sửa dữ liệu.

**Kết luận**

Vấn đề category hiện tại có thể được xử lý bằng một bước canonical mapping
trước khi xuất dữ liệu processed.

### 2.3 `ingredient_alias_map.json`

#### Vấn đề 13: Alias map có tham chiếu tới master ingredient không tồn tại

**Quan sát**

`ingredient_alias_map.json` có 4.684 alias và tham chiếu tới 745 master code
khác nhau.

Qua đối chiếu với `master_ingredients_nutrition.csv`, phát hiện 2 code được
alias map tham chiếu nhưng không tồn tại trong master:

- `10010`
- `7099`

Ngoài ra có 6 master ingredient không có alias nào trỏ tới:

- `12013`
- `12079`
- `20103`
- `20104`
- `3020011`
- `7026`

**Đánh giá**

Hai code `10010` và `7099` là broken reference và có thể khiến alias matching
trả về một master ingredient không tồn tại.

Việc một master ingredient không có alias chưa nhất thiết là lỗi, vì vẫn có thể
được match bằng tên chính thức hoặc các phương pháp khác.

**Hướng xử lý đề xuất**

- Kiểm tra các alias đang trỏ tới `10010` và `7099`.
- Xác minh hai code này đã bị xóa, đổi mã hay alias map đang dùng mã cũ.
- Cập nhật alias map về master code hợp lệ.
- Không cần bắt buộc mọi master ingredient phải có alias.

**Điều tra thêm**

Có 3 alias đang trỏ tới 2 master code không tồn tại:

- `kem sữa béo` → `10010`
- `kem tươi` → `10010`
- `thịt ếch` → `7099`

Đáng chú ý, master hiện có nguyên liệu `Kem tươi` với code `12079`,
cho thấy alias `kem tươi` có khả năng đang tham chiếu tới một code cũ.

**Hướng xử lý bổ sung**

- Xác minh `10010` có phải code cũ của `Kem tươi` hay không.
- Nếu đúng, cập nhật các alias liên quan sang code `12079`.
- Tìm master ingredient tương ứng với `thịt ếch` để xác định code thay thế
  cho `7099`.

**Xác minh candidate thay thế**

Đối với alias `thịt ếch`, master hiện có:

- `7080 - Ếch (thịt đùi)`

và dữ liệu `recipe_ingredients` cũng đã sử dụng code này cho nhiều bản ghi
`thịt ếch`. Vì vậy `7099` nhiều khả năng là một code cũ hoặc không còn hợp lệ.

Đối với `kem tươi`, có hai candidate:

- `12079 - Kem tươi`;
- `20070 - Whipping cream (Kem tươi whipping)`.

Qua kiểm tra:

- `12079` có dữ liệu nutrition bất thường (`energy_kcal = 1` nhưng
  `protein_g = 335`);
- `20070` có dữ liệu nutrition hợp lý hơn;
- nhiều công thức sử dụng cụm `kem tươi (whipping cream)`, phù hợp với
  master ingredient `20070`.

**Đề xuất**

- Xác minh và cập nhật `thịt ếch` từ code `7099` sang `7080`.
- Với `kem tươi` và `kem sữa béo`, ưu tiên xem xét code `20070`, nhưng cần
  xác nhận lại semantics/source trước khi sửa alias map.
- Không nên chuyển alias sang `12079` khi bản ghi master này vẫn đang có
  vấn đề về nutrition.

Ngoài các broken reference nêu trên, không phát hiện alias collision sau khi
chuẩn hóa chữ thường, khoảng trắng và Unicode.

### 2.4 `traditional_dishes_nutrition.csv`

**Cập nhật 2026-09-10 — lỗi parser fat đã sửa.** Các quan sát thiếu fat và
đề xuất sửa mapping bên dưới là kết quả điều tra trước bản sửa, được giữ lại
để truy vết; không còn mô tả trạng thái hiện tại của cột `fat_g`.

- Nguyên nhân: `strip().lower()` rồi exact match bỏ qua cả `Chất béo (Fat)`
  và `Total lipid (Fat)` trong raw.
- Parser hiện chuẩn hóa Unicode NFC, chữ hoa/thường và khoảng trắng;
  bổ sung alias `total lipid`. Nhãn có ngoặc chỉ được nhận khi cả hai phần
  là alias đã biết của cùng nutrient; giữ ưu tiên exact match và không bỏ
  qualifier tùy ý. Script audit dùng chung resolver này.
- Chạy `python -m scripts.regenerate_traditional_dishes` để parse lại raw,
  chỉ ghi CSV món truyền thống; script từ chối ghi nếu cột khác thay đổi.
  Không chạy crawler chính vì entry point đó ghi cả raw và master catalog.
- Số dòng: **78**; thiếu `fat_g`: **78 → 0**; khôi phục **78** giá trị từ raw,
  không điền thủ công và không ước tính.
- `fat_g` (g): min **0,13**, median **3,15**, mean **5,4132051282**,
  max **32,65**; số giá trị âm: **0**.
- Chỉ cột `fat_g` thay đổi; schema, thứ tự, ID và các giá trị khác giữ nguyên.
  Kết quả render lặp lại giống nhau.
- `Muối vừng` (`15074`): raw fat **32,65 g** → processed `fat_g = 32.65`.
  Raw `energy = 1` và processed `energy_kcal = 1` vẫn giữ nguyên:
  **bất thường năng lượng nguồn chưa được giải quyết**.
- Không regenerate master nutrition, recipe/canonicalization hoặc aliases.
- Kiểm chứng: **75 tests passed** trong `tests/test_viendinhduong_parser.py`;
  audit `scripts/eda/eda_raw_nutrient_mapping.py` còn **0** cặp nhãn không map.
  So với Git chỉ đổi 78 ô `fat_g`; hash các file raw/interim/processed khác
  không đổi; regenerate lần hai cho cùng kết quả; `git diff --check` đạt.

#### Vấn đề 114 Toàn bộ dữ liệu món ăn truyền thống bị thiếu `fat_g` — ĐÃ SỬA

**Quan sát**

Trong `traditional_dishes_nutrition.csv` có 78 món ăn.

Kết quả kiểm tra bốn trường dinh dưỡng cốt lõi cho thấy:

- `energy_kcal`: đầy đủ 100%;
- `protein_g`: đầy đủ 100%;
- `carbs_g`: đầy đủ 100%;
- `fat_g`: thiếu 78 / 78 bản ghi, tương đương 100%.

Như vậy toàn bộ dataset món ăn truyền thống đều thiếu thông tin chất béo.

**Đánh giá**

Đây là missing có tính hệ thống, không phải một số bản ghi bị thiếu ngẫu nhiên.

Việc thiếu hoàn toàn `fat_g` làm dataset không thể cung cấp đầy đủ thông tin
macronutrient nếu được sử dụng cho chức năng theo dõi dinh dưỡng hoặc làm feature
cho recommendation.

Không nên mặc định `fat_g = 0`, vì nhiều món như bánh chiên, bánh chưng,
bánh mì patê,... rõ ràng có khả năng chứa chất béo.

**Hướng xử lý đề xuất**

- Kiểm tra nguồn dữ liệu gốc để xác định liệu `fat_g` có tồn tại nhưng chưa
  được extract hay không.
- Nếu nguồn không cung cấp fat, cân nhắc bổ sung từ một nguồn dinh dưỡng khác.
- Có thể sử dụng calories, protein và carbohydrate để ước tính fat như một
  phép kiểm tra EDA, nhưng không nên ghi đè dữ liệu thật trước khi xác minh.

**Điều tra khả năng ước tính `fat_g`**

Thử ước tính lượng chất béo theo công thức:

`fat ≈ (energy_kcal - 4 × protein_g - 4 × carbs_g) / 9`

Kết quả:

- 77 / 78 món cho giá trị `fat_g` ước tính không âm;
- trung vị khoảng 3,18 g;
- trung bình khoảng 5,30 g;
- giá trị lớn nhất khoảng 40,31 g.

Điều này cho thấy phần lớn dữ liệu calories, protein và carbohydrate có thể
được sử dụng để ước tính fat như một phép kiểm tra.

Tuy nhiên, `Muối vừng` cho ra `fat_g` âm khoảng -14,06 g do
`energy_kcal = 1` không phù hợp với lượng protein và carbohydrate hiện có.

**Kết luận bổ sung**

Không nên tự động điền `fat_g` bằng giá trị suy ra trước khi xác minh nguồn.
Công thức trên chỉ nên được dùng để phát hiện dữ liệu bất thường hoặc tạo
candidate để kiểm tra.

Bản ghi `Muối vừng` cần được xác minh lại riêng vì các trường nutrition hiện tại
không nhất quán.

**Độ đầy đủ của các trường dinh dưỡng khác**

Ngoài việc `fat_g` thiếu 100%, nhiều vi chất cũng gần như không có dữ liệu.

Các trường thiếu 100% gồm:

- `fat_g`;
- `vitamin_b1_mg`;
- `vitamin_b3_mg`;
- `vitamin_b5_mg`;
- `vitamin_b6_mg`;
- `vitamin_c_mg`;
- `retinol_mcg`;
- `vitamin_a_rae_mcg`;
- `selenium_mcg`;
- `copper_mg`;
- `magnesium_mg`;
- `folate_total_mcg`;
- `folate_food_mcg`.

Một số trường khác chỉ có dữ liệu cho 1 / 78 món:

- `sugar_g`;
- `sodium_mg`;
- `potassium_mg`;
- `manganese_mg`;
- `vitamin_b2_mg`.

Ngược lại, một số trường có độ phủ tương đối tốt:

- `energy_kcal`: 78 / 78;
- `protein_g`: 78 / 78;
- `carbs_g`: 78 / 78;
- `calcium_mg`: 78 / 78;
- `fiber_g`: 73 / 78;
- `phosphorus_mg`: 74 / 78;
- `iron_mg`: 75 / 78;
- `zinc_mg`: 75 / 78;
- `water_g`: 76 / 78.

**Đánh giá**

Dataset món ăn truyền thống hiện phù hợp hơn với việc cung cấp một số chỉ số
dinh dưỡng cơ bản, nhưng chưa đủ độ phủ để sử dụng như một nguồn nutrition
đầy đủ cho vitamin, khoáng chất và macronutrient.

Các trường có tỷ lệ thiếu gần 100% không nên được sử dụng trực tiếp làm feature
cho model hoặc hiển thị như dữ liệu dinh dưỡng đầy đủ.

**Hướng xử lý đề xuất**

- Xác định tập trường dinh dưỡng có độ phủ đủ cao để sử dụng.
- Không mặc định các trường thiếu là bằng 0.
- Nếu hệ thống cần theo dõi vi chất chi tiết, cần bổ sung dữ liệu từ nguồn khác
  hoặc quay lại nguồn gốc để kiểm tra khả năng extract thêm.

**Kiểm tra outlier**

Kiểm tra IQR trên các trường có độ phủ đầy đủ phát hiện:

- 1 outlier ở `energy_kcal`: `Bánh mè` với 482 kcal;
- 4 outlier ở `protein_g`;
- không có outlier ở `carbs_g`.

Các giá trị cao như `Bánh mè`, `Thịt xiên nướng` hoặc `Chả quế`
chưa đủ cơ sở để xem là lỗi vì vẫn có thể hợp lý theo đặc điểm món ăn.

Riêng `Muối vừng` có `energy_kcal = 1` nhưng `protein_g = 18,11`
và `carbs_g = 13,77`, cho thấy bản ghi này không nhất quán rõ ràng.

Do đó không nên tự động loại outlier theo IQR; chỉ nên dùng outlier
để xác định các bản ghi cần kiểm tra thêm.

**Xác minh với dữ liệu raw**

Khi truy ngược bản ghi `Muối vừng` (`code = 15074`) về
`food_nutrition_raw.json`, dữ liệu raw có:

- `protein = 18,11 g`;
- `fat = 32,65 g`;
- `carbohydrate = 13,77 g`;
- `energy = 1 kcal`.

Điều này cho thấy hai vấn đề khác nhau:

1. Giá trị `energy = 1` đã tồn tại ngay trong dữ liệu raw, do đó lỗi
   energy của `Muối vừng` không phát sinh từ preprocessing.

2. Raw có trường `Chất béo (Fat)`, nhưng `fat_g` trong
   `traditional_dishes_nutrition.csv` lại bị thiếu. Điều này cho thấy
   khả năng bước transform raw → processed chưa ánh xạ trường fat
   cho nhóm `Thức ăn truyền thống`.

**Hướng xử lý bổ sung**

- Kiểm tra logic mapping `Chất béo (Fat)` sang `fat_g` trong preprocessing.
- Không tự sửa `energy_kcal = 1` của `Muối vừng` nếu chưa xác minh lại nguồn.
- Sau khi sửa mapping fat, regenerate `traditional_dishes_nutrition.csv`
  từ raw thay vì điền thủ công từng dòng.

**Nguyên nhân đã xác định trong preprocessing**

Kiểm tra trực tiếp toàn bộ 78 món thuộc nhóm `Thức ăn truyền thống`
trong dữ liệu raw cho thấy trường chất béo thực tế có tồn tại.

Raw sử dụng nutrient label:

- `Chất béo (Fat)`
- `Total lipid (Fat)`

Trong khi `NUTRIENT_KEY_MAP` của `crawler/crawl_viendinhduong.py`
chỉ định nghĩa các key:

- `chất béo`
- `fat`

Logic parser hiện chỉ thực hiện `strip().lower()` rồi exact match với
`NUTRIENT_KEY_MAP`. Vì vậy `Chất béo (Fat)` không khớp với key nào và
`fat_g` bị giữ ở `None`.

Kết quả kiểm tra cho thấy:

- lỗi xảy ra ở 78 / 78 món truyền thống;
- đây là nguyên nhân trực tiếp khiến `fat_g` thiếu 100% trong
  `traditional_dishes_nutrition.csv`;
- không phát hiện nutrient label nào khác trong nhóm món truyền thống
  bị bỏ qua do cùng cơ chế exact-match.

**Đề xuất**

- Chuẩn hóa nutrient label trước khi lookup hoặc bổ sung các variant thực tế
  từ raw vào `NUTRIENT_KEY_MAP`.
- Sau khi sửa parser, regenerate `traditional_dishes_nutrition.csv`
  từ dữ liệu raw thay vì điền `fat_g` thủ công.
- Không tự sửa `energy_kcal = 1` của `Muối vừng` trước khi xác minh lại nguồn,
  vì giá trị này đã tồn tại ngay trong raw.

## 4. Mức độ ưu tiên xử lý

### Ưu tiên cao – Cần xử lý trước khi sử dụng dataset cho nutrition/recommendation

1. **Fallback `estimated_weight_g = 10` cho nguyên liệu thiếu định lượng**

   Quy tắc fallback này ảnh hưởng tới 4.125 / 5.641 recipe (73,13%). Có 1.471 recipe nhận hơn 20% tổng calories từ các nguyên liệu fallback và 550 recipe nhận hơn 50%. Vì vậy đây là vấn đề có khả năng làm sai trực tiếp nutrition ở cấp recipe.

2. **Master nutrition thiếu macronutrient và pipeline chuyển `NaN` thành `0`**

   Có 271 / 749 master ingredient thiếu ít nhất một trường nutrition cốt lõi. Việc các giá trị thiếu gần như luôn bị chuyển thành `0` ở downstream giải thích 2.398 / 3.010 trường hợp nutrition inconsistency (79,67%).

3. **Một số master nutrition có giá trị bất thường**

   Một số master ingredient có `energy_kcal` không phù hợp rõ ràng với protein, fat và carbohydrate. Các master bất thường này lan truyền xuống ít nhất 431 bản ghi recipe ingredient không nhất quán.

4. **Parser làm mất toàn bộ `fat_g` của dataset món ăn truyền thống — ĐÃ SỬA**

   Trước sửa, `traditional_dishes_nutrition.csv` thiếu `fat_g` ở 78 / 78 món do exact-match nutrient label. Sau sửa parser và regenerate từ raw ngày 2026-09-10: thiếu 0 / 78. Bất thường raw energy của `Muối vừng` vẫn chưa giải quyết.

5. **Trạng thái `UNMATCHED` không nhất quán với `master_ingredient_code`**

   Có 459 / 8.194 dòng `UNMATCHED` vẫn giữ `master_ingredient_code`. Điều này vi phạm invariant của bước mapping và có nguy cơ khiến downstream sử dụng candidate confidence thấp như một match hợp lệ.

### Ưu tiên trung bình – Nên xử lý để cải thiện độ tin cậy của matching và dữ liệu chuẩn hóa

1. **Tỷ lệ nguyên liệu chưa match được với master còn cao**

   Có 7.735 / 63.943 bản ghi không có `master_ingredient_code`, tương đương khoảng 12,10%. Nguyên nhân chủ yếu liên quan đến `cleaned_name` còn chứa nhiều nguyên liệu, mô tả chế biến, lựa chọn thay thế hoặc alias chưa được bao phủ.

   Nên ưu tiên cải thiện preprocessing và alias trước khi cân nhắc giảm threshold matching.

2. **Qwen extraction và logic mapping có nguy cơ tạo false-positive match**

   Một số output của Qwen vẫn chứa nhiều nguyên liệu hoặc không phải tên nguyên liệu hợp lệ. Sau đó `map_clean_to_master()` sử dụng substring matching theo kiểu first-match-wins, nên input mơ hồ có thể bị gán vào một master ingredient duy nhất.

   Ngoài ra, `match_confidence = 0.98` của phần lớn `QWEN_LLM_MATCH` là giá trị hard-code, không phải confidence đã được calibration. Vì vậy không nên dùng score này như xác suất đúng của prediction.

3. **Category taxonomy giữa master ingredient và danh mục chuẩn chưa đồng nhất**

   Master ingredient đang sử dụng 25 category trong khi danh mục chuẩn chỉ định nghĩa 15 category. Có 11 category ngoài chuẩn, ảnh hưởng tới 62 master ingredient.

   Vấn đề này có thể gây sai lệch khi filter, thống kê hoặc dùng category làm feature. Nên xây dựng canonical mapping trước khi xuất dataset processed cuối cùng.

4. **Alias map có broken reference**

   Có 3 alias đang trỏ tới 2 `master_ingredient_code` không tồn tại trong master dataset (`10010` và `7099`).

   Các alias này cần được xác minh và cập nhật về code hợp lệ trước khi sử dụng alias matching trong pipeline.

### Ưu tiên thấp / Theo dõi – Chưa cần xử lý ngay

1. **Nhiều recipe có tên giống nhau sau khi chuẩn hóa**

   Có 251 dòng thuộc các nhóm recipe trùng tên sau khi chuẩn hóa, nhưng các bản ghi thường khác `source_url`, nguồn dữ liệu, khẩu phần, nguyên liệu hoặc nutrition.

   Đây không phải duplicate hoàn toàn. Không nên xóa recipe chỉ dựa trên `name`. Nếu sau này cần nhóm nhiều phiên bản của cùng một món, có thể bổ sung `canonical_dish_name`.

2. **Một số master ingredient có tên tiếng Việt giống nhau nhưng khác semantics**

   Trong 749 master ingredient chỉ có 8 dòng thuộc 4 nhóm tên bị trùng sau khi chuẩn hóa.

   Một số trường hợp thực sự là khác trạng thái hoặc loại nguyên liệu, ví dụ `Tôm đồng` dạng tươi và khô; một số trường hợp khác cần kiểm tra mapping như `Cần tây`.

   Phạm vi ảnh hưởng hiện nhỏ, nên chưa cần ưu tiên trước các lỗi nutrition và matching lớn hơn. Tuy nhiên, không nên deduplicate master ingredient chỉ dựa trên `name_vi`.

3. **`processed/recipes` hiện giống hoàn toàn dữ liệu `interim`**

   Các file recipe trong `data/processed/recipes` hiện không có khác biệt nội dung so với dữ liệu tương ứng trong `data/interim`.

   Đây chưa nhất thiết là lỗi. Cần xác nhận với nhóm xem `processed/recipes` có được thiết kế chỉ như một output copy hay được kỳ vọng là dữ liệu đã qua thêm bước làm sạch.

   Nếu đây là hành vi có chủ ý thì không cần xử lý.

## 5. Kết luận tổng hợp

EDA cho thấy dataset hiện tại có thể tiếp tục sử dụng cho quá trình phát triển và thử nghiệm, nhưng chưa nên xem là production-ready cho các chức năng phụ thuộc mạnh vào nutrition hoặc recommendation.

Các vấn đề cần ưu tiên xử lý trước gồm:

1. **Fallback khối lượng 10g đang ảnh hưởng tới phạm vi rất lớn**
   - 4.125 / 5.641 recipe có ít nhất một nguyên liệu sử dụng fallback.
   - Một số recipe phụ thuộc phần lớn hoặc toàn bộ nutrition vào khối lượng giả định này.

2. **Master nutrition còn thiếu dữ liệu và pipeline đang làm mất thông tin missing**
   - 271 / 749 master ingredient thiếu ít nhất một trường nutrition cốt lõi.
   - Các giá trị `NaN` gần như luôn bị chuyển thành `0` ở downstream.
   - Đây là nguyên nhân chính của phần lớn nutrition inconsistency.

3. **Một số giá trị nutrition trong master bản thân đã bất thường**
   - Một số ingredient có `energy_kcal` không phù hợp rõ ràng với macronutrients.
   - Các lỗi này lan truyền xuống nhiều recipe ingredient.

4. **Lỗi preprocessing fat của món truyền thống — ĐÃ SỬA ngày 2026-09-10**
   - Đã khôi phục 78 / 78 giá trị fat từ raw bằng parser đã sửa.
   - `Muối vừng` vẫn giữ `energy_kcal = 1`; bất thường nguồn này chưa giải quyết.

5. **Trạng thái matching chưa nhất quán**
   - Có 459 dòng `UNMATCHED` vẫn giữ `master_ingredient_code`.
   - Qwen mapping cũng có nguy cơ false-positive do output đa nguyên liệu, substring matching và confidence `0.98` hard-code.

Ngoài các vấn đề trên, taxonomy category, alias map và độ phủ matching cũng nên được cải thiện, nhưng có thể xử lý sau các lỗi trực tiếp ảnh hưởng đến nutrition.

### Đề xuất thứ tự xử lý

1. Sửa logic fallback `estimated_weight_g`.
2. Giữ đúng semantics của `NaN` thay vì chuyển thành `0`.
3. Xác minh và sửa các master nutrition bất thường.
4. **Đã hoàn thành:** sửa parser `fat_g` và regenerate riêng CSV món truyền thống.
5. Chuẩn hóa invariant của `UNMATCHED`.
6. Sau đó mới cải thiện Qwen extraction, alias và category taxonomy.

Sau khi các bước trên được xử lý, nên regenerate lại dữ liệu downstream và chạy lại các script EDA để xác minh rằng các lỗi đã giảm hoặc được loại bỏ.


## Missing nutrition propagation fix (2026-09-10)

**Status: fixed at ingredient level; master completeness and aggregate completeness remain unresolved.**

### Root cause and implementation

`master_ingredients_nutrition.csv` uses blank cells for unavailable nutrition.
`VietnameseIngredientMatcher._load_catalog()` reads these through `csv.DictReader`
as empty strings and preserves them in the catalog. The first lossy transformation
is the explicit `float(matched_item.get(field) or 0)` default in both
`nlp/pipeline.py` processing paths and `crawler/post_processing.py`.
The latter also had an exception fallback setting all four nutrients to zero.
`scripts/run_qwen_line_pipeline.py` repeated the empty-to-zero conversion before
one-decimal scaling when updating matches/weights, then copied inherited rows to
processed exports. CSV/JSON serialization does not cause the initial loss;
no production `fillna(0)` is responsible on these inspected paths.
The crawler pipeline export passes nutrition through without repairing missingness.

`nlp/nutrition.py` now parses blanks, None and numeric/string NaN as None and
scales only known values. Known zero and positive values retain their existing
rounding (two decimals in NLP/crawler, one decimal in Qwen). Qwen preserves
existing string representation for known values and restores master nulls on
inherited rows as well as recalculated rows. Missing values serialize as blank CSV
cells and JSON null, without literal NaN or the string "None".

The dedicated regeneration command uses current processed ingredient rows and
existing master-code links; it restores only fields whose master value is missing.
It leaves every other field exactly unchanged, including existing rounding,
matching, weights, row IDs/order and source provenance. Only
`data/processed/recipes/recipe_ingredients.csv` and its JSON companion were
regenerated. No master, raw, interim, canonical, alias, category or recipe-total
file was regenerated. The broad Qwen/crawler jobs were not run because they also
write unrelated artifacts.

### Before/after validation

Baseline: Git commit `242ff45c123d24670ad3df23ffe1a2cc2b24a35d`.

| Master field (downstream) | Missing master records | Linked ingredient instances | Zero before | Missing after | True-zero instances still zero |
| --- | ---: | ---: | ---: | ---: | ---: |
| energy_kcal (calories) | 2 | 0 | 0 | 0 | 358 |
| protein_g | 39 | 8,546 | 8,546 | 8,546 | 528 |
| fat_g | 146 | 12,163 | 12,163 | 12,163 | 554 |
| carbs_g | 142 | 9,144 | 9,144 | 9,144 | 538 |

19,499 distinct ingredient rows of 63,943 changed, spanning 5,403 recipes.
29,853 fabricated zero cells became missing. All other values are unchanged;
there were zero unexpected numeric changes. All true-zero linked instances
were zero both before and after. The two missing-energy masters have no linked
instances. All 27 other data files were hash-checked unchanged during generation.
Ingredient IDs are unique, recipe references valid, and CSV/JSON nutrition agrees.
Repeated regeneration produced identical output hashes (recorded in the JSON report).

### Nutrition inconsistency rerun

The historical formula is preserved exactly:
`abs(calories - (protein_g * 4 + carbs_g * 4 + fat_g * 9)) / calories * 100 > 30`.
Comparison requires all four values and positive calories. Missing macros are
excluded, not treated as zero. Operation order matters for five floating-point
boundary rows; keeping the historical order reproduces the prior EDA counts.

- Before: **3,010** inconsistent ingredient rows.
- After: **612** comparable inconsistent rows.
- **2,398** formerly inconsistent rows now lack a macro and are not valid formula
  comparisons. This is a correction of missingness, not repaired nutrition.
- Remaining: **431** rows linked to inconsistent complete master records, and
  **181** rows consistent with the historical scaling/rounding tolerance
  (absolute error <=1 kcal and <=0.11 g for each macro).
- No remaining rows outside those categories under that tolerance. Tolerance is
  an EDA classification, not proof that source nutrition is correct.

### Aggregate semantics and remaining issues

Qwen rollups use `float(value or 0.0)` and zero-initialized sums: unknown contributes
zero to a sum of known contributions. Crawler post-processing previously summed
already-defaulted values; it now explicitly skips missing contributions to retain
that same behavior, including its existing conversion of nonpositive totals to
None. NLP portion estimation itself does not aggregate recipes. EDA pandas sums
also skip missing values by default.

The audit verifies that every recipe/field ingredient sum under the legacy policy
is numerically identical before and after. Existing recipe-total files are unchanged.
Those totals can still be incomplete, especially for the 5,403 affected recipes;
they must not be interpreted as certified complete nutrient totals. Changing totals
to unknown or adding completeness flags requires a separate business decision.

Master missingness/incorrect nutrition, the 10g fallback, UNMATCHED rows with codes,
Qwen false positives, aliases and category issues remain unresolved. Canonical
ingredient files and interim snapshots intentionally retain their previous values;
this update applies to the named processed ingredient exports only. Regenerating
canonical outputs is outside this task.

### Reproduction and tests

- `python -m scripts.eda.validate_missing_nutrition --write` restores processed
  ingredient nulls and writes the validation JSON. Use `--before-ref` with the
  baseline commit above after HEAD changes.
- `python -m scripts.eda.validate_missing_nutrition` verifies existing outputs
  without writing data.
- `uv run --with pytest python -m pytest tests/test_missing_nutrition.py tests/test_data_integrity.py -q -p no:cacheprovider`
  ? **30 passed**. Focused tests cover missing/zero/positive scaling, zero factor,
  field isolation, CSV/JSON round trips, idempotence, both NLP paths, crawler
  calculation and legacy aggregation, Qwen calculation, and formula exclusion.
  Production calculation blocks are executed without loading GPU models.


## Master energy source investigation (2026-09-10)

**Status: unresolved source anomalies; no deterministic transformation bug found in the 10 target records.**

Baseline: `c8c45e7ceef72a10810e61e019294f633f0678fe`. No nutrition value was corrected or inferred.
The audit uses complete energy/protein/fat/carbs and the historical expression
`abs(E - (P*4 + C*4 + F*9)) / E * 100 > 30`. Positive energy is required;
478 of 749 masters have complete core fields, including one zero-energy record
excluded from division. Missing macros never become valid comparisons.

### Per-record diagnosis (before and after are identical)

In the tuple columns, order is energy kcal / protein g / fat g / carbs g.
Raw means the committed API snapshot, not an independently verified current website.

| Code | Current Vietnamese name | Processed values | Repository source values | Origin | Macro estimate (diagnostic only) | Difference % | Flagged ingredient rows | Diagnosis / proposed action |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| 1045 | Sợi mỳ Quảng | 1 / 5.32 / 0.27 / 82.23 | 1 / 5.32 / 0.27 / 82.23 | Raw API JSON | 352.63 | 35163.000000 | 0 | Raw energy is already 1; no repository-backed replacement. No automatic fix; source verification required. |
| 12079 | Kem tươi | 1 / 335 / 2.4 / 35.5 | 1 / 335 / 2.4 / 35.5 | Raw API JSON | 1503.60 | 150260.000000 | 14 | Raw energy is already 1; no repository-backed replacement. Raw protein is already 335 g; decimal/column correction cannot be established. No automatic fix; source verification required. |
| 13024 | Sả | 1 / 0.8 / 1 / 16.5 | 1 / 0.8 / 1 / 16.5 | Raw API JSON | 78.20 | 7720.000000 | 293 | Raw energy is already 1; no repository-backed replacement. No automatic fix; source verification required. |
| 13032 | Nước sốt cà chua (tương cà) | 1 / 1.1 / 0.1 / 27.4 | 1 / 1.1 / 0.1 / 27.4 | Raw API JSON | 114.90 | 11390.000000 | 8 | Raw energy is already 1; no repository-backed replacement. No automatic fix; source verification required. |
| 13056 | Bột hạt điều (dầu điều) | 1 / 11.5 / 2.23 / 42.2 | 1 / 11.5 / 2.23 / 42.2 | Raw API JSON | 234.87 | 23387.000000 | 22 | Raw energy is already 1; no repository-backed replacement. No automatic fix; source verification required. |
| 13073 | Nước ướp gà nướng | 1 / 0.82 / 0.63 / 40.8 | 1 / 0.82 / 0.63 / 40.8 | Raw API JSON | 172.15 | 17115.000000 | 0 | Raw energy is already 1; no repository-backed replacement. No automatic fix; source verification required. |
| 20009 | Bột quế | 247 / 4.0 / 1.2 / 80.6 | 247 / 4.0 / 1.2 / 80.6 | Manual extension | 349.20 | 41.376518 | 17 | Extension literals match; no record-specific source reference or authoritative replacement. No automatic fix; source verification required. |
| 20018 | Ớt bột Hàn Quốc (gochugaru) | 318 / 12.0 / 17.3 / 56.6 | 318 / 12.0 / 17.3 / 56.6 | Manual extension | 430.10 | 35.251572 | 32 | Extension literals match; no record-specific source reference or authoritative replacement. No automatic fix; source verification required. |
| 20068 | Nấm tuyết (Ngân nhĩ) | 200 / 8.0 / 0.6 / 65.0 | 200 / 8.0 / 0.6 / 65.0 | Manual extension | 297.40 | 48.700000 | 14 | Extension literals match; no record-specific source reference or authoritative replacement. No automatic fix; source verification required. |
| 20084 | Bột ớt Paprika | 282 / 14.1 / 12.9 / 54.0 | 282 / 14.1 / 12.9 / 54.0 | Manual extension | 388.50 | 37.765957 | 31 | Extension literals match; no record-specific source reference or authoritative replacement. No automatic fix; source verification required. |

### Pipeline evidence and limits

- `crawler/crawl_viendinhduong.py:parse_food_item` copies `item['energy']`
  directly. Each of the six raw-backed targets already has numeric energy 1.
  Protein, fat and carbohydrate source entries have numeric JSON values and g
  units. The current exact/synonym label parser reproduces all four core values
  for each target. No numeric separator conversion, unit conversion, incorrect
  label mapping, or downstream overwrite explains these discrepancies.
- `12079` already has protein 335 in the raw Protein entry. A shifted column or
  missing decimal might be suspected, but neither correction is established by
  repository evidence. Both energy and macros require verification.
- Raw names for `13032` and `13056` are respectively `N??c s?t c? chua` and
  `B?t h?t ?i?u ??`; the changed display names do not change their core nutrition.
  The exact current list uses `N??c s?t c? chua (t??ng c?)`, not the example label
  `T??ng c? (ketchup)`.
- All four extension tuples exactly match `nlp/master_extensions.py`.
  That file states a general USDA/Vietnamese composition origin, but provides
  no per-record citation, food identifier, source snapshot or authoritative
  correction rule. Their stored fiber values are 53.1, 27.2, 25.0 and 34.0 g
  respectively. Nutrient definitions require verification; the formula flag
  alone does not establish which source field is wrong.
- Git history: raw, extensions and these master rows first appear in `ae51d8b`.
  Historical `nlp/clean_master_ingredients.py` copies extension fields by column
  name; `scripts/update_master_and_aliases.py` and `scripts/sync_master_csv.py`
  append missing extension codes using the same field-name mapping.
  `scripts/append_new_extensions.py` contains literal extension data.
  No recoverable corrected target values were found. The later master change
  in `b912a43` only appends `20104` and `20103`.
- The existing fat-label parser fix is already present and correctly handles
  these targets. Re-running the broad crawler/legacy merge jobs would also
  overwrite unrelated catalog/alias/category/raw artifacts, so none were run.

### Before/after and validation

| Metric | Before | After |
| --- | ---: | ---: |
| Inconsistent complete-core masters | 10 | 10 |
| Inconsistent recipe ingredient rows | 612 | 612 |
| Linked to inconsistent masters | 431 | 431 |
| Within historical scaling/rounding tolerance | 181 | 181 |
| Other mismatch / missing master categories among flagged rows | 0 | 0 |
| Ingredient rows excluded for missing core values | 19,499 | 19,499 |

Zero masters fixed; zero ingredient rows resolved by master corrections.
The remaining 181 rows meet the existing absolute tolerance of <=1 kcal and
<=0.11 g per macro against master values scaled by recorded weight. This is an
EDA category, not proof of source correctness. All 10 records above remain
unresolved for their stated reasons; the overall finding is not fixed.

Implementation is limited to a read-only audit and this documentation:
`scripts/eda/audit_master_energy.py` traces source values, compares every master
and ingredient CSV cell to HEAD, and verifies hashes of all data files during
execution. `--write-report` writes only `reports/eda/master_energy_audit.json`,
including full raw nutrient evidence, per-record counts and data-file hashes.
All available non-target values, missing fields, aliases, categories, matching,
weights, source/interim files and canonical outputs remain unchanged.

Validation: `python -m scripts.eda.audit_master_energy --write-report` passes,
including two independently built, identical audit results. No dataset
regeneration was needed. No bug-fix tests were added because no production bug
was fixed. Existing focused regressions passed: **101 tests**, using
`uv run --with pytest --with requests python -m pytest -q -p no:cacheprovider
 tests/test_viendinhduong_parser.py tests/test_missing_nutrition.py`.
The default Python lacked pytest; uv supplied the test environment.
