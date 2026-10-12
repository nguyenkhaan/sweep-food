"""smart_parser - Module Độc Lập Trích Xuất & Đối Soát Thực Thể Ẩm Thực cho SweepFood.

Hỗ trợ 3 luồng đầu vào:
1. Gõ tay (User manual text)
2. Hóa đơn siêu thị OCR (Receipt lines)
3. Giọng nói ẩm thực ASR (Voice transcript)

Chiến thuật 4 tầng chuyên sâu (4-Tier In-Depth Matching):
- Tầng 1: Khớp tuyệt đối qua 15.000+ tên chuẩn & từ đồng nghĩa Viện Dinh Dưỡng (0ms)
- Tầng 2: Bóc tách thương hiệu (CP, Vissan...) & đơn vị đóng gói (kg, khay, vỉ)
- Tầng 3: Gọi LLM gpt-oss:120b-cloud qua Ollama Cloud API để phân tích ngữ cảnh sâu
- Tầng 4: Tự động gán mã Viện Dinh Dưỡng, tính calo/macro, hạn dùng theo 4 mức nhiệt độ
          và mẹo bảo quản khoa học từ FreshCheck KB.
"""

from smart_parser.pantry_parser import PantryEntityParser, get_pantry_parser

__all__ = ["PantryEntityParser", "get_pantry_parser"]
