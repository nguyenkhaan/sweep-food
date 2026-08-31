# Các luồng trong sản phẩm

## Luồng đăng ký - đăng nhập

### Các bước chi tiết

1. Người dùng gửi số điện thoại E.164, mật khẩu và thông tin hồ sơ tùy chọn đến `POST /api/auth/register`.
2. Hệ thống tạo tài khoản `UNVERIFIED` và gửi OTP đăng ký qua SMS; người dùng nhập OTP vào `POST /api/auth/verify/register` để kích hoạt tài khoản.
3. Người dùng đăng nhập bằng số điện thoại và mật khẩu tại `POST /api/auth/login` để nhận access token và refresh token.
4. Ứng dụng dùng access token cho các API bảo vệ; khi hết hạn, dùng `POST /api/auth/token/refresh` để lấy access token mới.
5. Người dùng đăng xuất qua `POST /api/auth/logout`; refresh token tương ứng bị thu hồi.

### Sơ đồ

```mermaid
sequenceDiagram
    participant U as Người dùng
    participant A as API
    participant O as OTP/SMS
    U->>A: Đăng ký (phone, password)
    A->>O: Tạo và gửi OTP REGISTER
    U->>A: Xác thực OTP
    A-->>U: Tài khoản ACTIVE
    U->>A: Đăng nhập
    A-->>U: Access token + Refresh token
    U->>A: API bảo vệ / Đăng xuất
```

## Luồng đổi mật khẩu

### Forgot password (No Authentication)

#### Các bước chi tiết

1. Người dùng quên mật khẩu, nhập số điện thoại tại `POST /api/auth/password/reset`.
2. Hệ thống gửi OTP `RESET_PASSWORD` mà không tiết lộ số điện thoại có tài khoản hay không.
3. Người dùng gửi số điện thoại, OTP, mật khẩu mới và `purpose = RESET_PASSWORD` đến `POST /api/auth/verify/change-password`.
4. Hệ thống đổi mật khẩu và thu hồi mọi session đang hoạt động; người dùng đăng nhập lại.

#### Sơ đồ

```mermaid
sequenceDiagram
    participant U as Người dùng
    participant A as API
    U->>A: Yêu cầu reset password
    A-->>U: OTP RESET_PASSWORD
    U->>A: OTP + mật khẩu mới
    A-->>U: Đổi mật khẩu, thu hồi sessions
    U->>A: Đăng nhập lại
```

### Reset Password (Authenticated)

#### Các bước chi tiết

1. Người dùng đã đăng nhập gọi `POST /api/auth/password/change`.
2. Hệ thống gửi OTP `CHANGE_PASSWORD` đến số điện thoại hiện tại.
3. Người dùng xác nhận OTP, số điện thoại, mật khẩu mới và `purpose = CHANGE_PASSWORD` tại `POST /api/auth/verify/change-password`.
4. Hệ thống cập nhật mật khẩu, thu hồi các session; người dùng đăng nhập lại bằng mật khẩu mới.

#### Sơ đồ

```mermaid
sequenceDiagram
    participant U as Người dùng
    participant A as API
    U->>A: Yêu cầu đổi mật khẩu + access token
    A-->>U: OTP CHANGE_PASSWORD
    U->>A: OTP + mật khẩu mới
    A-->>U: Đổi mật khẩu, thu hồi sessions
```

## Luồng đổi email / phone

### Đổi email

#### Các bước chi tiết

1. Người dùng đã đăng nhập gửi email mới đến `POST /api/users/me/email/request-verification`.
2. Hệ thống lưu email chờ xác thực theo user và gửi OTP đến email mới.
3. Người dùng gửi OTP đến `POST /api/users/me/email/verify`.
4. Hệ thống xác nhận OTP và lưu email mới là email đã xác minh.

#### Sơ đồ

```mermaid
sequenceDiagram
    participant U as Người dùng
    participant A as API
    participant E as Email mới
    U->>A: Yêu cầu đổi email + access token
    A->>E: Gửi OTP CHANGE_EMAIL
    U->>A: Xác thực OTP
    A-->>U: Email mới đã xác minh
```

### Đổi phone

#### Các bước chi tiết

1. Người dùng đã đăng nhập gửi số điện thoại mới đến `POST /api/users/me/phone/request-change`.
2. Hệ thống lưu số điện thoại chờ xác thực và gửi OTP `CHANGE_PHONE` đến số mới.
3. Người dùng gửi OTP đến `POST /api/users/me/phone/confirm-change`.
4. Hệ thống kiểm tra OTP, kiểm tra số điện thoại chưa được dùng và thay thế số điện thoại hiện tại.

#### Sơ đồ

```mermaid
sequenceDiagram
    participant U as Người dùng
    participant A as API
    participant P as Số điện thoại mới
    U->>A: Yêu cầu đổi phone + access token
    A->>P: Gửi OTP CHANGE_PHONE
    U->>A: Xác thực OTP
    A-->>U: Phone mới đã xác minh
```

## Luồng quét món ăn & lên kế hoạch nấu

### Các bước chi tiết

1. Người dùng yêu cầu đề xuất món cho bữa ăn và số servings; theo PRD, hệ thống trả 3–5 món cùng mức độ đáp ứng, nguyên liệu thiếu và lý do xếp hạng.
2. Người dùng chọn món, số servings, ngày và khung bữa ăn để thêm vào meal plan.
3. Người dùng tạo shopping list từ meal plan; hệ thống cộng nhu cầu đã scale theo servings, trừ tồn kho còn dùng được và chỉ trả nguyên liệu thiếu.
4. Sau khi mua, người dùng check từng shopping item. Theo luồng sản phẩm đã chốt, hệ thống tạo batch inventory và `INITIAL_STOCK` ledger cho item generated vừa được check.
5. Trước khi nấu, người dùng gọi `POST /api/cooking/preview` để xem FEFO, batch dự kiến dùng, cảnh báo và nguyên liệu thiếu.
6. Người dùng tạo session qua `POST /api/cooking/sessions` với `meal_plan_item_id` và `servings`. API chỉ tạo session khi tồn kho hiện tại đủ; nếu thiếu trả `409` nêu rõ nguyên liệu và số lượng thiếu.
7. Sau khi nấu, người dùng gọi `POST /api/cooking/sessions/{session_id}/complete` với `Idempotency-Key` và mode tiêu thụ. Hệ thống lock batch, revalidate, trừ tồn kho FEFO và ghi ledger.

*Một bữa ăn (meal) được đề xuất được tạo thành từ nhiều món ăn (recipe). Người dùng chọn ra các món cần nấu từ danh sách đề xuất và tiến hành thêm vào để tạo một bữa ăn (meal). Hệ thống sẽ lên danh sách shopping list cho người dùng để hoàn thiện bữa ăn này. Người dùng check và tiến hành di mua đồ ăn.*

### Sơ đồ

```mermaid
flowchart TD
    A[Đề xuất 3-5 món] --> B[Chọn món + servings vào meal plan]
    B --> C[Tạo shopping list]
    C --> D[Check item đã mua]
    D --> E[Tạo inventory batch + INITIAL_STOCK]
    E --> F[Preview FEFO]
    F --> G{Đủ nguyên liệu?}
    G -- Không --> C
    G -- Có --> H[Tạo cooking session]
    H --> I[Complete: lock, FEFO, ledger]
```

## Luồng mua sắm, bổ sung nguyên liệu vào kho

### Các bước chi tiết

1. Người dùng chọn meal plan rồi tạo shopping list; mỗi item hiển thị nhu cầu, tồn kho đang có và số lượng còn thiếu.
2. Người dùng mua nguyên liệu và check item generated chưa check.
3. Hệ thống chỉ xử lý lần check đầu tiên: tạo một raw-ingredient batch thuộc user với `missing_quantity`, dùng đơn vị/catalog ingredient của item và ghi `INITIAL_STOCK` ledger.
4. Batch mới dùng default storage của catalog và quy tắc ước tính hạn dùng; người dùng có thể bổ sung/chỉnh sửa các chi tiết inventory khi cần.
5. Shopping item giữ batch ID đã tạo trong `source_metadata`, nên lần check lại không tạo thêm tồn kho. Batch mới được tính vào preview, recommendation và kiểm tra tạo cooking session.

*Hiện trạng API: shopping-list và inventory batch routes chưa được triển khai; đây là contract cần hoàn thành ở Task 5.5 và các task inventory liên quan.*

### Sơ đồ

```mermaid
flowchart TD
    A[Meal plan] --> B[Tạo shopping list]
    B --> C[Hiển thị nguyên liệu thiếu]
    C --> D[Người dùng check đã mua]
    D --> E{Item generated chưa check?}
    E -- Có --> F[Tạo inventory batch]
    F --> G[Ghi INITIAL_STOCK ledger]
    G --> H[Lưu batch ID vào source metadata]
    E -- Không --> H
    H --> I[Tồn kho sẵn sàng cho cooking]
```
