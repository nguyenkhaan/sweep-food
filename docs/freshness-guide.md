# Hướng dẫn kiểm thử thủ công hai API FreshCheck

Tài liệu này dành cho người mới làm quen với backend. Bạn sẽ gọi API lấy câu hỏi cho một nguyên liệu, tạo một lô hàng (`batch`) để kiểm thử, rồi gửi câu trả lời để nhận đánh giá độ tươi. Hai API FreshCheck cần kiểm thử là `GET /api/freshness/questions` và `POST /api/freshness/batches/{batch_id}/assessment`.

## 1. Chuẩn bị

1. Trong `src/backend/.env`, cấu hình `DATABASE_URL` trỏ tới database cần kiểm thử. Backend cũng cần các biến môi trường khác theo [`.env.example`](../src/backend/.env.example).
2. Đảm bảo migration đã chạy và FreshCheck KB có một phiên bản `ACTIVE` với mapping nguyên liệu. Nếu chưa có, xem [runbook vận hành](../src/backend/docs/freshcheck-operations-runbook.md). Lệnh `uv run python -m src.seed_freshness --dry-run` chỉ xem trước; thêm `--apply` mới ghi dữ liệu.
3. Từ `src/backend`, chạy `uv run main.py`. Mở `http://localhost:4000/docs` và bấm **Authorize** để dùng access token của tài khoản đang hoạt động. Không dùng refresh token.

Ví dụ dưới đây dùng nguyên liệu **Ba rọi bò**, có `master_ingredient_id` là `2a3f9a6c-d42f-519e-ae13-93c63fad1003` và FreshCheck ID là `ba_chi_bo` trong database đã seed ở môi trường thử nghiệm. Ở database khác, ID có thể thay đổi; hãy dùng một ID đã được mapping tại đó.

Hai ID dễ nhầm:

| ID | Dùng ở đâu? |
| --- | --- |
| `master_ingredient_id` | Query của API lấy câu hỏi và body tạo batch. |
| `batch_id` | Đường dẫn của API gửi assessment; lấy từ trường `id` của response tạo batch. |

## 2. API lấy câu hỏi

Trong Swagger, chọn **GET `/api/freshness/questions`**, bấm **Try it out** và điền:

```text
master_ingredient_id = 2a3f9a6c-d42f-519e-ae13-93c63fad1003
```

Bấm **Execute**. Kết quả mong đợi là HTTP `200` với `kb_version`, `freshcheck_ingredient_id`, `archetype_id` và mảng `questions`. Mỗi câu hỏi có `axis` (tên tiêu chí), `question_vi`, `options` (các giá trị được chọn) và `default`.

Với ví dụ Ba rọi bò, bạn nên thấy `freshcheck_ingredient_id` là `ba_chi_bo` và các `axis` như `color`, `stickiness`, `elasticity`, `smell`. Khi chuẩn bị body assessment, **chỉ dùng `axis` và `options[].value` lấy từ response này**. `additionalProp1: "string"` trong Swagger chỉ là ví dụ cấu trúc, không phải câu trả lời hợp lệ.

Nếu nhận `422` với `MAPPING_UNAVAILABLE`, hãy kiểm tra lại ID và mapping của phiên bản KB đang active. Nếu nhận `503` với `FRESHCHECK_KB_UNAVAILABLE`, KB chưa được activate.

## 3. Tạo batch để kiểm thử assessment

API assessment cần một batch thuộc **chính tài khoản đang đăng nhập**. Nếu bạn đã có batch như vậy với nguyên liệu được mapping, lấy `id` của nó và chuyển sang bước 4.

Nếu chưa có, dùng **POST `/api/inventory/batches`** trong Swagger. Thêm header `Idempotency-Key` với giá trị duy nhất, ví dụ `create-ba-roi-bo-001`, rồi dùng body:

```json
{
  "master_ingredient_id": "2a3f9a6c-d42f-519e-ae13-93c63fad1003",
  "quantity": 0.5,
  "unit": "KG",
  "storage_mode": "REFRIGERATED",
  "purchased_at": "2026-10-16T05:00:00Z",
  "note": "Kiem thu FreshCheck"
}
```

Hãy thay `purchased_at` trong ví dụ bằng thời gian mua gần lúc kiểm thử, theo định dạng ISO 8601 có múi giờ (ví dụ hậu tố `Z` nghĩa là UTC). Assessment cần `purchased_at` hoặc `stored_at` để tính thời gian còn lại. Không gửi đồng thời `custom_name` và `master_ingredient_id`; batch chỉ nhận một trong hai. Để kiểm thử FreshCheck tự tính hạn dùng, **không gửi `expires_at`** trong request tạo batch, vì giá trị đó được coi là hạn do nhà sản xuất cung cấp.

Kết quả mong đợi là HTTP `201`. Ghi lại trường `id` trong response; đó là `batch_id` cần dùng ở bước tiếp theo. Cũng ghi lại `current_quantity` và `expires_at` để so sánh sau assessment.

## 4. API gửi đánh giá độ tươi

Trong Swagger, chọn **POST `/api/freshness/batches/{batch_id}/assessment`**:

1. Thay `{batch_id}` bằng `id` của batch vừa tạo; không dùng `master_ingredient_id` ở đây.
2. Điền header `Idempotency-Key`, ví dụ `assess-ba-roi-bo-001`. Đây là khóa nhận diện lần gửi để hệ thống không tạo assessment trùng khi bạn gửi lại.
3. Dán body dưới đây. Các value là lựa chọn hợp lệ cho rubric Ba rọi bò ở KB mẫu; nếu bước 2 trả về lựa chọn khác, dùng value từ response bước 2.

```json
{
  "answers": {
    "color": "hong_tuoi",
    "stickiness": "kho_rao",
    "elasticity": "hoi_ngay",
    "smell": "thom_tuoi"
  }
}
```

Không cần gửi lại `purchased_at` hay `storage_mode` nếu batch đã có hai thông tin đó. Có thể gửi chúng làm dữ kiện thay thế cho lần đánh giá này; hai trường này trên batch không bị sửa bởi API assessment. Nếu gửi `purchased_at`, giá trị phải kèm múi giờ.

Kết quả mong đợi là HTTP `200`. Kiểm tra `assessment_id`, `batch_id`, `kb_version`, `freshcheck_ingredient_id`, `blocked`, `tier`, `score`, `remaining_hours_min`, `remaining_hours_max`, `rule_version` và `expires_at`. `blocked` cho biết có điều kiện an toàn buộc dừng hay không. Một số trường kết quả có thể là `null` tùy tình huống; không nên tự suy diễn rằng mọi assessment đều có số giờ còn lại.

Sau đó dùng **GET `/api/inventory/batches/{batch_id}`** để kiểm tra batch. Với kết quả có hạn dùng ước tính, `expiration_source` sẽ là `ESTIMATED`; `current_quantity` phải bằng trước khi đánh giá. Nếu batch có hạn nhà sản xuất, FreshCheck không ghi đè hạn đó.

## 5. Kiểm thử gửi lại và xử lý lỗi cơ bản

- Gửi lại **cùng URL, body và `Idempotency-Key`** của bước 4. `assessment_id` phải giữ nguyên; batch không bị trừ số lượng.
- Đổi sang `Idempotency-Key` mới khi muốn tạo một lần đánh giá mới. Không tái sử dụng khóa của request cũ cho một tình huống khác.
- Bỏ `Authorization`: mong đợi HTTP `401`. Bỏ `Idempotency-Key` khi gọi POST: mong đợi HTTP `422`.
- Thử answer không thuộc `options[].value`, chẳng hạn `"color": "string"`: mong đợi HTTP `422` với `FRESHCHECK_ASSESSMENT_INPUT_INVALID`.
- Dùng `batch_id` không tồn tại hoặc của tài khoản khác: mong đợi HTTP `404`.

Nếu API trả HTTP `500`, lưu lại đường dẫn API, status, body lỗi và phần cuối server traceback để báo người phụ trách. Không chia sẻ access token hoặc `DATABASE_URL` trong báo cáo lỗi.
