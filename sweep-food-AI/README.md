# 🥗 SweepFood AI: Vietnamese Recipe & Nutritional Knowledge Base

> **AI-Powered Culinary Recommendation & Food Waste Minimization System**

[![Dataset QC](https://img.shields.io/badge/Dataset_QC-100%25_PASSED-success.svg)](#quality-control--audit)
[![Recipes](https://img.shields.io/badge/Recipes-5%2C641_Unique_Dishes-blue.svg)](#dataset-specifications)
[![Ingredients](https://img.shields.io/badge/Ingredients-63%2C943_Lines-green.svg)](#dataset-specifications)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](requirements.txt)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 📌 Tổng Quan Dự Án (Project Overview)

**SweepFood AI** là hệ thống cơ sở tri thức ẩm thực và AI gợi ý món ăn tối ưu cho người Việt, giải quyết bài toán hàng ngày: *"Hôm nay ăn gì?"* dựa trên nguyên liệu thực tế có sẵn trong tủ lạnh nhằm **tối đa hóa tỷ lệ sử dụng thực phẩm** và **giảm thiểu lãng phí (Food Waste Minimization)**.

Kho dữ liệu này đã được xây dựng, làm sạch, tính toán dinh dưỡng đa lượng (Macro: Calories, Protein, Fat, Carbs) và kiểm định chất lượng tự động đạt chuẩn **Production-Grade (Zero Defects)**.

---

## 📊 Thông Số Kỹ Thuật Dataset (Dataset Specifications)

| Chỉ số kỹ thuật | Số lượng thực tế | Tỷ lệ hoàn thành | Đánh giá chất lượng |
| :--- | :---: | :---: | :--- |
| **Công thức món ăn (`recipes`)** | **5.641 món** | **100.0%** | Chuẩn Single-Dish (đã loại sạch 50 mâm cơm combo) |
| **Chuẩn hóa tên món (Qwen 2.5 3B)** | **5.641 món** | **100.0%** | **Sạch 100%** từ thừa (*Cách làm, Bí quyết, giật tít SEO...*) |
| **Gắn nhãn Phương pháp nấu** | **5.641 món** | **100.0%** | Chiên/Rán, Xào, Kho, Canh/Súp, Nướng, Hấp, Luộc... |
| **Gắn nhãn Vai trò bữa ăn** | **5.641 món** | **100.0%** | Món chính, Canh, Khai vị/Gỏi, Ăn vặt, Tráng miệng, Đồ uống |
| **Gắn nhãn Chế độ ăn & Đối tượng** | **5.641 món** | **100.0%** | Cơm gia đình, Ăn chay, Eat Clean, Trẻ em |
| **Độ phủ Calo & Macro món ăn** | **5.625 món** | **99.7%** | Đầy đủ `total_calories`, `protein_g`, `fat_g`, `carbs_g` |
| **Dòng nguyên liệu (`recipe_ingredients`)** | **63.943 dòng** | **100.0%** | Khử trùng lặp, bóc tách thực thể cốt lõi bằng Qwen 2.5 3B |
| **Quy đổi trọng lượng Gram** | **63.943 dòng** | **100.0%** | 100% có `estimated_weight_g`, khống chế trần lá/thảo mộc rời |
| **Khớp Viện Dinh Dưỡng Quốc Gia** | **58.687 dòng** | **91.8%** | Liên kết trực tiếp bảng dinh dưỡng, 0 mismatch hệ thống |
| **Kho Master Viện Dinh Dưỡng** | **751 nguyên liệu** | **100.0%** | Bổ sung Củ sen, Cá cam tươi, đầy đủ vi chất |

---

## 📈 Phân Bổ Năng Lượng Ẩm Thực (Calorie Distribution)

| Phân vị (Percentile) | Tổng Calo món ăn | Khẩu phần | Calo / Người ăn | Ý nghĩa ẩm thực thực tế |
| :--- | :---: | :---: | :---: | :--- |
| **5% (Thấp)** | **109 kcal** | 2.0 người | **55 kcal** | Canh rau thanh đạm, dưa ngâm, salad nhẹ |
| **25% (Nhẹ)** | **437 kcal** | 2.0 người | **218 kcal** | Rau củ xào thịt, trứng chiên, canh thịt băm |
| **50% (Trung vị)** | **828 kcal** | **4.0 người** | **207 kcal** | Món mặn ăn cơm gia đình (thịt kho, cá chiên, sườn rim) |
| **75% (Đậm đà)** | **1.488 kcal** | 4.0 người | **372 kcal** | Món thịt nướng, gà chiên, bò kho, cá hấp |
| **95% (Tiệc/Lẩu)** | **3.557 kcal** | 4.0 người | **889 kcal** | Nồi lẩu gia đình, giò heo hầm măng, vịt tiềm |
| **99% (Mâm cỗ)** | **6.306 kcal** | 6.0 người | **1.051 kcal** | Món tiệc lớn, gà quay nguyên con, khay bánh mâm cỗ |

---

## 📁 Cấu Trúc Thư Mục Dự Án (Repository Structure)

```text
sweep-food-AI/
├── data/
│   ├── processed/
│   │   ├── recipes/
│   │   │   ├── recipes.csv               # 5,641 món ăn chuẩn (CSV)
│   │   │   ├── recipes.json              # 5,641 món ăn chuẩn (JSON)
│   │   │   ├── recipe_ingredients.csv    # 63,943 nguyên liệu sạch (CSV)
│   │   │   └── recipe_ingredients.json   # 63,943 nguyên liệu sạch (JSON)
│   │   └── viendinhduong/
│   │       ├── master_ingredients_nutrition.csv  # 751 nguyên liệu VDD
│   │       └── ingredient_alias_map.json         # 4,684 alias ngữ nghĩa
│   ├── interim/                          # Tệp đệm đồng bộ song song
│   └── raw/                              # Dữ liệu cào web gốc
├── nlp/
│   ├── entity_matcher.py                 # Thuật toán so khớp thực thể ẩm thực
│   ├── recipe_classifier.py              # Phân loại phương pháp, kiểu món, chế độ ăn
│   └── ingredient_parser.py              # Parser định lượng & đơn vị nguyên liệu
├── src/
│   └── recommendation/
│       ├── ingredient_roles.py           # Phân loại gia vị, đạm chính, rau củ
│       ├── candidate_generator.py        # Inverted index lọc ứng viên siêu tốc
│       ├── pantry_simulator.py           # Bộ sinh 10,000+ kịch bản tủ lạnh gia đình
│       └── feature_extractor.py          # Trích xuất 30 đặc trưng LTR 3 tầng
├── scripts/
│   ├── generate_ltr_dataset.py           # Sinh bộ dữ liệu LTR (Train/Val/Test 50k mẫu)
│   ├── train_deep_rankers.py             # Huấn luyện mô hình LightGBM & XGBoost Ranker
│   ├── run_fair_benchmark.py             # Giải đấu Ablation Tournament (100 kịch bản)
│   └── run_qwen_line_pipeline.py         # Pipeline bóc tách thực thể bằng Qwen 2.5 3B
├── tests/
│   ├── test_data_integrity.py            # Kiểm thử hồi quy toàn vẹn dữ liệu & mismatch
│   └── test_api_endpoints.py             # Kiểm thử hồi quy API backend
├── web/                                  # Giao diện tương tác & FastAPI REST API
├── insight.md                            # Cơ sở khoa học & Insight "Thiếu một chút vẫn nấu được"
├── requirements.txt                      # Danh mục thư viện phụ thuộc
└── README.md
```

---

## 💡 Cơ Sở Khoa Học & Insight Ẩm Thực

Hệ thống áp dụng mô hình toán học **Continuous Quantity Elasticity** giải quyết bài toán thực tế *"Thiếu một chút vẫn nấu được"* (ví dụ: công thức đòi 300g rau muống nhưng tủ lạnh chỉ có 150g vẫn đạt 88.75% độ thỏa dụng, không bị gãy điểm hay rơi vào vách đá). 

Chi tiết công thức toán học và 6 cấp độ hồ sơ co giãn xem tại [**`insight.md`**](insight.md).

---

## 🚀 Cài Đặt & Khởi Chạy (Quickstart)

### 1. Cài đặt môi trường
```bash
git clone https://github.com/BaryuH/sweep-food-AI.git
cd sweep-food-AI
pip install -r requirements.txt
```

### 2. Chạy kiểm thử hồi quy tự động (Automated Regression Tests)
```bash
pytest tests/ -v
```

### 3. Huấn luyện mô hình xếp hạng 3 tầng đặc trưng
```bash
python scripts/generate_ltr_dataset.py --samples 50000
python scripts/train_deep_rankers.py
```

### 4. Đánh giá kiểm thử khách quan (100 Scenarios Ablation Tournament)
```bash
python scripts/run_fair_benchmark.py
```

### 5. Khởi chạy Web UI Demo tương tác trực tiếp
```bash
pip install fastapi "uvicorn[standard]" python-multipart \
  opencv-python-headless Pillow ctranslate2 tokenizers
# Run the application
uvicorn web.app:app --host 127.0.0.1 --port 8000
```
Truy cập trình duyệt: `http://127.0.0.1:8000`

---

## 🎯 Lộ Trình Dự Án (Roadmap Status)
- [x] **Giai đoạn 1**: Thu thập, thanh lọc, tính toán Macro & kiểm định chất lượng Dataset (100% Hoàn thành).
- [x] **Giai đoạn 2**: Xây dựng Engine mô phỏng tủ lạnh, Continuous Elasticity & Dataset Learning-to-Rank (100% Hoàn thành).
- [x] **Giai đoạn 3**: Tối ưu hóa siêu tham số mô hình LightGBM / XGBoost Ranker & đánh giá NDCG@5 (100% Hoàn thành).
- [x] **Giai đoạn 4**: Xây dựng bộ kiểm thử hồi quy tự động (100% Tests Passed).
- [x] **Giai đoạn 5**: Triển khai REST API (FastAPI) & Demo Web tương tác trực quan (100% Hoàn thành).