# TÓM TẮT THÔNG TIN THAY ĐỔI

## Abstract 

Tài liệu này mô tả trạng thái hiện tại của các tính năng đã bổ sung và luồng API chính từ lập kế hoạch bữa ăn đến hoàn tất nấu ăn.

Các route bên dưới đều có tiền tố `/api` và yêu cầu đăng nhập. Route quản trị Rating yêu cầu tài khoản có vai trò `ADMIN`. Những thao tác có header `Idempotency-Key` cần dùng một giá trị riêng cho mỗi yêu cầu mới.

## Bổ sung các tính năng mới

### Rating

Đã bổ sung bảng `user_feedback` để lưu đánh giá của người dùng. Mỗi lần gửi sẽ tạo một bản ghi mới; cùng một người dùng có thể gửi nhiều lần.

- `rating`: số thực hữu hạn từ 1 đến 5.
- `feedback`: nội dung góp ý; lưu chuỗi rỗng `""` nếu người dùng chỉ gửi số sao.
- `created_at`: thời điểm tạo có múi giờ.

**API route mới:**

- `POST /api/rating?rating={value}`: Gửi một đánh giá mới. `rating` là query bắt buộc; body là tùy chọn.

```json
{
  "feedback": "Gợi ý món ăn hữu ích"
}
```

Có thể bỏ body hoặc gửi `{}` nếu chỉ đánh giá bằng sao.

- `GET /api/rating/admin/feedback?limit=20&offset=0`: Quản trị viên xem danh sách góp ý, tổng số bản ghi và điểm trung bình. Route không có body.
- `GET /api/rating/admin/average`: Quản trị viên lấy điểm trung bình toàn hệ thống. Nếu chưa có đánh giá, `average_rating` là `null`.

### Lịch sử sử dụng nguyên liệu

Đã bổ sung bảng `ingredient_usage_history`. Mỗi lượng nguyên liệu thực tế bị trừ khi hoàn tất nấu ăn sẽ tạo một bản ghi gồm:

- Người dùng, số lượng, đơn vị và thời điểm sử dụng.
- Snapshot JSONB tên nguyên liệu và tên công thức.
- Snapshot không giữ khóa ngoại đến nguyên liệu hoặc công thức, nên lịch sử vẫn đọc được nếu dữ liệu nguồn bị xóa sau này.

Tất cả bản ghi dùng chung thời điểm UTC với `cooking_session.completed_at`. Việc trừ kho, ghi bản ghi tiêu thụ, sổ kho, lịch sử sử dụng, bằng chứng giảm lãng phí và cập nhật trạng thái được lưu trong cùng một giao dịch; nếu có lỗi thì toàn bộ được hoàn tác.

**Route liên quan:**

- `POST /api/cooking/sessions/{session_id}/complete`: Hoàn tất phiên nấu và tự động ghi lịch sử sử dụng nguyên liệu. Không có endpoint ghi history riêng.

```json
{
  "consumption_mode": "EXACT",
  "consumptions": []
}
```

Với `EXACT` hoặc `HALF`, có thể bỏ `consumptions` hoặc truyền `[]` để hệ thống tự chọn lô theo FEFO. `CUSTOM` và `USE_ALL_MATCHED` phải truyền các lô cần sử dụng.

- `GET /api/cooking/history`: Lấy danh sách các phiên nấu đã hoàn tất của người dùng. Đây là route có sẵn và không thay đổi.
- `GET /api/cooking/history/{session_id}`: Lấy chi tiết một phiên nấu, consumption và leftover liên quan. Đây là route có sẵn và không thay đổi.

Không bổ sung API đọc trực tiếp bảng `ingredient_usage_history` trong đợt thay đổi này.

### Hạn sử dụng và FEFO

`expires_at` hiện là trường bắt buộc tại các API tạo nguyên liệu thô do người dùng kiểm soát và phải có múi giờ.

- Lô có `expires_at <= thời điểm hiện tại` được xem là hết hạn.
- Lô hết hạn không được tính là tồn kho khả dụng và không được dùng khi nấu.
- Các dòng dữ liệu cũ có `expires_at = null` vẫn được giữ để tương thích.

**API route liên quan:**

- `POST /api/inventory/batches`: Tạo trực tiếp một lô nguyên liệu trong kho.

```json
{
  "master_ingredient_id": "<ingredient_id>",
  "quantity": 150,
  "unit": "GRAM",
  "storage_mode": "REFRIGERATED",
  "expires_at": "2026-09-30T23:59:59+07:00"
}
```

- `PATCH /api/shopping-lists/{list_id}/items/{item_id}`: Xác nhận đã mua một shopping item và đồng thời tạo inventory batch.

```json
{
  "checked": true,
  "purchase": {
    "storage_mode": "REFRIGERATED",
    "expires_at": "2026-09-30T23:59:59+07:00"
  }
}
```

## Một meal plan có thể có nhiều meal plan item

Trước đây database giới hạn một item cho mỗi tổ hợp `meal_plan_id + planned_for + meal_slot`. Ràng buộc này đã được bỏ.

Hiện tại:

- Một meal plan có thể chứa nhiều meal plan item, kể cả cùng ngày và cùng `meal_slot`.
- Mỗi meal plan item vẫn liên kết với đúng một công thức qua `recipe_id`.
- `meal_slot` vẫn bắt buộc để phân loại `BREAKFAST`, `LUNCH`, `DINNER` hoặc `SNACK`, nhưng không còn quyết định tính duy nhất.
- UUID `id` mới là định danh của meal plan item.

Database hiện có cần bỏ constraint cũ thủ công:

```sql
ALTER TABLE public.meal_plan_items
DROP CONSTRAINT IF EXISTS meal_plan_items_meal_plan_id_planned_for_meal_slot_key;
```

### Luồng API mô phỏng quá trình nấu

#### 1. Tạo meal plan

- `POST /api/meal-plans`: Tạo kế hoạch bữa ăn trong một khoảng ngày.

```json
{
  "name": "Kế hoạch tuần này",
  "starts_on": "2026-09-25",
  "ends_on": "2026-10-01"
}
```

#### 2. Tạo các meal plan item

- `POST /api/meal-plans/{meal_plan_id}/items`: Thêm một công thức vào meal plan. Gọi route nhiều lần để thêm nhiều món, kể cả cùng `planned_for` và `meal_slot`.

```json
{
  "recipe_id": "<recipe_id>",
  "planned_for": "2026-09-26",
  "meal_slot": "BREAKFAST",
  "servings": 1,
  "recommendation_run_id": null
}
```

`recommendation_run_id` là tùy chọn, dùng để truy vết lần gợi ý đã tạo ra món được chọn.

#### 3. Tạo shopping list từ meal plan

- `POST /api/shopping-lists/generate`: Tổng hợp nguyên liệu bắt buộc còn thiếu của các meal plan item đang ở trạng thái `PLANNED`. Route yêu cầu header `Idempotency-Key`.

```json
{
  "meal_plan_id": "<meal_plan_id>"
}
```

Phản hồi chỉ trả thông tin chung của shopping list:

```json
{
  "id": "<list_id>",
  "meal_plan_id": "<meal_plan_id>",
  "status": "ACTIVE",
  "generated_at": "2026-09-25T02:48:57Z"
}
```

Nếu meal plan đã có shopping list `ACTIVE`, hệ thống trả lại list hiện có thay vì tạo list mới.

#### 4. Lấy meal plan và danh sách nguyên liệu cần mua

- `GET /api/meal-plans/{meal_plan_id}`: Lấy meal plan cùng toàn bộ meal plan item. Route không có body.
- `GET /api/shopping-lists/{list_id}`: Lấy shopping list cùng trường `items`, bao gồm số lượng yêu cầu, số lượng đang có và số lượng còn thiếu. Route không có body.

#### 5. Mua và bổ sung nguyên liệu vào inventory

Cách ưu tiên là xác nhận từng shopping item để trạng thái mua hàng và inventory được cập nhật cùng lúc:

- `PATCH /api/shopping-lists/{list_id}/items/{item_id}`: Đánh dấu item đã mua và tạo inventory batch theo `missing_quantity`. Route yêu cầu header `Idempotency-Key`.

```json
{
  "checked": true,
  "purchase": {
    "storage_mode": "REFRIGERATED",
    "expires_at": "2026-09-30T23:59:59+07:00"
  }
}
```

Có thể nhập kho trực tiếp bằng route sau, nhưng shopping item sẽ không tự chuyển sang `is_checked: true`:

- `POST /api/inventory/batches`: Tạo một inventory batch độc lập. Route yêu cầu header `Idempotency-Key`.

```json
{
  "master_ingredient_id": "<ingredient_id>",
  "quantity": 150,
  "unit": "GRAM",
  "storage_mode": "REFRIGERATED",
  "expires_at": "2026-09-30T23:59:59+07:00"
}
```

#### 6. Bắt đầu và hoàn tất cooking session

- `POST /api/cooking/preview`: Xem trước lượng nguyên liệu sẽ dùng, batch được đề xuất và nguyên liệu còn thiếu. Route chỉ đọc, không tạo session hoặc trừ kho.

```json
{
  "meal_plan_item_id": "<meal_plan_item_id>"
}
```

- `POST /api/cooking/sessions`: Tạo cooking session cho một meal plan item đang `PLANNED`. API trả `409` nếu inventory không đủ.

```json
{
  "meal_plan_item_id": "<meal_plan_item_id>"
}
```

- `POST /api/cooking/sessions/{session_id}/complete`: Hoàn tất session, trừ kho và ghi toàn bộ lịch sử liên quan trong một transaction. Route yêu cầu header `Idempotency-Key`.

```json
{
  "consumption_mode": "EXACT"
}
```

`EXACT` và `HALF` tự chọn inventory batch theo FEFO. Khi dùng `CUSTOM`, mỗi phần tử `consumptions` cần có `recipe_ingredient_id`, `inventory_batch_id` và `quantity`.

## Bỏ trường `items` khỏi response của POST shopping list

Trước đây `POST /api/shopping-lists/generate` khai báo response có `items`, nhưng dữ liệu item vừa tạo chưa được query nhìn thấy trước khi commit. Điều này có thể làm response trả `items: []` dù các item đã được lưu.

Hiện tại POST chỉ trả metadata của shopping list. Danh sách nguyên liệu cần mua được lấy qua:

- `GET /api/shopping-lists/{list_id}`: Trả shopping list cùng danh sách `items` mới nhất. Route không có body.

Thay đổi này chỉ tách rõ trách nhiệm của POST và GET; logic tạo shopping-list item trong database vẫn được giữ nguyên.

## Lưu ý cập nhật database

Không có migration tự động nào được tạo hoặc chạy. Database cần được cập nhật thủ công để:

1. Tạo bảng `ingredient_usage_history` cùng các constraint kiểm tra quantity và JSONB snapshot.
2. Tạo bảng `user_feedback` cùng constraint `rating` từ 1 đến 5.
3. Bỏ unique constraint cũ của `meal_plan_items` như câu SQL ở trên.
4. Giữ nguyên cột `inventory_batches.expires_at`; thay đổi mới chỉ bắt buộc trường này tại API tạo dữ liệu mới.
