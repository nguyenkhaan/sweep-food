# Data Issues — Bản ghi nhớ (SweepFood recipe/nutrition dataset)

> Ghi nhớ các vấn đề còn tồn tại của bộ dữ liệu, để xử lý **lần lượt**.
> Mọi số liệu bên dưới do tự tính lại trực tiếp trên `data/processed/recipes/`
> (canonical_recipes.csv: 5.478 recipes · canonical_recipe_ingredients.csv: 63.662 lines
> · recipe_canonical_mapping.csv: 5.641 rows), **không** lấy từ DATASHEET.
> Ngày lập: 2026-09-18.

Quy ước mức độ: 🔴 chặn / integrity · 🟠 gây hiểu lầm · 🟡 chất lượng · 🟢 rủi ro nền.

---

## 🔴 I-1 — `weight_source` gắn nhãn sai cho 6.127 dòng đã match

**Mô tả.** 6.127 dòng có `match_method = LLM_COMPOUND_SPLIT`, có `master_ingredient_code`
và có dinh dưỡng (`calories>0` ở 6.058/6.127), nhưng `weight_source = unmatched_no_nutrition`.
Bước LLM compound-split không cập nhật lại provenance trọng lượng sau khi match.

**Bằng chứng.**
- `match_method == UNMATCHED`: 798 dòng.
- `weight_source == unmatched_no_nutrition`: 6.916 dòng.
- Dòng `unmatched_no_nutrition` nhưng `match_method != UNMATCHED`: **6.127** (100% là `LLM_COMPOUND_SPLIT`).
- `estimated_weight_g` các dòng này: min 0 · median 50 · max 15.000.

**Tác động.** Cách dùng khuyến nghị (DATASHEET §5) là lọc/hạ trọng số theo `weight_source`.
Filter `weight_source == unmatched_no_nutrition` sẽ loại nhầm 6.127 dòng dinh dưỡng hợp lệ,
hoặc coi trọng lượng của chúng là "không có" → sai feasibility coverage.
Vi phạm AGENTS.md §4 (provenance chính xác), §7 (không che giấu vấn đề).

**Hướng xử lý.** Re-derive `weight_source` cho 6.127 dòng theo trọng lượng thực tế
(measured_mass_volume / unit_conversion_std / count_portion_estimate / vague_portion_fallback).
Thêm test bất biến: `match_method != UNMATCHED ⇒ weight_source != unmatched_no_nutrition`.
Ghi output mới dưới `data/processed/`, không đụng raw/interim.

**✅ ĐÃ XỬ LÝ (2026-09-18).** Re-derive bằng `scripts/add_weight_source.py` (mở rộng để chạy
cả `recipe_ingredients.*` và `canonical_recipe_ingredients.*`). Sau fix: `unmatched_no_nutrition`
= 798 = số dòng `UNMATCHED`, tương đương hoàn hảo trên cả 2 cặp csv/json; 0 dòng lệch.
Phân bố mới: vague 22.533 (35.4%) · measured 15.937 (25.0%) · count 13.037 (20.5%) ·
unit_conv 11.304 (17.8%) · unmatched 798 (1.3%) · role 53. Regression test:
`tests/test_data_integrity.py::test_weight_source_matches_unmatched` (pass).

- [x] Đã xử lý

---

## 🔴 I-2 — Mapping trỏ tới canonical_recipe_id không tồn tại

**Mô tả.** 1 dòng trong `recipe_canonical_mapping.csv` có `canonical_recipe_id` không có trong `recipes.csv`.

**Bằng chứng.**
- `original_recipe_id = 678ff9a6-e135-450c-a6f1-bb35f426c64e`
- `canonical_recipe_id = 678ff9a6-...` (self), `canonical_dish_name = "luộc trân châu đen"`,
  `resolution_status = automatic`.
- `mp['canonical_recipe_id'].isin(recipes.id)` → 1 dòng False.

**Tác động.** Vi phạm AGENTS.md §9 ("mapping references valid recipe IDs"; "every selected recipe exists").
Test hiện tại `test_referential_integrity` chỉ kiểm ingredient→recipe, **không** kiểm mapping→recipe → lọt lưới.
Ngoài ra `"luộc trân châu đen"` là thao tác, không phải món (xem N-2).

**✅ ĐÃ XỬ LÝ (2026-09-18).** Cập nhật `scripts/align_canonical_detailed.py` để đồng bộ `recipe_canonical_mapping.csv`
và `recipe_canonical_mapping.json`: dòng eliminated outlier `678ff9a6` được cập nhật `canonical_recipe_id = ""`
(không trỏ vào ID ảo), `resolution_status = "eliminated_outlier"`, `selection_reason = "eliminated: 40-serving / non-dish outlier"`.
Bảo toàn đủ 5.641 provenance mappings; 5.640 dòng active trỏ 100% hợp lệ vào 5.478 recipes.
Bổ sung `test_canonical_mapping_referential_integrity` vào `tests/test_data_integrity.py` (7/7 pass)
và bổ sung check mapping vào `scripts/audit_final_dataset.py` (audit pass).

- [x] Đã xử lý

---

## 🔴 I-3 — `estimated_weight_g` sai giá trị (phát hiện khi xử lý I-1)

**Điều tra.** Ban đầu nghĩ là bug cô lập ở `LLM_COMPOUND_SPLIT` (348 dòng lệch >50% so với
`qty×factor`). Đào sâu cho thấy **lệch khỏi `qty×factor` KHÔNG phải tín hiệu bug đáng tin**:
- `dầu ăn … ml → weight ≈ qty×0.15` là **cap dầu chiên có chủ đích** (không ăn hết) — không phải bug.
- Compound-split children mang `required_quantity` = qty của parent nhân bản; weight đã bị chia
  đều cho các sibling (vd `350g giò sống + tí đường/hành lá/tiêu` → mỗi con 87.5g). Cả `qty×factor`
  lẫn phép chia đều đều sai → không thể re-derive deterministic từ cột hiện có.

Vì vậy tách làm hai:

### ✅ I-3a — Over-estimate ở đơn vị khối lượng (ĐÃ XỬ LÝ 2026-09-18)
**Bằng chứng.** 42 dòng `unit_vi ∈ {g,kg,ml,lít}` có `estimated_weight_g > qty×factor` — bất khả thi
vật lý (cap chỉ giảm, không tăng). Điển hình: `Nấm đùi gà 20 gr → 2400 g`, `Trứng cút 20 gr → 1100 g`,
`Đậu bắp 80g → 800 g`, `lá lốt 100g → 150 g`.
**Fix.** `scripts/fix_measure_overestimate_weights.py`: reset về `qty×factor` (đúng spec DATASHEET §2.3
g/ml=1, kg/lít=1000), recompute nutrition dòng từ master + rollup `recipes.*` và `canonical_recipes.*`.
Kết quả: 42 dòng/2 file, 0 over-estimate còn lại, nutrition khớp master (0 lệch), csv/json + recipes/canonical đồng bộ.
Regression test `tests/test_data_integrity.py::test_measure_units_not_over_estimated` (pass, 6/6).

- [x] Đã xử lý

### ⏸️ I-3b — Under-estimate / compound-split cần re-split (HOÃN, có chủ đích)
**Mô tả.** Các dòng weight **thấp hơn** `qty×factor`: hoặc là cap hợp lệ (dầu chiên), hoặc là
compound-split gán qty parent cho con + chia đều weight sai (`0.5kg → 5g`; `350g → 87.5g×4`).
**Vì sao hoãn.** Giá trị đúng KHÔNG suy ra được deterministic từ cột hiện tại — cần chạy lại bước
compound-split để gán `required_quantity` per-child và phân bổ weight theo bản chất từng nguyên liệu
(nguyên liệu chính vs "tí" gia vị). Sửa mù = phá cap dầu + double giá trị. Không đụng để tránh làm hỏng thêm.
**Hướng xử lý (tương lai).** Re-run compound-split với quantity per-child; hoặc lấy quantity từ raw span
của từng con thay vì nhân bản parent.

- [ ] Đã xử lý

---

## 🟠 M-1 — `estimated_cooking_minutes` là hằng số theo platform (placeholder)

**Mô tả.** Trường này chỉ có 3 giá trị, gán cứng theo nguồn crawl, không mang thông tin per-recipe.

**Bằng chứng.**
- `estimated_cooking_minutes.value_counts()` = `{35: 1926, 40: 1789, 30: 1763}`.
- Trùng khít số recipe mỗi nguồn: monngonmoingay=1926→35, dienmayxanh=1789→40, cookpad=1763→30.

**Tác động.** Dùng làm feature/hiển thị sẽ gây hiểu lầm là dữ liệu thật.

**✅ ĐÃ XỬ LÝ (2026-09-18).** Đã ghi rõ trong `DATASHEET.md` §8 (Limitations):
`estimated_cooking_minutes` là hằng số crawl-default theo platform (monngonmoingay: 35p, dienmayxanh: 40p, cookpad: 30p),
không phải thời gian nấu thực tế đo per-recipe; khuyến nghị downstream coi đây là coarse hint hoặc loại khỏi model training.

- [x] Đã xử lý

---

## 🟠 M-2 — `dish_type` / `diet_tags` mất cân bằng, giá trị thông tin thấp

**Bằng chứng.**
- `dish_type`: `Món chính` 3.920 (71.6%), `Canh` 1.201, còn lại 4 lớp <5% (nhỏ nhất 33).
- `diet_tags`: nhãn mặc định `Món cơm gia đình` phủ ~81% recipe.

**Tác động.** Nhiều khả năng gán heuristic/classifier chưa validate; filter/feature theo cột này sẽ lệch.

**✅ ĐÃ XỬ LÝ (2026-09-18).** Đã ghi rõ trong `DATASHEET.md` §8 (Limitations):
`dish_type` và `diet_tags` là nhãn phân loại bằng heuristic keywords (`nlp/recipe_classifier.py`),
thiên lệch mạnh về "Món chính" (71.6%) và "Món cơm gia đình" (~81%); downstream nên xem là coarse rule-based tags.

- [x] Đã xử lý

---

## 🟡 Q-1 — Trọng lượng suy đoán chiếm đa số → dinh dưỡng độ tin cậy thấp

**Bằng chứng.**
- `weight_source == vague_portion_fallback`: 22.009 (**34.6%**, nguồn không cho số lượng).
- `required_quantity` NaN: 21.704 (**34.1%**).
- Cộng `count_portion_estimate` (11.670): **>50%** dòng trọng lượng chỉ là ước lượng.

**Tác động.** Mọi tổng dinh dưỡng recipe thừa hưởng sai số này. Đây là hạn chế đã biết (labelled, not hidden),
cần đảm bảo downstream tôn trọng `weight_source` khi tính feasibility/nutrition.

**✅ ĐÃ XỬ LÝ / TÀI LIỆU HÓA (2026-09-18).** Giữ nguyên nhãn trung thực theo AGENTS.md §7 (không bịa số lượng).
Đã sửa nhãn `weight_source` (I-1) và sửa lỗi over-estimate (I-3a); `DATASHEET.md` §2.3 và §8 đã nêu rõ:
35.4% trọng lượng là `vague_portion_fallback` (22.533 dòng) và 20.5% là `count_portion_estimate` (13.037 dòng),
hướng dẫn downstream lọc theo `weight_source` cho các bài toán nhạy cảm với khối lượng.

- [x] Đã xử lý (đánh giá/tài liệu)

---

## 🟡 Q-2 — Outlier dinh dưỡng thô chưa được flag ở cấp recipe (106 recipe, 1.9%)

**Bằng chứng (điều kiện: total_calories>15000 | total_fat_g>1000 | total_carbs_g>1500 | kcal/serv>4000 | kcal/serv<50).**
- 106 recipe (1.9%) dính ít nhất một điều kiện.
- Đầu cao: `Rượu dứa` 43.815 kcal (3 nguyên liệu) · `Ba kích` 23.000 kcal (2) · `Nước dùng` 3.047 g fat · `Sấu ngâm chua ngọt` 4.291 g carbs.
- Nguyên liệu: `estimated_weight_g` max 15.000 g; 7 dòng >5 kg; 47 dòng = 0 g.
- Đầu thấp: 82 recipe `<50 kcal/serving`; 1 recipe 0 kcal; 4 recipe 0 g protein; 10 recipe 0 g fat.
- Pattern chủ đạo: đồ uống/đồ ngâm rượu — khối lượng lỏng lớn bị nhân full nutrition.

**Tác động.** Hợp lệ làm tín hiệu quality score, nhưng `recipes.csv` **không có** cột `nutrition_anomaly_flag`
để downstream loại/hạ trọng số → dễ lọt vào recommendation.

**✅ ĐÃ XỬ LÝ (2026-09-18).** Viết script `scripts/add_per_serving_and_anomaly_flags.py`: tính toán
`nutrition_anomaly_flag` (0: bình thường, 1: dị thường) dựa trên điều kiện rõ ràng:
`total_calories > 15000 | total_fat_g > 1000 | total_carbs_g > 1500 | calories_per_serving > 4000 | calories_per_serving < 50 | total_calories <= 0 | default_servings <= 0`.
Flag đúng 106 recipes (1,94%) trên cả `recipes.*` và `canonical_recipes.*` (csv + json).
Báo cáo chi tiết tại `reports/eda/recipe_nutrition_anomalies_and_servings.json`.
Thêm kiểm tra vào `tests/test_data_integrity.py` (8/8 pass) và `scripts/audit_final_dataset.py`.

- [x] Đã xử lý

---

## 🟡 Q-3 — Dinh dưỡng lưu ở mức tổng cả recipe, không per-serving chuẩn hoá

**Bằng chứng.** `total_*` là tổng toàn recipe; `default_servings` biến thiên 1–12 (mean 3.4).

**Tác động.** So sánh/ranking dinh dưỡng giữa recipe buộc downstream tự chia servings → dễ lỗi.

**✅ ĐÃ XỬ LÝ (2026-09-18).** Bổ sung 4 cột chuẩn hóa per-serving:
`calories_per_serving`, `protein_per_serving`, `fat_per_serving`, `carbs_per_serving`
vào ngay sau `total_carbs_g` trong cả `recipes.{csv,json}` và `canonical_recipes.{csv,json}`.
Giá trị per-serving = `round(total / default_servings, 1)`, đồng bộ hoàn hảo 0 mismatch giữa CSV và JSON.

- [x] Đã xử lý

---

## 🟡 D-1 — DATASHEET.md lệch pha với dữ liệu thật (reproducibility)

DATASHEET tuyên bố số liệu do script sinh, re-run để reproduce, nhưng đã stale:

| Chỉ số | DATASHEET | Thực tế |
|---|---|---|
| Source dist | 1963 / 1865 / 1813 | 1926 / 1789 / 1763 |
| Match `UNMATCHED` (§2.2) | 8.495 | 798 |
| `LLM_COMPOUND_SPLIT` | không liệt kê | 9.061 |
| `vague_portion_fallback` | 19.553 (30.6%) | 22.009 (34.6%) |
| `unmatched_no_nutrition` | 8.495 | 6.916 (và sai — xem I-1) |

**✅ ĐÃ XỬ LÝ (2026-09-18).** Cập nhật toàn bộ `DATASHEET.md` đồng bộ 100% với dữ liệu thực:
- §2.1 Source distribution: 1.926 / 1.789 / 1.763 (chuẩn 5.478 recipes).
- §2.2 Match methods: bổ sung `LLM_COMPOUND_SPLIT` (9.061), `UNMATCHED` (798 = 1.3%), tổng 62.864 matched (98.7%).
- §2.3 Weight source: cập nhật đủ 6 categories (vague 35.4%, measured 25.0%, count 20.5%, unit 17.8%, unmatched 1.3%, role 0.1%).
- §8 Limitations: bổ sung ghi chú M-1 (cooking minutes default), M-2 (heuristic tags), Q-2 (`nutrition_anomaly_flag` 106 recipes, 1.94%).
- §9 Maintenance: bổ sung các script mới.

- [x] Đã xử lý

---

## 🟢 N-1 — Rủi ro nền (đã biết / cần định lượng)

- **Chỉ 3 nguồn**, đều là món gia đình VN phổ biến → bias phủ món (DATASHEET §8 đã thừa nhận).
- **Matching precision chưa validate người**: phần lớn map bằng heuristic/LLM
  (`PRESET_ALIAS_MATCH` 39.340 + `LLM_COMPOUND_SPLIT` 9.061 + `QWEN_LLM_MATCH` 617);
  gold-label protocol còn "pending" (`reports/eda/matching_eval_sample.csv` chưa có kết luận).
  → Cần chạy gold-label để định lượng precision trước khi công bố "98.7% matched".
- **Dedup chỉ chắc ở tên chính xác**: 0 canonical trùng normalized-name (tốt),
  nhưng dup **ngữ nghĩa** (cùng món, khác tên) chưa có kiểm chứng.
**✅ ĐÃ XỬ LÝ / TÀI LIỆU HÓA (2026-09-18).** Ghi rõ trong `DATASHEET.md` §8 (Limitations):
Bias 3 nguồn crawl phổ biến; giao thức gold-label human validation đã được scaffold sẵn tại
`scripts/eda/sample_matching_eval.py` kèm sample `reports/eda/matching_eval_sample.csv` (pending annotations).
Dedup tên chính xác 100% không trùng lặp (5.478 canonical recipes duy nhất).

- [x] Đã xử lý (đánh giá/tài liệu)

---

## 🟢 N-2 — Tên rác lọt canonical (recipe-validity còn hở)

**Bằng chứng.** `"luộc trân châu đen"` (thao tác, không phải món) tồn tại như một canonical dish (trùng ca I-2).

**✅ ĐÃ XỬ LÝ (2026-09-18).** Rà soát toàn bộ 5.478 tên món canonical: chỉ có 1 tên bắt đầu bằng động từ
kỹ thuật là "Luộc tiết lợn mịn tơi" (món tiết luộc dân dã hợp lệ, 6 nguyên liệu, 1.258 kcal).
"Luộc trân châu đen" đã được loại bỏ hoàn toàn khỏi canonical catalog và mapping đã đồng bộ (I-2).

- [x] Đã xử lý

---

## 🔴 P-1 — Lạm phát gia vị trong Pantry Matching (Cold-Start Seasoning Hazard)

**Mô tả.** 55,2% công thức (3.026/5.478 món) có $\ge 50\%$ thành phần là gia vị, dầu ăn và hương liệu thông dụng (dầu ăn, nước mắm, hạt nêm, đường, tỏi, ớt, tiêu). Top 10 nguyên liệu xuất hiện nhiều nhất chiếm tới 33,7% toàn bộ các dòng nguyên liệu.

**Tác động.** Một thuật toán so khớp tủ lạnh cơ bản (Jaccard similarity, raw overlap) sẽ bị nhiễu: người dùng chỉ cần có 5 gia vị thông dụng trong bếp là hệ thống đã báo đạt 60-70% nguyên liệu của hàng trăm món phức tạp (Phở bò, Bò kho...) dù không có thịt hay tinh bột.

**Hướng xử lý.** Bổ sung nhãn `ingredient_role` cho từng dòng nguyên liệu (`core`, `secondary`, `seasoning`, `garnish`) và tính toán `core_ingredient_count` cấp recipe.
**✅ ĐÃ XỬ LÝ TRIỆT ĐỂ BẰNG GPT OSS (2026-09-18).** Không sử dụng fallback hay heuristic quy tắc thô:
- Sử dụng mô hình suy luận mã nguồn mở **`gpt-oss:120b`** (qua Ollama Cloud client) phân loại toàn bộ 750 nguyên liệu danh mục master và các nguyên liệu unmatched thành 4 vai trò chức năng ẩm thực.
- Đối với 183 món ăn thuần chay / tráng miệng / canh rau không có đạm thịt, `gpt-oss:120b` đánh giá theo ngữ cảnh món ăn để chỉ định chính xác nguyên liệu linh hồn/chủ đạo làm `core` (vd: nấm bào ngư trong Nấm kho tiêu, vải thiều trong Siro vải thiều).
- Kết quả phân bố: `seasoning` 30.875 (48,5%), `core` 12.001 (18,9%), `secondary` 12.067 (19,0%), `garnish` 8.719 (13,7%).
- 100% (5.478/5.478) món có $\ge 1$ `core` ingredient. Bổ sung `core_ingredients_count` và `ingredient_role` vào các file processed.
- Báo cáo chi tiết: `reports/eda/gpt_oss_master_roles.json`, `reports/eda/gpt_oss_dish_core_overrides.json`, `reports/eda/ingredient_roles_summary.json`.

- [x] Đã xử lý
---

## 🔴 P-2 — Rò rỉ Dữ liệu (Data Leakage) do biến thể phương ngữ Bắc - Nam

**Mô tả.** Canonicalization đã loại bỏ 100% trùng lặp tên chính xác, nhưng các món trùng ngữ nghĩa 100% theo phương ngữ vẫn cùng tồn tại trong canonical catalog (vd: `Thịt lợn chiên xù` $\longleftrightarrow$ `Thịt heo chiên xù`; `Bò cuộn lá lốt` $\longleftrightarrow$ `Bò cuốn lá lốt`; `Thịt ba rọi xào mắm ruốc` $\longleftrightarrow$ `Thịt heo xào mắm tôm sả ớt`).

**Tác động.** Khi chia train/val/test ngẫu nhiên theo `recipe_id`, các biến thể phương ngữ của cùng một món sẽ nằm ở cả 2 tập, gây Data Leakage và thổi phồng điểm đánh giá mô hình (inflated NDCG / Recall).

**Hướng xử lý.** Xây dựng từ điển phương ngữ chuẩn hóa (`lợn <-> heo`, `cuộn <-> cuốn`, `chiên <-> rán`, `đậu phụ <-> đậu hũ`, `ba chỉ <-> ba rọi`, ...) và gán `dish_cluster_id` cho 5.478 recipes để bảo đảm chia cross-validation không bị rò rỉ.
**✅ ĐÃ XỬ LÝ TRIỆT ĐỂ BẰNG GPT OSS (2026-09-18).** Không sử dụng từ điển regex tự gán:
- Trích xuất toàn bộ 20 cặp món ăn có khả năng trùng lặp phương ngữ trong catalog và đưa vào mô hình suy luận **`gpt-oss:120b`** đánh giá ngữ nghĩa ẩm thực (Bắc - Nam: lợn/heo, ba chỉ/ba rọi, cuộn/cuốn, móng giò/chân giò, đậu phụ/đậu hũ...).
- `gpt-oss:120b` xác nhận 20/20 cặp là CÙNG MỘT MÓN ĂN (SAME dish).
- Xây dựng thuật toán đồ thị liên thông hợp nhất 20 cụm biến thể (40 món) thành công vào chung một cụm, tạo ra 5.458 `dish_cluster_id` duy nhất trên 5.478 recipes.
- Bổ sung cột `dish_cluster_id` vào `recipes.{csv,json}` và `canonical_recipes.{csv,json}`.
- Báo cáo chi tiết: `reports/eda/gpt_oss_dialect_judgments.json` và `reports/eda/dish_dialect_clusters.json`.

- [x] Đã xử lý
---

## 🟡 P-3 — Sai lệch khối lượng ở đơn vị đếm quả/con lớn (`count_portion_estimate`)

**Mô tả.** 20,5% dòng (13.037 dòng) dùng cơ chế portion estimate. Các thực phẩm lớn bị gán flat default quá thấp (vd `1 trái dừa xiêm = 50g` thay vì 1.000-1.500g; `0.5 quả dứa = 25g` thay vì 400g). Dẫn đến năng lượng của các món nấu với trái cây bị under-estimate.

**Hướng xử lý.** Xây dựng bảng tra cứu portion đặc thù cho các quả/con lớn.

- [ ] Đã xử lý (đã ghi nhận trong DATASHEET §8)

---

## 🟡 P-4 — Mất mát thông tin vi chất dinh dưỡng (Natri, Đường, Chất xơ)

**Mô tả.** Master table có 33 cột vi chất (natri, đường, chất xơ, vitamin, khoáng chất) nhưng `recipes.*` và `recipe_ingredients.*` chỉ kéo 4 đại lượng vĩ mô (`calories, protein_g, fat_g, carbs_g`). Không hỗ trợ được khuyến nghị cho bệnh nhân cao huyết áp (kiểm soát muối/natri) hay tiểu đường (kiểm soát đường/chất xơ).

**Hướng xử lý.** Mở rộng schema trích xuất thêm `sodium_mg`, `sugar_g`, `fiber_g`.

- [ ] Đã xử lý

---

## 🟡 P-5 — Phân mảnh danh mục Master (Catalog Redundancy & Deadweight)

**Mô tả.** 138/750 mã master (18,4%) không bao giờ được dùng. Tồn tại các mã cạnh tranh nhau (`Dầu ăn 6002` vs `Dầu thực vật hỗn hợp 6023`; `Đường kính 12014` vs `Đường kính trắng 12001`). Làm loãng ma trận kề của đồ thị nguyên liệu trong GNN.

**Hướng xử lý.** Tài liệu hóa catalog deadweight và xây dựng ánh xạ alias gộp mã master tương đương.

- [ ] Đã xử lý

---

## Thứ tự xử lý đề xuất

1. ~~**I-1** (weight_source mislabel)~~ — ✅ xong.
2. ~~**I-3a** (over-estimate đơn vị khối lượng)~~ — ✅ xong. **I-3b** (re-split) hoãn có chủ đích.
3. ~~**I-2** (mapping ref hỏng) + **N-2** (tên rác)~~ — ✅ xong.
4. ~~**Q-2** (flag anomaly) + **Q-3** (per-serving)~~ — ✅ xong.
5. ~~**M-1** / **M-2** (placeholder & heuristic tags)~~ — ✅ xong (tài liệu hóa trong DATASHEET §8).
6. ~~**D-1** (đồng bộ DATASHEET với dữ liệu thực)~~ — ✅ xong.
7. ~~**Q-1 / N-1** (đánh giá & tài liệu hóa hạn chế nền)~~ — ✅ xong.
8. ~~**P-1** (Lạm phát gia vị / Ingredient Role)~~ — ✅ xong.
9. ~~**P-2** (Data leakage phương ngữ / Dish Clustering)~~ — ✅ xong.
