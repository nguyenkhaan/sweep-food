# Phase 2 — Theo dõi tiến độ

## Quy tắc triển khai

- Bám sát `plan.md`, `task.md` và `api-contract.md`; không tự thêm API, field, behavior hoặc phạm vi chưa được mô tả.
- Các tác vụ mất nhiều thời gian do người phụ trách chạy và kiểm tra. Trước khi cần thực hiện, phải dừng lại và thông báo rõ lệnh cùng mục đích.
- Mỗi lần chạy test giới hạn tối đa 100 giây. Nếu test vượt 100 giây, phải dừng và thông báo cho người phụ trách, không tiếp tục chạy.
- Nếu cùng một kiểm tra thất bại 3 lần, phải dừng và thông báo cho người phụ trách, không retry lần thứ tư.
- Test treo hoặc không pass không chặn việc hoàn tất code theo task; phải ghi rõ kết quả khi bàn giao.
- Chỉ tạo hoặc chạy file test khi người phụ trách yêu cầu rõ trong prompt; không tự tìm, thêm hoặc chạy test.
- Sau mỗi thay đổi code, phải kiểm tra kỹ import, annotation, generic và kiểu trả về của các file đã chạm; không bàn giao khi còn lỗi type trong IDE hoặc kiểm tra type tĩnh của phạm vi thay đổi.
- Áp dụng `agent/rules/clean-code/mini.md`: ưu tiên local reasoning, tên rõ nghĩa, hàm có một trách nhiệm, side effect tường minh và không thêm abstraction ngoài phạm vi task.
- Chỉ đổi `[ ]` thành `[x]` khi task tương ứng đã hoàn thành và đạt acceptance criteria trong `task.md`.

## Phase 0

- [x] Task 0.1 — Chỉnh sửa SQLAlchemy model theo schema Phase 2
- [x] Task 0.2 — Dọn migration cũ và cập nhật seed data

## Phase 1

- [x] Task 1.1 — Chuẩn hóa error envelope cho OCR/ASR
- [x] Task 1.2 — Đồng bộ HTTP status đăng ký device
- [x] Task 1.3 — Cố định response và thứ tự GET meal plans

## Phase 2

- [x] Task 2.1 — Thêm DTO query và response cho danh sách shopping list
- [x] Task 2.2 — Triển khai service và route GET shopping-lists
- [x] Task 2.3 — Cho phép purchase dùng default storage từ catalog
- [x] Task 2.4 — Định nghĩa recipe_summary cho recommendation response
- [x] Task 2.5 — Populate recipe_summary trong mock recommendation service
- [x] Task 2.6 — Thêm barcode mock không tìm thấy

## Phase 3

- [x] Task 3.1 — Viết ShoppingMutationReceiptModel
- [ ] Task 3.2 — Tạo migration DB-01 shopping_mutation_receipts
- [x] Task 3.3 — Cài đặt lookup, fingerprint và replay receipt
- [x] Task 3.4 — Áp dụng receipt cho generate và add item
- [x] Task 3.5 — Áp dụng receipt cho update và delete item

## Phase 4

- [x] Task 4.1 — Xác nhận quy tắc một item cho một lần nấu
- [x] Task 4.2 — Cập nhật completion transaction và lock order
- [x] Task 4.3 — Chặn sửa/xóa meal-plan item đã được sử dụng
- [x] Task 4.4 — Kiểm tra tác động tới shopping snapshot

## Phase 5

- [x] Task 5.1 — Chốt metric và response Reports
- [x] Task 5.2 — Viết WasteReductionEventModel
- [ ] Task 5.3 — Tạo migration DB-02 waste_reduction_events
- [x] Task 5.4 — Viết logic phân loại và snapshot waste event
- [x] Task 5.5 — Ghi event trong cooking completion transaction
- [x] Task 5.6 — Viết Report DTO và aggregate service
- [x] Task 5.7 — Setup module và route GET reports/waste-reduction

## Phase 6

- [x] Task 6.1 — Viết PremiumInterestModel
- [ ] Task 6.2 — Tạo migration DB-03 premium_interests
- [x] Task 6.3 — Viết Subscription DTO và service
- [x] Task 6.4 — Setup module và hai route Subscription

## Phase 7

- [ ] Task 7.1 — Kiểm tra toàn bộ chuỗi migration Phase 2
- [ ] Task 7.2 — Chạy regression API giữ lại
- [ ] Task 7.3 — Chạy E2E theo api-contract
- [ ] Task 7.4 — Hoàn thiện tài liệu bàn giao BE

## Phase 8 — Chỉ thực hiện khi có quyết định sản phẩm

- [ ] Task 8.1 — Xác nhận schema và contract direct cooking
- [ ] Task 8.2 — Mở rộng preview và create-session cho recipe trực tiếp
