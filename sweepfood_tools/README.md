# Bộ công cụ SweepFood – Vòng 2

Thay cho các file zip trước. Theo bản gọn: không đổi công nghệ, không khảo sát 2, không chấm nhãn mù.
Chi tiết việc của từng người ở tab **Việc cần làm** trong tài liệu kế hoạch.

## can_dung/ – dùng cho vòng 2

| File | Ai | Làm gì |
|---|---|---|
| `sweep-food_be_freshness-api.patch` | Khả An | **Đã có trên nhánh `dev` (commit `77abd5d`) – KHÔNG chạy `git apply` nữa.** BE đã làm bản đầy đủ hơn patch: module `freshness`, bảng `freshcheck_assessments`, kho lấy từ DB qua `scripts.sync_freshcheck_kb` thay cho file JSON. Patch giữ lại để tham khảo; file dùng xuống dòng CRLF nên `git apply` báo lỗi "lacks filename information". |
| `fridge_report.py` | Khả An | Chạy thử gợi ý món trên tủ lạnh thật, không cần sửa code AI, không cần người chấm. Hướng dẫn định dạng file tủ ở đầu file. `python fridge_report.py fridges` → in 4 con số cho slide 6 + ghi `fridge_top3.csv`. |
| `feature_gain_slide6.png` | Gia Huy, Thắng Lê | Biểu đồ cho slide 6. |

## de_danh_chung_ket/ – KHÔNG cần cho vòng 2

`fresh_estimate.py`, `test_freshcheck_safety.py` (đã chạy, số nằm ở tab Kiểm chứng ①; kho không đổi thì không cần chạy lại),
`ocr_eval.py` (OCR vòng 2 chỉ cần đếm tay 15 ảnh), `build_blind_lists.py` + `eval_human_labels.py` + patch sweep-food-AI
(đánh giá có người chấm mù, để dành nếu vào chung kết).
