# SweepFood AI — Catalog món ăn và Master nguyên liệu

**Trọng tâm hiện tại của project là xây dựng, tuyển chọn và kiểm chứng catalog món ăn cùng master nguyên liệu/dinh dưỡng.** Các phân hệ AI, crawler, OCR/ASR và recommendation vẫn được giữ trong repo để hỗ trợ hoặc tích hợp khi cần; không phải phạm vi phát triển mặc định ở giai đoạn này.

## 1. Hai phần dữ liệu trung tâm

### Catalog món ăn

Cần phân biệt **corpus công thức đầy đủ** và **catalog đã tuyển chọn**:

| Thành phần | Đường dẫn | Vai trò |
| --- | --- | --- |
| Công thức trong corpus | `data/processed/recipes/recipes.csv` và `.json` | Tên món, nguồn, khẩu phần, thời gian, phân loại và dinh dưỡng ước tính |
| Nguyên liệu từng công thức | `data/processed/recipes/recipe_ingredients.csv` và `.json` | Định lượng, gram quy đổi, vai trò nguyên liệu và liên kết tới master |
| Mapping canonical | `data/processed/recipes/recipe_canonical_mapping.csv` và `.json` | Ánh xạ công thức nguồn sang món đại diện |
| Catalog tuyển chọn | `data/main/catalog/` | Công thức, nguyên liệu, mapping, ghi chú, manifest và ZIP đã công bố |

**Catalog đã chọn không đồng nghĩa với toàn bộ `recipes.csv`/`recipes.json`.** Khi rà catalog, đọc ID trong `data/main/catalog/catalog_manifest.json`, không dùng số lượng của corpus.

### Master nguyên liệu và dinh dưỡng

| Thành phần | Đường dẫn | Vai trò |
| --- | --- | --- |
| Master dữ liệu | `data/processed/viendinhduong/master_ingredients_nutrition.csv` và `.json` | Mã nguyên liệu, tên Việt/Anh, nhóm, alias, dinh dưỡng và nguồn tham chiếu |
| Bảng chuyển mã | `data/processed/viendinhduong/master_code_redirects.csv` và `.json` | Mã đã gộp (`old_code`) → mã chuẩn (`canonical_code`); mã cũ không còn trong master |
| Giao diện tra cứu | `data/processed/viendinhduong/master_viewer.html` | Bản xem có dữ liệu nhúng; không tự cập nhật khi CSV/JSON thay đổi |

Liên kết chính: `recipe_ingredients.recipe_id` → `recipes.id`; `recipe_ingredients.master_ingredient_code` → `master_ingredients_nutrition.code`. Mapping canonical trỏ tới `recipes.id` qua `canonical_recipe_id`.

Master có dữ liệu Viện Dinh Dưỡng, USDA và phần mở rộng có nguồn khác; không mặc định mọi dòng đều là số liệu của Viện Dinh Dưỡng. Đọc `source_type` và `source_ref` của từng dòng. Bảng dinh dưỡng master dùng đơn vị trên 100 g; dinh dưỡng công thức được ước tính từ trọng lượng nguyên liệu.

**CSV/JSON là dữ liệu cần đối chiếu khi bảo trì master, không phải snapshot trong HTML.** Nếu cần giao diện phản ánh thay đổi master, phải cập nhật và kiểm chứng bản xem tương ứng.

### Bộ dữ liệu bàn giao `data/main/`

`data/main/` đóng gói bản mới nhất để chuyển sang recommendation system ở repo khác. Script train mặc định đọc `data/main/catalog/`; giao diện thử nghiệm `mock_web/` vẫn đọc corpus và master trong `data/processed/`.

| Thư mục | Nội dung |
| --- | --- |
| `data/main/catalog/` | Catalog `catalog-r1259-n31-2e025e6abc8e`: 1.075 món, 10.406 dòng nguyên liệu; CSV/JSON công thức, nguyên liệu, canonical mapping, ghi chú, manifest và ZIP |
| `data/main/master_ingredients/` | Master nguyên liệu/dinh dưỡng và bảng chuyển mã, mỗi bảng có CSV/JSON |
| `data/main/training/` | Mô hình `lgbm_contextual.txt` và `metadata.json`, phiên bản 3.1.0, dùng 9 đặc trưng tủ đồ; không dùng thời gian nấu hoặc 5 đặc trưng ngữ cảnh |
| `data/main/training/catalog_ranking/` | `pantries.jsonl.gz` (3.300 tủ đồ) và `pairs.csv.gz` (201.693 cặp tủ đồ–món, có cột train/val/test) |

Catalog công bố được giữ tại `data/main/catalog/` sau khi xóa ứng dụng tuyển chọn. Metadata giữ đường dẫn nguồn lúc train để truy xuất; các đường dẫn lịch sử không phải đầu vào hiện tại. Manifest catalog giữ hash **corpus đầu vào**, không phải hash các bảng catalog đã lọc. `catalog_fingerprint` trong metadata trỏ tới corpus hiện tại; `training_catalog_fingerprint` giữ fingerprint lúc train. Những dòng không công bố phương pháp khớp để trống `match_method` và `match_confidence`, không được coi là khớp thủ công hay đã xác minh. Mã, định lượng, dinh dưỡng và nguồn không thay đổi khi bỏ metadata khớp; tập train và trọng số mô hình giữ nguyên.

Nhãn train là nhãn tổng hợp từ 51 kịch bản (15 kịch bản sinh viên), không phải đánh giá của người dùng thật. Kết quả mô hình 9 đặc trưng nằm trong [`metadata.json`](data/main/training/metadata.json): NDCG@5 = 0,9719 trên 503 query có nhãn dương trong 513 query test.

## 2. Huấn luyện recommendation

Python có `lightgbm` và `numpy`:

```powershell
python -X utf8 scripts/train_recommendation_ranker.py
```

Mặc định đọc catalog ở `data/main/catalog/`, master từ `data/processed/viendinhduong/`; kết quả ghi vào `data/training/`. Lần chạy mới sẽ tạo lại thư mục báo cáo `reports/eda/`; không tự cập nhật bản bàn giao `data/main/training/`.

## 3. Quy tắc bảo trì dữ liệu

1. Giữ ID món và mã master ổn định. Tránh thêm món trùng chỉ vì khác tên vùng miền, cách viết hoặc alias.
2. Sửa đồng bộ các cặp CSV/JSON bị ảnh hưởng; giữ schema và quy ước kiểu dữ liệu hiện có.
3. Khi thêm món, có công thức, nguyên liệu và mapping canonical tương ứng. Nguyên liệu đã khớp phải trỏ tới mã master tồn tại; chưa khớp phải thể hiện đúng trạng thái, không gán mã gần giống mà không có căn cứ.
4. Khi thêm hoặc sửa master, ghi nguồn ở `source_type`/`source_ref`; phân biệt nguyên liệu sống/chín, khô/tươi, có/không đường và phần ăn được.
5. Không bịa định lượng, nguồn hoặc số liệu dinh dưỡng. Quy đổi và proxy phải ghi rõ là ước tính; giá trị chưa biết không thay bằng 0. Dùng dạng thiếu dữ liệu phù hợp với schema hiện có.
6. Tính lại aggregate của công thức bị ảnh hưởng khi thay đổi nguyên liệu/định lượng/dinh dưỡng. Không chỉ sửa tổng để che lỗi ở dòng nguyên liệu.
7. Giữ ghi chú của người dùng. Ghi chú không tự động thay đổi dữ liệu nguồn hoặc phân loại món; cần đọc và xử lý theo yêu cầu cụ thể.
8. Sao lưu trước khi cập nhật corpus. Không tự chạy crawl, merge hoặc rebuild toàn bộ chỉ để sửa một phần dữ liệu.

## 4. Mốc dữ liệu đã ghi nhận

Snapshot sau đợt sửa ngày **17/10/2026**, không phải hằng số của ứng dụng:

| Thành phần | Số lượng |
| --- | ---: |
| Công thức trong corpus | 4.881 |
| Dòng nguyên liệu công thức | 52.760 |
| Master nguyên liệu | 1.398 |
| Món đã chọn trong state local | 1.123 |

## 5. Các phân hệ hỗ trợ và tích hợp

Các phần sau vẫn thuộc project, nhưng chỉ chỉnh sửa khi phục vụ yêu cầu cụ thể hoặc bị ảnh hưởng trực tiếp bởi thay đổi catalog/master:

| Thư mục | Vai trò |
| --- | --- |
| `crawler/` | Thu thập công thức và dữ liệu nguồn; xem [`crawler/README.md`](crawler/README.md) |
| `scripts/` | Công cụ xử lý dữ liệu, rebuild aggregate, merge canonical và huấn luyện |
| `smart_parser/` | So khớp đầu vào với nguyên liệu master; xem [`smart_parser/README.md`](smart_parser/README.md) |
| `smart_input/` | Nhập liệu OCR/ASR và pantry |
| `src/recommendation/` | Sinh ứng viên, đặc trưng và xếp hạng gợi ý món. Kịch bản: `life_scenarios.py`; luật nhãn: `scenario_rules.py`; train: `scripts/train_recommendation_ranker.py` (cần `lightgbm`, ví dụ conda env `ocr_env`) |
| `mock_web/` | Experimental interface for AI agent/component testing only; incomplete and not production-ready. See [`mock_web/README.md`](mock_web/README.md). |
| `nlp/` | Client LLM trích xuất thực thể từ văn bản đầu vào của parser |
| `data/raw/`, `data/training/`, `docs/` | Dữ liệu nguồn, tài nguyên huấn luyện và tài liệu thiết kế rộng hơn |

### Experimental AI agent test interface

**`mock_web/` exists only for local testing of AI agents and components. It is not a finished SweepFood application or a production-ready backend.** It provides a mock interaction surface for recommendation, OCR, ASR and pantry input; inference still uses real components rather than stubbed responses.

The interface and API contracts are experimental. Outputs may be incorrect or incomplete and require review; they are not medical, dietary or food-safety advice. The mock currently reads the full corpus in `data/processed/`, not just the curated catalog. Its displayed ordering also includes heuristic post-processing, so UI results are not a standalone model evaluation.

Run from the repository root with `python -m uvicorn mock_web.app:app --host 127.0.0.1 --port 8000`. Keep it on localhost and use non-sensitive test inputs. See the [mock interface documentation](mock_web/README.md) for dependencies, known limitations and verification steps.


Mục tiêu dài hạn về gợi ý món và giảm lãng phí thực phẩm được giữ lại. **Ưu tiên hiện tại vẫn là chất lượng, độ phủ, truy xuất nguồn và tính nhất quán của catalog + master.**
