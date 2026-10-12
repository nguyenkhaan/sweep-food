# 🍲 smart_parser — Module Trích Xuất & Đối Soát Thực Thể Ẩm Thực (SweepFood)

Module độc lập giải quyết bài toán: **Từ văn bản người dùng gõ tay, quét hóa đơn siêu thị OCR hoặc giọng nói ASR, làm sao để trích xuất sạch và đối soát chính xác vào Bảng thành phần thực phẩm Viện Dinh Dưỡng (`master_ingredients`) để lưu vào Tủ Lạnh (Pantry)?**

---

## 🚀 Cách chạy thử nghiệm nhanh (Quickstart)

```bash
python smart_parser/demo.py
```

---

## 🛠️ Cách gọi trong mã nguồn Python (Usage)

```python
from smart_parser import get_pantry_parser

# Khởi tạo singleton parser
parser = get_pantry_parser()

# 1. Xử lý đoạn văn bản bất kỳ (OCR hóa đơn, câu nói ASR, hoặc chuỗi gõ tay)
raw_text = "hôm nay mua nửa cân thịt ba rọi với 3 quả cà chua để ngăn mát"
items = parser.parse_input_to_pantry(raw_text, prefer_llm=True)

for item in items:
    print(item["name"])             # Tên chuẩn hóa (ví dụ: Thịt ba chỉ (ba rọi) heo)
    print(item["code"])             # Mã Viện Dinh Dưỡng (ví dụ: 7018)
    print(item["quantity_g"])       # Định lượng chuẩn gram (ví dụ: 500.0)
    print(item["hours_to_expire"])  # Hạn dùng theo nhiệt độ bảo quản từ FreshCheck KB (ví dụ: 72.0h)
    print(item["freshness_guide"])  # Mẹo bảo quản & dấu hiệu tươi/hỏng
    print(item["nutrition"])        # Calo, Protein, Fat, Carbs per 100g
```

---

## 🧠 Chiến thuật Phễu 4 Tầng Chuyên Sâu (4-Tier In-Depth Matching)

```
[Input Thô: Gõ tay / OCR / ASR]
       │
       ▼
┌────────────────────────────────────────────────────────┐
│ Tầng 1: Khớp tuyệt đối qua 15.000+ từ đồng nghĩa (0ms) │ -> ba chỉ, ba rọi, cá lóc, tàu hũ, ngao...
└──────────┬─────────────────────────────────────────────┘
           │ (Chưa khớp)
           ▼
┌────────────────────────────────────────────────────────┐
│ Tầng 2: Bóc tách thương hiệu (CP, Vissan) & Quy cách   │ -> Lọc khay, vỉ, hộp, kg, lạng, làm sạch...
└──────────┬─────────────────────────────────────────────┘
           │ (Dòng phức tạp / OCR lỗi / giọng nói dài)
           ▼
┌────────────────────────────────────────────────────────┐
│ Tầng 3: LLM gpt-oss:120b-cloud (Ollama Cloud API)      │ -> Trích xuất thực thể sâu, suy luận ngữ cảnh
└──────────┬─────────────────────────────────────────────┘
           │ (Nếu mạng chậm hoặc quota LLM bị ngắt)
           ▼
┌────────────────────────────────────────────────────────┐
│ Tầng 4: Heuristic Regex Fallback & FreshCheck KB       │ -> Gán hạn dùng 4 mức nhiệt độ, mẹo bảo quản
└────────────────────────────────────────────────────────┘
       │
       ▼
[Danh sách Pantry Items chuẩn hóa lưu vào Tủ Lạnh]
```

---

## 📁 Cấu trúc thư mục

```
smart_parser/
├── __init__.py           # Export get_pantry_parser
├── pantry_parser.py      # Lõi xử lý 4 tầng, tra cứu từ điển và FreshCheck KB
├── demo.py               # Kịch bản chạy thử nghiệm thực tế (OCR, ASR, Alias)
└── README.md             # Hướng dẫn chi tiết này
```
