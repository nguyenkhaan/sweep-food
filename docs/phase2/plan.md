# Phase 2 — Đối chiếu API FE/BE và kế hoạch bổ sung

> Ngày phân tích: 2026-09-06. Trạng thái: **kế hoạch, chưa triển khai thay đổi BE/FE**.
> Yêu cầu đầu vào: [docs/api-contract.md — M7](../api-contract.md), gồm nội dung đang sửa trong working tree.
> Phạm vi BE: `src/backend/src/module/**`, đối chiếu thêm DTO, service, model, router registration và test liên quan.
> Nguyên tắc bắt buộc: **giữ các chức năng BE đã có; bổ sung có kiểm soát, không xóa trắng module, API, bảng dữ liệu, migration hoặc lịch sử kho**.

## 1. Kết luận và phạm vi

Bản M7 đã mô tả lại phần lớn API theo BE hiện tại. Những endpoint được M7 ghi rõ “không có” như `/pantry/*`, `/scan/*`, `/dishes/{id}`, `PUT` cả meal plan không tự động trở thành yêu cầu phải xây thêm. Cần phân biệt mô tả hiện trạng, đề xuất cải thiện trong phần “Ghi chú cho Backend”, và sai lệch thực sự giữa contract với code.

Kết quả kiểm kê bằng AST và OpenAPI: **77 operation HTTP trong 13 module**, gồm 6 route health và 2 route gửi push thử. Trong đó Auth có 11 route, User có 7 route, Favorites có 11 route đã triển khai nhưng **không có mục request/response riêng trong thân contract M7**, dù phần mở đầu nói đã đối chiếu các nhóm này.

Kế hoạch chính gồm:

1. Sửa tài liệu còn sai/thiếu, chuẩn hóa lỗi OCR/ASR và giải quyết status đăng ký device.
2. Thêm **`GET /shopping-lists`** để khôi phục danh sách theo tài khoản; thêm dữ liệu recipe card vào response **`POST /recommendations`**, vẫn mock recommendation.
3. Mở rộng request tick mua sắm để có thể suy ra `storage_mode` từ catalog, giữ việc xác nhận `purchase` và transaction nhập kho.
4. Giữ nấu qua meal plan theo PRD; làm rõ giới hạn item “ẩn”, trạng thái hoàn tất và dữ liệu shopping list đã generate. Nấu trực tiếp recipe là phương án riêng, không mặc nhiên thay thế luồng cũ.
5. Lên lịch thêm **`GET /reports/waste-reduction`**, **`GET /subscription`**, **`POST /subscription/premium-interest`** sau nhóm tích hợp chính. Hai màn FE tiếp tục mock tới khi endpoint tương ứng hoàn thành.

**Số endpoint mới trong phương án chính: 4.** Không cần thêm `GET /recommendations`, `/cooking/quick`, API tuần hiện tại, API nhập kho hàng loạt hoặc hệ thống thanh toán để đáp ứng M7.

**Phạm vi database:** chưa cần thêm/xóa/đổi kiểu field của bảng hiện hữu cho các thay đổi API chính. Đề xuất thêm **3 bảng** khi triển khai T08, T12 và T14; chi tiết field, khóa, index, transaction, migration và nghiệm thu nằm ở **mục 5.8**. Reports/Subscription vẫn thuộc P2; không tạo các bảng này nếu chưa triển khai nhóm chức năng tương ứng.

### Quy ước phân loại

| Nhãn | Ý nghĩa | Cách xử lý |
|---|---|---|
| GIỮ | API đã đáp ứng nội dung M7 | Giữ đường dẫn, request, response và chức năng hiện tại |
| DOC | Contract sai/thiếu hoặc mô tả chưa đủ | Sửa tài liệu, ví dụ và mapping FE; không đổi BE chỉ để chuẩn hóa hình thức |
| REQ | Cần mở rộng/sửa request API hiện có | Giữ payload cũ hợp lệ; thêm validation cho trường hợp mới |
| RES | Cần bổ sung/sửa response hoặc HTTP status | Giữ field cũ; ghi rõ tác động nếu đổi status |
| LOGIC | Khoảng trống hành vi khi đi qua các API | Tách khỏi đổi schema; kiểm thử ở service/database |
| NEW | Chưa có route đáp ứng | Viết thêm trong module phù hợp hoặc module mới |
| DECISION | Cần định nghĩa sản phẩm/nghiệp vụ | Ghi phương án mặc định và điều kiện triển khai; không coi là đã thống nhất |

Ưu tiên: **P0** = xử lý sai lệch gây lỗi tích hợp; **P1** = bổ sung phục vụ luồng chính; **P2** = Reports/Subscription không chặn MVP; **P3** = phương án mở rộng chưa được M7 yêu cầu chắc chắn.

## 2. Nguồn và mức độ kiểm chứng

| Mã | Nguồn đã đọc | Nội dung dùng để đối chiếu |
|---|---|---|
| S01 | [app.py](../../src/backend/src/app.py), [exceptions.py](../../src/backend/src/core/exceptions.py) | Prefix `/api`, đăng ký router, envelope lỗi |
| S02 | [catalog_router.py](../../src/backend/src/module/catalog/catalog_router.py), [catalog_dto.py](../../src/backend/src/module/catalog/catalog_dto.py), [catalog_service.py](../../src/backend/src/module/catalog/catalog_service.py) | Search/category, phân trang, nutrition, shelf-life |
| S03 | [recipe_router.py](../../src/backend/src/module/recipes/recipe_router.py), [recipe_dto.py](../../src/backend/src/module/recipes/recipe_dto.py), [recipe_service.py](../../src/backend/src/module/recipes/recipe_service.py) | Card, detail, Decimal, scale servings |
| S04 | [recommendation_dto.py](../../src/backend/src/module/recommendations/recommendation_dto.py), [recommendation_service.py](../../src/backend/src/module/recommendations/recommendation_service.py) | Mock đọc tối đa 5 recipe thật, không ghi recommendation run |
| S05 | [cooking_route.py](../../src/backend/src/module/cooking/cooking_route.py), [cooking_dto.py](../../src/backend/src/module/cooking/cooking_dto.py), [cooking_service.py](../../src/backend/src/module/cooking/cooking_service.py), [cooking_helper.py](../../src/backend/src/module/cooking/cooking_helper.py) | Preview, sessions, complete, leftovers, history |
| S06 | [meal_plan_router.py](../../src/backend/src/module/meal_plans/meal_plan_router.py), [meal_plan_dto.py](../../src/backend/src/module/meal_plans/meal_plan_dto.py), [meal_plan_service.py](../../src/backend/src/module/meal_plans/meal_plan_service.py), [meal_plan_item_model.py](../../src/backend/src/model/meal_plan_item_model.py) | List trả array, ownership, ngày trong plan, unique slot |
| S07 | [shopping_router.py](../../src/backend/src/module/shopping_lists/shopping_router.py), [shopping_dto.py](../../src/backend/src/module/shopping_lists/shopping_dto.py), [shopping_service.py](../../src/backend/src/module/shopping_lists/shopping_service.py), [shopping_list_model.py](../../src/backend/src/model/shopping_list_model.py) | Generate/get, purchase, retry, ACTIVE theo plan |
| S08 | [inventory_router.py](../../src/backend/src/module/inventory/inventory_router.py), [inventory_dto.py](../../src/backend/src/module/inventory/inventory_dto.py), [inventory_service.py](../../src/backend/src/module/inventory/inventory_service.py) | Batch, audit reason, summary, freshness, ledger |
| S09 | [extraction_route.py](../../src/backend/src/module/extractions/extraction_route.py), [extraction_dto.py](../../src/backend/src/module/extractions/extraction_dto.py), [extraction_provider.py](../../src/backend/src/module/extractions/extraction_provider.py) | Multipart/query, mock, lỗi validation riêng |
| S10 | [notification_router.py](../../src/backend/src/module/notification/notification_router.py), [notification_dto.py](../../src/backend/src/module/notification/notification_dto.py), [notification_service.py](../../src/backend/src/module/notification/notification_service.py) | Device 200, notification status, public push test |
| S11 | [auth_router.py](../../src/backend/src/module/auth/auth_router.py), [auth_dto.py](../../src/backend/src/module/auth/auth_dto.py), [user_router.py](../../src/backend/src/module/user/user_router.py), [user_dto.py](../../src/backend/src/module/user/user_dto.py) | Auth, OTP, profile, JSON/plain text |
| S12 | [favorite_router.py](../../src/backend/src/module/favorites/favorite_router.py), [favorite_dto.py](../../src/backend/src/module/favorites/favorite_dto.py), [favorite_service.py](../../src/backend/src/module/favorites/favorite_service.py) | Favorite recipes/menus đã có; status/body DELETE |
| S13 | [prd.md §7.9](../../src/backend/docs/prd.md), [product-flow.md](../../src/backend/docs/product-flow.md), [phase5-api-spec.md](../../src/backend/docs/phase5-api-spec.md) | Xác nhận chủ đích nấu qua meal-plan item và mock recommendation |
| S14 | [inventory_ledger_entry_model.py](../../src/backend/src/model/inventory_ledger_entry_model.py), [inventory guards migration](../../src/backend/alembic/versions/7b1f4d2a9c30_phase4_inventory_guards.py), [fefo_service.py](../../src/backend/src/service/fefo_service.py) | Ledger bất biến, đơn vị tương thích, nền dữ liệu Reports |

Skill áp dụng: [planning-and-task-breakdown](../../agent/skills/planning-and-task-breakdown/SKILL.md), [documentation-and-adrs](../../agent/skills/documentation-and-adrs/SKILL.md), và `ponytail` để tái sử dụng DTO/service/model hiện có. Theo yêu cầu người dùng, kế hoạch và checklist cùng nằm trong file này, thay cho đường dẫn mặc định `tasks/plan.md` của skill. Tài liệu `references/definition-of-done.md` được skill dẫn tới không có trong bản skill cục bộ; tiêu chí nghiệm thu cụ thể được ghi trực tiếp bên dưới.

Phân tích hiện trạng dựa trên code trong workspace, không phải cam kết rằng môi trường deploy đã chạy cùng revision. Các schema đề xuất ở mục 5 là thiết kế cho lần triển khai tới, chưa phải API đang có.

## 3. Ma trận đối chiếu toàn bộ endpoint được mô tả trong thân M7

Mọi đường dẫn dưới đây đều có prefix `/api`. Tên `{id}` trong M7 và `{recipe_id}`/`{batch_id}` trong code chỉ là tên tham số, không phải khác đường dẫn thực tế.

### 3.1 Catalog, Recipes, Recommendations

| Endpoint | Request FE so với BE | Response/hành vi FE so với BE | Loại / hành động |
|---|---|---|---|
| `GET /ingredients` | Khớp `q`, `category`, `page=1`, `per_page=20`, max 100 | Khớp category object, aliases, unit/storage enums | GIỮ — S02 |
| `GET /ingredients/{id}` | Khớp UUID | Khớp nutrition và rules; nutrition dùng Decimal nullable. Service hiện load rules gắn trực tiếp ingredient; không suy ra đã có fallback category chỉ vì enum có `CATEGORY` | GIỮ + DOC kiểu số/phạm vi rules — S02 |
| `GET /recipes` | Khớp `q`, `tag`, `max_cooking_minutes`, page/per_page | Khớp card; tags object; nhiều giá trị Decimal có thể ra string | GIỮ — S03 |
| `GET /recipes/{id}` | Khớp `servings` tùy chọn, dương | Khớp ingredient/nutrition scale tổng theo servings; không có pantry fields | GIỮ — S03 |
| `POST /recommendations` | Khớp `{request}`; trim, 1–1000 ký tự, cấm extra fields | Mock đã có, thiếu media/time/nutrition để dựng card như FE đề xuất ở ghi chú #5 | RES P1: thêm `recipe_summary`, không đổi request/method/provider — S04 |

**Lưu ý mock:** BE không phân tích ngữ nghĩa chuỗi request, không đọc kho để tính thiếu/hạn dùng; chọn recipe theo tên/id và dựng score giả lập. `missing_ingredients` và `near_expiry_ingredients` hiện là mảng rỗng. Không hứa luôn có 3–5 item khi catalog có ít hơn 3 recipe; thực tế trả 0–5. Không có `recommendation_run_id` trong response; FE bỏ qua/null trường đó khi thêm meal-plan item. Dòng “GET /recommendations” ở ghi chú #5 là lỗi tài liệu, phải là **POST**.

### 3.2 Cooking

| Endpoint | Request FE so với BE | Response/hành vi FE so với BE | Loại / hành động |
|---|---|---|---|
| `POST /cooking/preview` | Khớp, chỉ `meal_plan_item_id` | 200 preview, không ghi kho/session | GIỮ; DOC luồng meal plan — S05/S13 |
| `POST /cooking/sessions` | Khớp, chỉ `meal_plan_item_id` | 201 PLANNED; thiếu nguyên liệu trả 409; chưa trừ kho | GIỮ; DECISION “nấu nhanh” — S05/S13 |
| `POST /cooking/sessions/{id}/complete` | Khớp mode và Idempotency-Key. M7 thiếu quy định EXACT/HALF cấm consumptions; USE_ALL_MATCHED cấm quantity; batch không được lặp | 200 `{session, consumptions, updated_batches}` chưa được M7 mô tả đủ | DOC P0; LOGIC trạng thái meal-plan xem G10 — S05 |
| `POST /cooking/sessions/{id}/leftovers` | Khớp quantity/unit, default REFRIGERATED, expires/note optional; không yêu cầu Idempotency-Key | 201; chưa truyền expires thì hiện cộng 3 ngày; M7 thiếu schema đầy đủ | GIỮ + DOC; rủi ro retry và nhiều leftover xem mục 7 — S05 |
| `GET /cooking/history` | Không query phân trang | 200 `{items:[{session_id, recipe_id, recipe_name, servings, status, completed_at}]}` | GIỮ + DOC — S05 |
| `GET /cooking/history/{id}` | Khớp UUID | `{session, recipe_id, recipe_name, consumptions, leftover_batch_id, completed_at}` | GIỮ + DOC — S05 |

Tạo session kiểm tra đủ lượng theo toàn bộ servings trước khi complete chọn HALF/CUSTOM; không hứa HALF sẽ cho phép tạo session khi kho không đủ cho EXACT. Không tự đổi điều kiện này trong Phase 2.

### 3.3 Meal Plans

| Endpoint | Request FE so với BE | Response/hành vi FE so với BE | Loại / hành động |
|---|---|---|---|
| `POST /meal-plans` | Khớp name?, starts_on, ends_on | 201 plan rỗng; không có unique theo tuần/user | GIỮ — S06 |
| `GET /meal-plans/` | Khớp limit/offset, 20/0, max limit 100 | BE trả **array** `MealPlanViewDTO[]`, thêm created_at/updated_at, không items/total; router thiếu response_model, query thiếu order_by | DOC + RES schema/OpenAPI + LOGIC thứ tự ổn định P1; giữ array — S06 |
| `GET /meal-plans/{id}` | Khớp UUID/ownership | Khớp plan + items; chưa có active_shopping_list_id | GIỮ; chọn NEW list shopping thay vì thêm field này — S06/S07 |
| `POST /meal-plans/{id}/items` | Khớp recipe/date/meal_slot/servings/run? | 201; ngày ngoài plan hoặc trùng `(plan,date,slot)` → 409; run phải thuộc user | GIỮ + DOC ràng buộc — S06 |
| `PATCH /meal-plans/{id}/items/{item_id}` | Khớp 4 field optional; body phải có field; không nhận status | 200 item; không có API skip; status enum không đồng nghĩa có transition API | GIỮ + DOC — S06 |
| `DELETE /meal-plans/{id}/items/{item_id}` | Khớp | 204 với item xóa được; item đã được session tham chiếu có rủi ro FK, không mặc định xóa an toàn | GIỮ; LOGIC kiểm tra xung đột trước xóa khi làm T09 — S05/S06 |

### 3.4 Shopping Lists

| Endpoint | Request FE so với BE | Response/hành vi FE so với BE | Loại / hành động |
|---|---|---|---|
| `POST /shopping-lists/generate` | Khớp meal_plan_id và header | 201; có ACTIVE list cho plan thì trả list đó, **không tính lại** từ kho/plan mới; key nhận vào chưa được lưu | GIỮ + DOC snapshot, LOGIC retry riêng — S07 |
| `GET /shopping-lists/{list_id}` | Khớp UUID | Khớp ShoppingList + items | GIỮ — S07 |
| `POST /shopping-lists/{list_id}/items` | Khớp identity XOR, quantity>0, unit, cost? | 201 manual item; Idempotency-Key có ở router nhưng service bỏ qua, retry có thể tạo item trùng | LOGIC P1, giữ request/response — S07 |
| `PATCH /shopping-lists/{list_id}/items/{item_id}` | `purchase` bắt buộc khi checked=true cho **mọi item**, không riêng generated; storage_mode hiện required; expires_at đã optional | Check tạo batch một lần; uncheck không trừ/xóa batch; recheck không nhập kho lần nữa. Chỉ manual chưa check mới được sửa quantity/cost | DOC P0 + REQ P1 default storage; giữ response — S07 |
| `DELETE /shopping-lists/{list_id}/items/{item_id}` | Header đã required | Chỉ xóa manual chưa check; generated hoặc đã check → 409; retry sau xóa có thể 404 | DOC + LOGIC retry nếu hoàn thiện idempotency — S07 |
| **`GET /shopping-lists`** | FE đề xuất status=ACTIVE để phục hồi sau đổi máy | **Chưa có**; DB/service có nền ownership và list theo plan | **NEW P1**, thiết kế mục 5.1 — S07 |

### 3.5 Inventory

| Endpoint | Request FE so với BE | Response/hành vi FE so với BE | Loại / hành động |
|---|---|---|---|
| `POST /inventory/batches` | Khớp identity XOR, quantity/unit/storage, datetime có timezone, key | Khớp batch 201 + INITIAL_STOCK ledger | GIỮ — S08 |
| `GET /inventory/batches` | Khớp status/storage/master/page/per_page | `{items,total,page,per_page}`; không mặc định chỉ ACTIVE nếu bỏ status | GIỮ + DOC pagination/filter — S08 |
| `GET /inventory/batches/{id}` | Khớp UUID | Khớp batch; freshness tính khi đọc | GIỮ — S08 |
| `PATCH /inventory/batches/{id}` | M7 chưa liệt kê **reason required** và ít nhất một metadata field; không nhận identity/quantity/storage_mode | Khớp batch 200; reason phục vụ audit | DOC P0; **không bỏ reason ở BE** — S08 |
| `DELETE /inventory/batches/{id}` | Khớp key và X-Reason | 204 archive + ledger, không hard delete | GIỮ bắt buộc — S08 |
| `POST /inventory/batches/{id}/adjustments` | Chỉ MANUAL_ADJUSTMENT, CORRECTION, DISCARDED hợp lệ; không phải mọi enum ledger. Hai loại đầu cần delta hữu hạn khác 0; DISCARDED cấm delta | Khớp batch 200; không cho tồn âm | DOC P0 — S08 |
| `POST /inventory/batches/{id}/consume` | Khớp quantity>0, reason, key | Batch 200; số lượng tính theo unit của batch | GIỮ — S08 |
| `POST /inventory/batches/{id}/move` | Khớp storage_mode, reason, key | Batch 200; xử lý ước tính hạn dùng theo logic có sẵn | GIỮ — S08 |
| `GET /inventory/summary` | Không query | M7 nói không có “sắp hết hạn” chưa chính xác: có expiring_soon_count/expired_count **mỗi nhóm ingredient + unit tương thích** | DOC P0; không viết lại summary — S08 |
| `GET /inventory/ledger` | Khớp filters, timezone, phân trang | Khớp ledger `{items,total,page,per_page}` bất biến | GIỮ — S08/S14 |

Summary chỉ xét ACTIVE và current_quantity>0 nhưng vẫn có thể gồm batch đã hết hạn. Tổng quantity ở summary **không phải tồn kho đủ điều kiện nấu**; preview/generate còn loại batch hết hạn. Không cộng các nhóm khác đơn vị thành một số kg. FE cần thống kê theo storage phải lấy đủ các trang batch hoặc chờ yêu cầu aggregate riêng; M7 chưa yêu cầu API mới cho việc đó.

### 3.6 Extractions, Devices, Notifications, Reports, Subscription

| Endpoint | Request FE so với BE | Response/hành vi FE so với BE | Loại / hành động |
|---|---|---|---|
| `POST /extractions/ocr/label` | Khớp multipart file image | Success khớp, persisted=false; lỗi MIME/size 422 chỉ `{detail}` | **RES P0** envelope lỗi — S09/S01 |
| `POST /extractions/ocr/invoice` | Khớp multipart file image | Như trên; fields.line_items riêng | **RES P0** envelope lỗi — S09/S01 |
| `POST /extractions/asr` | Khớp multipart file audio | Như trên; fields giống label | **RES P0** envelope lỗi — S09/S01 |
| `POST /extractions/barcode` | Khớp **query barcode**, không body multipart | Mock hiện luôn SUCCEEDED + Whole Milk cho mọi chuỗi; nhánh “không tìm thấy → fields rỗng” chưa có | DOC + LOGIC fixture mock P1; giữ 200/persisted=false — S09 |
| `POST /users/me/devices` | Khớp fcm_token/platform; token 20–4096 ký tự | Body khớp; **BE/test 200, FE 201** | **RES P0** status; quyết định tương thích mục 5.4 — S10 |
| `DELETE /users/me/devices/{id}` | Khớp device_id/ownership | 204 disable | GIỮ — S10 |
| `GET /notifications` | Khớp limit/before | Khớp items/next_before và các enum | GIỮ — S10 |
| `PATCH /notifications/{id}` | Khớp READ/DISMISSED; UNREAD không hợp lệ | Notification body khớp | GIỮ — S10 |
| **`GET /reports/waste-reduction`** | period=week/month/year; M7 chưa định nghĩa default/kỳ | **Chưa có route/service**, cũng chưa có metric saved_kg | **NEW + DECISION P2** — mục 5.6 |
| **`GET /subscription`** | Bearer theo quy ước chung; không body | **Chưa có**; plan free/premium và expires_at | **NEW P2**, MVP trả free/null — mục 5.7 |
| **`POST /subscription/premium-interest`** | Chưa định nghĩa body trong M7 | **Chưa có**; registered=true, không thanh toán | **NEW P2**, lưu quan tâm theo user — mục 5.7 |

Không có endpoint tạo notification inbox cho FE là đúng. Tuy nhiên BE có public `/send-notification` và `/send-web-notification` dùng gửi push thử; không được đánh đồng hai route đó với API tạo notification thuộc user, cũng không xóa chúng vì không xuất hiện trong M7.

## 4. Các gap xuyên module và tài liệu

| ID | Gap có bằng chứng | Tác động | Phương án / task |
|---|---|---|---|
| G01 | M7 tuyên bố JSON chung, nhưng verify-register/logout/verify-email/confirm-phone trả plain text; 204 không body | FE parse JSON lỗi | DOC: liệt kê ngoại lệ, giữ response hiện tại. T01 |
| G02 | Danh sách route không Bearer thiếu `POST /auth/verify/change-password`; route này dùng OTP cho RESET_PASSWORD/CHANGE_PASSWORD, không dependency auth | FE reset mật khẩu có thể gắn auth sai | DOC: mô tả OTP purpose và bước xác nhận; không tự thêm JWT bắt buộc. T01 |
| G03 | Auth/User/Favorites vắng body schema trong thân M7 | Có thể viết trùng API đã có hoặc bỏ sót FE mapping | Bổ sung phụ lục request/response 29 route hiện hữu. T01; danh sách mục 8 |
| G04 | OCR/ASR tự trả JSONResponse nên bypass global handler | Envelope lỗi khác quy ước | RES: dùng HTTPException 422 để qua handler chung hoặc create_error_response sẵn có. T02 |
| G05 | Device status 200/201 lệch | Client kiểm tra đúng 201 có thể báo thất bại sau khi đã đăng ký | FE chấp nhận 200/201 trước; BE đáp ứng 201 trong đợt chuyển đổi. T03 |
| G06 | GET meal-plans thiếu response_model/order_by; contract không nêu array | Codegen và chọn tuần không ổn định | Khai báo list[MealPlanViewDTO], order_by created_at DESC + id DESC; không đổi envelope. T04 |
| G07 | Không tìm shopping list bằng tài khoản | Mất list_id sau cài lại app | NEW read endpoint, tái sử dụng model/index; không tự archive list khác. T05 |
| G08 | Gợi ý thiếu card; service đã tải RecipeModel đầy đủ | FE N lần GET cho phần card | Thêm summary ngay từ recipe đã tải; không gọi HTTP hoặc query từng recipe. T07 |
| G09 | purchase yêu cầu storage_mode dù catalog có default | Form mua sắm nhiều bước hơn cần thiết | REQ chỉ làm storage_mode optional trong purchase; vẫn cần người dùng xác nhận purchase. T06 |
| G10 | complete chỉ cập nhật CookingSessionModel, không cập nhật MealPlanItemModel.status; generate chỉ lấy PLANNED | Món đã nấu có thể vẫn hiện chưa nấu và được tính vào list tạo sau đó | LOGIC đề xuất hoàn tất item cùng transaction, xác định quy tắc một item/một lần nấu. T09; không khẳng định M7 đã định nghĩa quy tắc này |
| G11 | Không có cờ hidden/source cho meal plan/item, unique slot chỉ cho một item mỗi ngày/bữa/plan | FE “ẩn” bằng local state vẫn tạo dữ liệu BE thật, có thể trùng slot hoặc tham gia shopping | Giữ plan thật theo PRD; không bảo đảm item ẩn vô hại. Nhánh tùy chọn mục 5.5 |
| G12 | Header Idempotency-Key được yêu cầu nhưng generate/add/remove shopping không sử dụng key để replay | Nhận header chưa đồng nghĩa retry an toàn; thêm manual item có thể lặp | LOGIC P1, tách task retry có dữ liệu lưu và kiểm thử. T08 |
| G13 | Generate trả lại ACTIVE list cũ, không regenerate | Sửa meal plan/kho không tự đổi list đã lưu | DOC snapshot; không đổi ngầm sang replace toàn bộ items. Muốn refresh phải có yêu cầu riêng. T01/T09 |
| G14 | Reports thiếu định nghĩa saved_kg và snapshot hạn dùng tại thời điểm dùng | Dễ báo sai, đếm lại leftovers hoặc coi mọi consumption là “tránh lãng phí” | Chốt metric, ghi evidence mới riêng, không sửa ledger cũ. T11/T12/T13 |
| G15 | Barcode mock không có nhánh not-found; OCR trả ngày dạng string date-only trong khi inventory cần datetime có timezone | FE mapping trực tiếp có thể 422; màn not-found không kiểm chứng được | DOC chuyển đổi sau review + fixture not-found xác định. T01/T10 |

Idempotency-Key hiện chỉ bị validate là chuỗi không rỗng, không bắt buộc UUID ở BE. FE nên phát UUID; **một logical request dùng lại cùng key khi retry**, request mới dùng key mới. Không sinh key mới cho từng lần retry và không siết BE chỉ chấp nhận UUID vì sẽ phá key dạng chuỗi của client/test hiện hữu.

## 5. Thiết kế thay đổi đề xuất

### 5.1 NEW — tìm shopping list của user

**`GET /shopping-lists?status=ACTIVE&meal_plan_id=<uuid>&limit=20&offset=0`** — Bearer, không Idempotency-Key.

- Query: status optional (`ACTIVE`/`ARCHIVED`, bỏ trống lấy mọi trạng thái); meal_plan_id optional; limit 1–100, default 20; offset>=0, default 0. FE màn hiện tại gọi `status=ACTIVE&limit=1`.
- Lọc bằng user_id từ JWT; sắp xếp `created_at DESC, id DESC` để “mới nhất” có nghĩa rõ ràng. Một user có thể có nhiều ACTIVE list của nhiều plan.
- Trả summary để tránh load toàn bộ items của các list; FE dùng GET theo id hiện có để đọc items. Không có list trả 200 với items rỗng. UUID không hợp lệ/enum sai/phân trang sai → 422. Filter plan không thuộc user trả collection rỗng, không tiết lộ dữ liệu.
- Response 200 đề xuất:

```json
{
  "items": [
    {
      "id": "uuid",
      "meal_plan_id": "uuid",
      "status": "ACTIVE",
      "generated_at": "2026-09-06T03:00:00Z",
      "created_at": "2026-09-06T03:00:00Z",
      "updated_at": "2026-09-06T03:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

Giữ `GET /shopping-lists/{id}` và mọi mutation. Tận dụng index `ix_shopping_lists_user_status` đang có; chưa thêm index hoặc field `active_shopping_list_id` nếu chưa cần. Phải đăng ký route collection rõ ràng và kiểm tra GET detail vẫn resolve đúng.

### 5.2 REQ — tick mua sắm với storage mặc định

Giữ `PATCH /shopping-lists/{list_id}/items/{item_id}`, response `ShoppingListItemDTO` và Idempotency-Key. Payload cũ đầy đủ vẫn hợp lệ.

```json
{ "checked": true, "purchase": {} }
```

Payload mới trên chỉ hợp lệ khi item có master ingredient với `default_storage_mode` khác null. Quy tắc:

1. `purchase.storage_mode` tường minh luôn được ưu tiên; nếu bỏ qua/null thì lấy default của ingredient. `purchase` vẫn bắt buộc khi checked=true cho cả manual/generated.
2. Không có catalog default hoặc là custom_name thì trả 422 với detail yêu cầu storage_mode; không tự chọn REFRIGERATED cho mọi nguyên liệu.
3. `expires_at` vốn đã optional. Giữ logic shelf-life/expiration_source của `InventoryService.stage_batch`; không tự gán hạn cố định. Giữ validation timezone, finite cost/quantity và XOR identity.
4. Resolve metadata khi thực sự tạo batch; recheck đã có inventory_batch_id vẫn dùng batch cũ, không bị lỗi chỉ vì default catalog sau này thay đổi.
5. Check, batch mới, INITIAL_STOCK ledger và inventory_batch_id trên item cùng transaction; lỗi phải rollback cả ba. Uncheck vẫn không hoàn kho. Checked=false + purchase vẫn 422.

Phương án không sửa BE vẫn dùng được ngay: FE lấy catalog default để điền `purchase.storage_mode`. Kế hoạch REQ giúp giảm phụ thuộc FE phải tải catalog trước, không tạo thêm endpoint “check nhanh”.

### 5.3 RES — nhúng recipe card, vẫn mock recommendation

Thêm `recipe_summary` vào mỗi item của **POST** `/recommendations`, giữ tất cả field cũ và request `{request}`. Summary lấy từ RecipeModel đang được query; không gọi `GET /recipes` nội bộ.

```json
{
  "recipe_id": "uuid",
  "recipe_name": "Grilled chicken breast",
  "recipe_summary": {
    "id": "uuid",
    "name": "Grilled chicken breast",
    "media_url": null,
    "estimated_cooking_minutes": 25,
    "default_servings": "2.00",
    "nutrition": {
      "calories": "330.00",
      "protein_g": "62.00",
      "fat_g": "7.20",
      "carbs_g": "0.00",
      "sugar_g": "0.00",
      "other_nutrients": {}
    }
  }
}
```

Đây là phần bổ sung của item, không phải response thay thế. Nutrition tổng cho **default_servings**, không per-serving; tái sử dụng `RecipeNutritionDTO` và mapping hiện có khi phù hợp. Nếu cần tách mapper đang private ở RecipeService, chỉ tách phần dùng chung thực tế, không tạo tầng provider mới. FE chia theo servings nếu card hiển thị mỗi khẩu phần. Instructions/ingredients vẫn đọc detail khi mở món.

Giữ `analysis.is_mock=true`, `provider=MOCK`, score E/A/P/U giả lập, request không lưu, không tạo recommendation run. Không tích hợp LLM, không tính điểm kho thật, không tạo recipe giả không tồn tại. Field summary nên nullable/default None ở DTO để fixture cũ vẫn tạo được; service hiện tại phải populate cho mọi recipe tìm thấy. FE dùng summary khi có, fallback GET detail cho response BE cũ.

### 5.4 RES/DOC — lỗi extraction, device status, list meal plan

- OCR/ASR: chuyển nhánh MIME/size lỗi sang handler chung, trả `{status_code:422, detail:"...", path:"/api/extractions/..."}`. Giữ status và detail cũ, success envelope/multipart/provider không đổi. Test thiếu file, MIME sai, size vượt giới hạn phải cùng envelope.
- Device: đề xuất đáp ứng M7 bằng **201 cho đăng ký/upsert**, body giữ nguyên. Đây là thay đổi status thật, không được gọi là hoàn toàn tương thích. Triển khai FE nhận cả 200/201 trước, rồi BE 201, cập nhật OpenAPI/test. Nếu chưa chuyển được FE, giữ BE 200 và ghi ngoại lệ contract; không tạo route version mới chỉ vì status.
- Meal-plan list: thêm `response_model=list[MealPlanViewDTO]`, return annotation và order_by rõ ràng. Giữ path có `/` cuối, array và limit/offset; không biến thành `{items,total}` vì FE đang dùng shape cũ. FE chọn plan tuần phải xét toàn bộ trang cần thiết, không chỉ trang đầu. Không thêm PUT plan hoặc xóa các plan trùng tuần.

### 5.5 DECISION — nấu ngay và vòng đời meal-plan item

**Quyết định mặc định của kế hoạch:** giữ `meal_plan_item_id` bắt buộc, theo PRD §7.9. FE “nấu ngay” dùng một plan/item thật với ngày, meal_slot và servings hợp lệ; không gọi đó là item ẩn ở BE. Không thêm `recipe_id` vào request hiện tại trong nhóm công việc bắt buộc.

Các ràng buộc cần FE biết:

- Unique `(meal_plan_id, planned_for, meal_slot)`: một slot hiện chứa một recipe. Không tự retry bằng cách tạo item cùng slot hoặc thay item đã có.
- Ngày item phải nằm trong plan. Có thể tồn tại nhiều plan trùng khoảng ngày, nên FE cần quy tắc chọn plan.
- Không có hidden flag; item có thể xuất hiện trong GET plan và tham gia shopping list. Không dùng tên plan bắt đầu bằng ký tự đặc biệt làm cơ chế ẩn đáng tin cậy.
- Session snapshot recipe/servings lúc tạo. Thay recipe của item sau khi tạo session có thể làm dữ liệu hiển thị khác session; cần guard khi triển khai vòng đời.
- Đề xuất T09: một item biểu diễn một lần nấu. Complete đánh dấu item COMPLETED trong cùng transaction; chặn sửa/xóa item đã được session tham chiếu bằng 409 có ý nghĩa, giữ session/ledger. Các request hoàn tất cùng key phải replay; session thứ hai của cùng item phải không trừ kho lần nữa sau khi item đã completed. Đây là thay đổi nghiệp vụ cần xác nhận khi bắt đầu T09.
- Existing ACTIVE shopping list là snapshot, không tự sửa khi item completed. Khi tạo list mới, chỉ lấy PLANNED như logic hiện có.

**Nhánh P3 nếu sản phẩm quyết định nấu ngoài kế hoạch:** mở rộng *cả* preview và create-session để nhận đúng một trong `{meal_plan_item_id}` hoặc `{recipe_id, servings?}`. Hai trường hợp cùng lúc/không có trường hợp nào → 422; servings mặc định theo recipe, phải dương/hữu hạn. Tái sử dụng build_preview, FEFO, completion, leftovers/history; response đã có meal_plan_item_id nullable và [CookingSessionModel](../../src/backend/src/model/cooking_session_model.py) cho phép null. Không cần xóa FK hay tạo hệ nấu riêng. Bổ sung test direct/planned/cross-user, kiểm tra schema DB deploy khớp nullable trước khi quyết định không cần migration. Chỉ đưa nhánh này vào triển khai sau quyết định sản phẩm, không thực hiện đồng thời workaround item ẩn.

### 5.6 NEW P2 — Reports, định nghĩa trước khi tính số thật

M7 chỉ cho shape, chưa cho nghĩa của “saved”. **Không lấy toàn bộ COOKING_CONSUMPTION hoặc số lượng nhập kho rồi đặt tên saved_kg.** Nền đã có ledger/consumption/session, nhưng `expires_at` của batch có thể bị sửa sau khi nấu, nên query ledger join batch hiện tại không chứng minh batch đã sắp hết hạn lúc dùng.

Đề xuất để chốt ở T11:

- Metric v1 là **ước tính khối lượng nguyên liệu thô được dùng khi sắp hết hạn**, không khẳng định đo được lãng phí tránh được theo quan hệ nhân quả.
- Chỉ tính delta âm của COOKING_CONSUMPTION trên RAW_INGREDIENT, có hạn dùng xác định, chưa hết hạn và nằm trong cửa sổ warning-days tại thời điểm complete. Không cộng INITIAL_STOCK, DISCARD, LEFTOVER_CREATED, metadata/move/archive; không đếm lại cooked leftover. Có thể bổ sung MANUAL_CONSUMPTION sau nếu sản phẩm yêu cầu, không mặc định trộn vào v1.
- Chỉ GRAM/KG quy đổi sang kg bằng quy tắc có sẵn; không coi ML/LITER/PIECE/PACK/OTHER là kg khi chưa có dữ liệu density/mass. Trả thêm số dòng không quy đổi được/thiếu evidence để số 0 không bị hiểu nhầm là đủ dữ liệu.
- Ghi evidence tại transaction nấu: bảng phụ `waste_reduction_events` đề xuất, unique `inventory_ledger_entry_id`, FK user/batch/session/ledger, quantity/unit/mass_kg nullable, expiry lúc dùng, thời điểm dùng, warning-days, metric_version, `is_eligible` và `exclusion_reason`. Tận dụng ledger mới đã tạo trong transaction; không sửa/xóa ledger cũ hoặc bỏ trigger bất biến.
- Lưu snapshot cho các consumption được xét, kể cả trường hợp bị loại vì thiếu hạn dùng/không đổi được đơn vị/cooked leftover; chỉ cộng kg của event eligible. Như vậy có thể phân biệt đã kiểm tra và bị loại với lịch sử chưa có evidence. Metadata coverage (`data_from`, số dòng thiếu evidence) mô tả rõ lịch sử trước ngày bắt đầu chưa đo được. Không backfill bằng expires_at hiện tại rồi xem là số lịch sử chính xác.
- period default `month`; nhận `week|month|year`, sai → 422. Đề xuất dùng kỳ lịch hiện tại theo Asia/Ho_Chi_Minh, lấy đến thời điểm request: tuần bắt đầu thứ Hai, tháng từ ngày 1, năm từ 01/01. Query UTC bằng biên local đã chuyển đổi, khoảng nửa mở.
- Giữ `weekly_series` là array số theo M7: tổng theo các tuần thứ Hai giao với kỳ chọn, tuần đầu/cuối bị cắt theo kỳ. Điền 0 cho tuần đã bắt đầu mà không có event; thêm `weekly_labels` tương ứng và period_start/period_end/timezone để FE không đoán trục. Nếu FE thực tế muốn chart theo ngày cho period=week, cần chốt trước T13, không đổi nghĩa âm thầm.
- `top_saved_ingredients`: group theo identity, tên để hiển thị; top 5 theo kg DESC, identity để phá hòa. `total_saved_kg` bằng tổng **mọi** ingredient trong kỳ, không chỉ top 5; làm tròn ở output. User không có dữ liệu vẫn 200 với tổng 0 và top rỗng, kèm coverage.

Response giữ 4 field M7: `total_saved_kg`, `period`, `weekly_series`, `top_saved_ingredients`. Bổ sung metadata nêu trên là additive. FE tiếp tục mock và ghi rõ là mock tới khi thống nhất metric, có evidence và kiểm thử. Không cần worker báo cáo hoặc cache ở bản đầu; query aggregate trên dữ liệu user bằng service của module `reports` mới.

### 5.7 NEW P2 — Subscription chỉ phục vụ quan tâm premium

- `GET /subscription`: Bearer, response 200 `{ "plan": "free", "expires_at": null }` trong MVP. DTO có thể giữ enum free/premium theo M7; không tạo account premium từ đăng ký quan tâm.
- `POST /subscription/premium-interest`: Bearer, không có business body; trả 200 `{ "registered": true }` sau khi lưu thành công. Gọi lặp trả như nhau, không ghi nhiều lần và không sửa thời điểm đăng ký đầu tiên. Không thêm Idempotency-Key bắt buộc vào API mà M7 chưa yêu cầu; uniqueness theo user đủ cho thao tác này.
- Đề xuất bảng nhỏ `premium_interests` với `user_id` PK/FK và `registered_at` timezone-aware. Không dùng `UserModel.preferences` vì PATCH profile hiện thay cả object, có thể làm mất trạng thái đăng ký; cũng tránh FE tự sửa field này qua profile.
- `GET /subscription` không phụ thuộc đã đăng ký quan tâm hay chưa. Không thêm payment provider, webhook, invoice, checkout, gia hạn hoặc feature gating.
- Nếu lưu DB thất bại trả envelope lỗi, không trả registered=true giả. FE giữ mock cho màn tương ứng tới khi hai route sẵn sàng.

### 5.8 Yêu cầu thay đổi database để triển khai API Phase 2

Mục này là đặc tả dữ liệu **đề xuất cho lần triển khai**, không mô tả bảng đã tồn tại. M7 quy định API; các bảng phụ dưới đây là lựa chọn triển khai để bảo đảm retry, số liệu lịch sử và persistence. Không biến lựa chọn bảng thành yêu cầu FE phải gửi thêm field nội bộ.

#### 5.8.1 Ma trận API → model → thay đổi schema

| API / task | Model và dữ liệu hiện có | Thêm field bảng cũ | Xóa/đổi field bảng cũ | Công việc database thực tế |
|---|---|---|---|---|
| `GET /shopping-lists`, T05 | ShoppingListModel có user_id, meal_plan_id, status, generated_at, created_at, updated_at | Không | Không | Query/filter/count; dùng index user/status sẵn có. Không cần migration |
| PATCH shopping purchase, T06 | MasterIngredientModel.default_storage_mode; ShoppingListItemModel.source_metadata lưu inventory_batch_id | Không | Không | Resolve default tại service. InventoryBatchModel.storage_mode vẫn NOT NULL, không làm nullable theo DTO |
| POST/PATCH/DELETE shopping, T08 | Key có ở API nhưng thiếu persistence replay đầy đủ | Không | Không | Thêm ShoppingMutationReceiptModel / shopping_mutation_receipts, migration DB-01 |
| `POST /recommendations`, T07 | RecipeModel có media_url, estimated_cooking_minutes, default_servings, total_calories/protein/fat/carbs/sugar và other_nutrients | Không | Không | Map thành recipe_summary DTO. Không tạo cột JSON recipe_summary, không ghi RecommendationRunModel/RecommendationItemModel khi vẫn mock |
| GET meal plans, T04 | MealPlanModel đã có timestamp, khoảng ngày và ownership | Không | Không | order_by + DTO; chưa thêm index trước khi có bằng chứng query cần tối ưu |
| Cooking completion, T09 | MealPlanItemModel.status và CookingSessionModel.meal_plan_item_id đã có | Không | Không | Lock/update dữ liệu cùng transaction; giữ FK, unique slot và enum. Không backfill trạng thái hàng loạt |
| Direct cooking, nhánh P3 | CookingSessionModel.meal_plan_item_id đã nullable trong model | Không theo schema hiện tại | Không xóa FK | Chỉ mở request/service nếu được chọn; kiểm tra schema deploy trước khi kết luận không cần migration |
| Reports, T11–T13 | InventoryLedgerEntryModel có delta/unit/batch/session nhưng không snapshot hạn dùng lúc tiêu thụ | Không | Không | Thêm WasteReductionEventModel / waste_reduction_events, migration DB-02; giữ ledger bất biến |
| `GET /subscription`, T15 | MVP luôn free/null | Không | Không | Không cần bảng subscription, plan hoặc payment |
| `POST /subscription/premium-interest`, T14/T15 | UserModel.preferences bị replace qua profile nên không phù hợp lưu đăng ký hệ thống | Không | Không | Thêm PremiumInterestModel / premium_interests, migration DB-03 |
| Device status, extraction errors/barcode mock, T02/T03/T10 | Model device/notification hiện đủ; extraction không lưu DB | Không | Không | Chỉ router/DTO/provider; không tạo bảng OCR/ASR/barcode |
| Auth/User/Favorites/Catalog/Inventory còn lại | Các bảng đã triển khai | Không | Không | Giữ nguyên; thay tài liệu hoặc mapping API theo ma trận mục 3 |

**Các field không thêm trong phương án này:** active_shopping_list_id trên meal plan, is_hidden trên item, recipe_summary trên recipe, subscription_plan/premium_interest trong users.preferences và saved_kg trên inventory_batches. Dữ liệu tổng hợp được trả qua DTO hoặc tính từ evidence, tránh hai nơi lưu cùng một giá trị dễ lệch nhau.

#### 5.8.2 Quy ước model và migration dùng chung

- File mới đặt trong `src/backend/src/model/`; đăng ký import và `__all__` tại [model/__init__.py](../../src/backend/src/model/__init__.py) để Base.metadata nhận diện. [alembic/env.py](../../src/backend/alembic/env.py) hiện lấy metadata qua `from src.model import Base`.
- Tái sử dụng [base.py](../../src/backend/src/model/base.py): receipt/event dùng CreatedAtUUIDModel, kế thừa `id` UUID PK do generate_uuid7 tạo và `created_at` TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP. Không thêm updated_at vào bản ghi chỉ append. PremiumInterestModel dùng Base trực tiếp vì user_id đã là PK, không cần id thứ hai.
- Tất cả thời điểm persisted dùng DateTime(timezone=True); ứng dụng ghi thời gian UTC, chuyển biên kỳ Reports theo timezone sản phẩm. Không dùng datetime naive hoặc timestamp local không có timezone.
- FK tới bảng cũ giữ dữ liệu khi xóa cha: không thêm ON DELETE CASCADE cho receipt/evidence/interest. Không thêm relationship hai chiều vào tất cả model cha nếu service chỉ query bằng FK; thêm relationship một chiều khi thực sự dùng.
- Enum unit và batch type của bảng event tái sử dụng các PostgreSQL enum hiện có (`measurement_unit`, `inventory_batch_type`); migration không CREATE TYPE trùng hoặc DROP TYPE dùng chung. Trạng thái eligibility của metric dùng boolean/string có CHECK, không mở rộng enum ledger để phục vụ báo cáo.
- Quy định NOT NULL/default/FK/UNIQUE/CHECK bên dưới phải có trong **cả model lẫn migration**. Các quy tắc ownership liên bảng vẫn cần kiểm tra trong service: một FK hợp lệ không tự chứng minh mọi row cùng user.

#### 5.8.3 DB-01 — shopping_mutation_receipts / ShoppingMutationReceiptModel

**Liên kết yêu cầu:** contract §6 và quy ước Idempotency-Key; gap G12; task T08a/T08b. Bảng hỗ trợ replay kết quả mutation, không thay ShoppingListModel hoặc ShoppingListItemModel.

| Field | Kiểu DB đề xuất | Null/default/khóa | Nguồn và ý nghĩa |
|---|---|---|---|
| id | UUID | PK, generate_uuid7 từ base | ID bản ghi nội bộ, không gửi cho FE |
| created_at | TIMESTAMPTZ | NOT NULL, CURRENT_TIMESTAMP | Thời điểm ghi receipt |
| user_id | UUID | NOT NULL, FK users.id | User từ JWT đã xác thực |
| method | VARCHAR(6) | NOT NULL | POST/PATCH/DELETE, uppercase |
| request_path | VARCHAR(255) | NOT NULL | Path canonical có resource ID, ví dụ `/api/shopping-lists/<uuid>/items/<uuid>`; không query string |
| idempotency_key | TEXT | NOT NULL | Giá trị header gốc; không lưu token Authorization |
| key_hash | VARCHAR(64) | NOT NULL | SHA-256 của key gốc để index không phụ thuộc độ dài key; không đổi rule API chỉ nhận chuỗi không rỗng |
| request_fingerprint | VARCHAR(64) | NOT NULL | SHA-256 body request đã chuẩn hóa; dùng phát hiện reuse key với payload khác |
| response_status | SMALLINT | NOT NULL | HTTP status kết quả thành công cần replay: 200/201/204 |
| response_body | JSONB | NULL chỉ khi 204 | JSON public DTO đúng lúc mutation hoàn thành, không lưu ORM/private metadata |

Ràng buộc/index:

- UNIQUE `uq_shopping_receipt_scope_key` trên `(user_id, method, request_path, key_hash)`; đây cũng là index tra replay. Không tạo thêm index trùng bộ cột này.
- CHECK method thuộc POST/PATCH/DELETE; response_status thuộc 200/201/204; key không rỗng; hash/fingerprint đúng dạng 64 hex lowercase.
- CHECK 204 tương ứng response_body SQL NULL; 200/201 tương ứng JSON object. Phân biệt SQL NULL với JSON `null` khi mapping JSONB.
- Không đặt FK receipt → shopping item: DELETE nghiệp vụ được phép xóa item nhưng receipt phải còn để replay 204. Request_path giữ định danh resource.

Quy trình service bắt buộc:

1. Validate request và auth; canonicalize UUID/path. Fingerprint từ payload đã validate với các field được gửi (`exclude_unset`), sort key ổn định và giữ khác biệt omitted/null khi có nghĩa nghiệp vụ. Tính fingerprint **trước** khi resolve catalog default, để thay default catalog không làm retry payload cũ bị 409. Không đưa thời điểm server, kết quả query hay JWT vào fingerprint.
2. Lấy lock resource cha theo thứ tự thống nhất: generate lock plan; add/update/remove lock shopping list thuộc user. Tra receipt trước khi tìm item có thể đã bị DELETE. Nếu có receipt, so sánh key gốc và fingerprint: khớp → replay status/body; khác → 409, không mutation. So sánh key gốc cũng tránh xử lý nhầm trường hợp hash collision.
3. Chưa có receipt → thực hiện business mutation dùng service hiện có, build DTO, lưu receipt rồi commit **cùng transaction**. Row lock cha và unique scope phối hợp chống concurrent duplicate; không commit business write trước rồi mới lưu receipt.
4. Lỗi validation/business/DB rollback không lưu receipt thành công. Nếu gặp unique conflict từ writer khác, rollback transaction hiện tại trước khi đọc receipt winner và kiểm tra fingerprint; không truy vấn trên transaction đang lỗi.
5. Replay trả snapshot response cũ; FE dùng GET nếu muốn trạng thái mới nhất. Batch/link INITIAL_STOCK có sẵn tiếp tục chống nhập kho trùng khi user recheck bằng key mới.

Chỉ lưu successful receipt nên không cần status PROCESSING, lease, background worker hoặc TTL cleanup trong đợt đầu. Bản ghi cũ trước rollout không có receipt: không dựng receipt từ suy đoán và không hứa replay được các request lịch sử đó. Nếu client cũ đang có mutation chưa rõ thành công, đối chiếu GET trước khi gửi lại sau cutover.

#### 5.8.4 DB-02 — waste_reduction_events / WasteReductionEventModel

**Liên kết yêu cầu:** contract §10; gap G14; task T11/T12a/T12b/T13. Chỉ tạo sau khi chốt metric mục 5.6. Bảng lưu evidence mỗi lần tiêu thụ để Reports có thể giải thích số liệu; không thêm/sửa field của inventory ledger.

| Field | Kiểu DB đề xuất | Null/default/khóa | Nguồn và ý nghĩa |
|---|---|---|---|
| id | UUID | PK, generate_uuid7 từ base | ID event |
| created_at | TIMESTAMPTZ | NOT NULL, CURRENT_TIMESTAMP | Thời điểm ghi event, không dùng thay consumed_at để chia kỳ |
| inventory_ledger_entry_id | UUID | NOT NULL, FK inventory_ledger_entries.id, UNIQUE | Mỗi ledger tiêu thụ tối đa một snapshot |
| user_id | UUID | NOT NULL, FK users.id | Cùng owner với ledger, batch và session |
| inventory_batch_id | UUID | NOT NULL, FK inventory_batches.id | Batch đã tiêu thụ |
| cooking_session_id | UUID | NOT NULL, FK cooking_sessions.id | Session hoàn tất; v1 chỉ xét COOKING_CONSUMPTION |
| master_ingredient_id | UUID | Nullable, FK master_ingredients.id | Identity để group; null với batch không có catalog identity |
| ingredient_name_snapshot | TEXT | NOT NULL, không rỗng | Tên tại thời điểm dùng; không bắt buộc join tên hiện tại khi hiển thị lịch sử |
| batch_type_snapshot | inventory_batch_type | NOT NULL | RAW_INGREDIENT hoặc COOKED_FOOD tại lúc dùng |
| quantity | NUMERIC | NOT NULL, >0 | Số lượng thực tế bị trừ, biểu diễn dương, lấy từ `-ledger.quantity_delta` |
| unit | measurement_unit | NOT NULL | Unit của ledger/batch, không phải unit recipe sau scale |
| mass_kg | NUMERIC | Nullable; có giá trị thì >0 | KG giữ nguyên, GRAM chia 1000; null nếu chưa có quy tắc đổi kg |
| expires_at_snapshot | TIMESTAMPTZ | Nullable | Hạn dùng thực tế tại lúc complete; null phải giữ nghĩa UNKNOWN |
| consumed_at | TIMESTAMPTZ | NOT NULL | Cùng mốc với session.completed_at, chụp một lần cho transaction |
| warning_days | INTEGER | NOT NULL, >=0 | Cấu hình cửa sổ sắp hết hạn đã dùng để xét event |
| metric_version | VARCHAR(32) | NOT NULL, không default ngầm | Ví dụ `near-expiry-v1`; writer gửi phiên bản đã được chốt |
| is_eligible | BOOLEAN | NOT NULL, không default ngầm | Event có được cộng vào saved kg theo metric hay không |
| exclusion_reason | VARCHAR(32) | Nullable | Null khi eligible; một lý do xác định khi excluded |

Quy tắc ghi và ràng buộc:

- UNIQUE `uq_waste_event_ledger` trên inventory_ledger_entry_id; index `ix_waste_events_user_consumed_at` trên `(user_id, consumed_at)`. Không tạo bảng tổng tuần/tháng/năm hoặc cột total_saved_kg ở user.
- Numeric mới giữ precision không ép về số chữ số cố định làm mất lượng nhỏ; chuẩn hóa từ `Decimal(str(value))` của ledger float hiện có. Writer từ chối NaN/Infinity; CHECK tương ứng phải loại giá trị đặc biệt bên cạnh điều kiện >0. Không đổi kiểu các cột float hiện hữu trong Phase 2.
- CHECK eligible: mass_kg và expires_at_snapshot khác null, batch_type_snapshot=RAW_INGREDIENT, exclusion_reason null. CHECK excluded: exclusion_reason khác null, thuộc tập `COOKED_FOOD`, `UNKNOWN_EXPIRATION`, `EXPIRED`, `OUTSIDE_WARNING_WINDOW`, `UNSUPPORTED_UNIT`. Eligibility theo thời gian và tính nhất quán FK/quantity/unit kiểm tra trong service; không dựng trigger join chéo toàn bộ bảng.
- Ưu tiên lý do khi một event có nhiều điều kiện loại: cooked food → unknown expiry → expired → ngoài cửa sổ warning → không đổi được unit. Nếu trả `unsupported_unit_count`, đếm event có mass_kg null; không chỉ đếm exclusion_reason vì có thể có lý do khác được ưu tiên.
- Nếu dùng quy tắc freshness theo ngày của InventoryService: dùng cùng ngày local và warning-days để xét expired/expiring, gồm cả ngày hết hạn. T11 phải ghi rõ lựa chọn này với FE; không trộn so sánh date của kho với timestamp chính xác trong Reports. Chụp expires_at gốc để sau này kiểm chứng lại được.
- Event eligible/excluded phải cùng ledger event_type=COOKING_CONSUMPTION, cùng user/batch/session, quantity bằng lượng thực trừ và unit trùng ledger. Không nhận các field evidence từ body FE hoặc tự tin dữ liệu vì FK tồn tại.

Nối với code hiện có:

1. `apply_quantity_change()` trong InventoryService **đã trả InventoryLedgerEntryModel**. CookingHelper giữ lại object trả về, chụp metadata batch trước mutation và dùng cùng mốc complete; không cần viết lại hàm kho chỉ để lấy ledger ID.
2. Flush các ledger mới trong transaction để UUID/default đã có rồi thêm events, hoặc dùng ORM relationship phù hợp để SQLAlchemy giữ thứ tự insert. Không dùng ledger.id chưa được sinh và không commit giữa hai bước.
3. Commit session/consumption/batch/ledger/evidence và trạng thái item nếu T09 được chọn trong một transaction. Lỗi event phải rollback toàn bộ completion. Không query/network/report aggregate từ bên trong vòng lặp trừ kho.
4. Cùng-key replay trả completion cũ, không thêm event; unique ledger chống event trùng. Sau khi ghi, event được dùng như snapshot chỉ đọc; không sửa event theo expires_at/name hiện tại. Không bổ sung API PATCH/DELETE event.
5. Query Reports lọc user_id, metric_version và consumed_at trong kỳ, cộng mass_kg **chỉ khi is_eligible=true**. Khi tên catalog đổi, group theo master_ingredient_id; tên hiển thị chọn snapshot mới nhất trong kỳ với tie-break id, không tách một ingredient thành nhiều dòng vì tên khác nhau. Với identity custom, dùng quy tắc normalized name được chốt ở T11.

Lịch sử và coverage:

- Migration tạo bảng rỗng. Không backfill hạn dùng từ batch hiện tại, không sửa/xóa ledger cũ và không bỏ trigger `inventory_ledger_entries_immutable`.
- `data_from` là consumed_at sớm nhất có snapshot của user, null nếu chưa có. Nó không tự chứng minh dữ liệu liên tục/đầy đủ, đặc biệt khi chạy đồng thời phiên bản app cũ và mới.
- Đếm `missing_evidence_count` từ COOKING_CONSUMPTION ledger của user join session đã hoàn tất trong kỳ theo completed_at, LEFT JOIN event và lấy các dòng thiếu evidence phù hợp phiên bản metric. Như vậy khoảng trống trước rollout và do writer cũ đều được phản ánh.
- `unsupported_unit_count` lấy từ event trong kỳ có mass_kg null. Không nhập hai khái niệm thiếu evidence và không đổi được unit làm một.
- Nếu chưa có event, API trả tổng 0 cùng coverage; FE không diễn giải là đã chứng minh không có lượng thực phẩm được tiết kiệm. Không tạo event 0 giả để lấp lịch sử.
- Thay đổi định nghĩa metric sau v1 phải có kế hoạch version riêng; unique theo ledger hiện chỉ giữ một snapshot/event, không tự ghi event thứ hai để cộng lại cùng consumption.

#### 5.8.5 DB-03 — premium_interests / PremiumInterestModel

**Liên kết yêu cầu:** contract §11, task T14/T15. Không đồng nghĩa triển khai subscription có thanh toán.

| Field | Kiểu DB đề xuất | Null/default/khóa | Ý nghĩa |
|---|---|---|---|
| user_id | UUID | PK, FK users.id, NOT NULL | Một đăng ký quan tâm cho mỗi user |
| registered_at | TIMESTAMPTZ | NOT NULL, CURRENT_TIMESTAMP | Thời điểm đăng ký đầu tiên |

- Không thêm id, updated_at, plan, expires_at, payment_status hoặc email snapshot khi M7 chưa dùng. PK đã là index cho lookup/upsert, không cần unique/index user_id trùng lặp.
- POST lấy user từ JWT, insert nếu chưa có; conflict user_id thì giữ nguyên row và registered_at. Trả registered=true sau commit; không đổi user.role hoặc preferences. DB failure không được trả thành công giả.
- GET subscription vẫn trả free/null dù có hoặc không có interest. Không tạo bảng subscription chỉ để lưu hai giá trị hằng này.
- Không backfill user hiện tại thành “đã quan tâm”; bảng rỗng đúng trạng thái chưa đăng ký. Không copy dữ liệu FE mock vào DB như đăng ký thật.

#### 5.8.6 Thay đổi dữ liệu không đổi schema: meal-plan completion

T09 dùng MealPlanItemModel.status đã có; không thêm is_completed/completed_at trùng nghĩa vào item và không sửa status enum. Transaction phải giữ lock item khi kiểm tra PLANNED và chuyển COMPLETED; hai session cạnh tranh cùng item phải không cùng được trừ kho.

Thống nhất lock order giữa create-session, complete và PATCH/DELETE item để tránh race với lúc kiểm tra session tham chiếu: các luồng liên quan lấy plan → item → session → inventory batches khi cần, với thứ tự batch ổn định. Replay đọc trước có thể trả ngay nếu kết quả đã tồn tại, nhưng mọi nhánh ghi phải kiểm tra lại dưới lock. Khi direct-cook được chọn và không có item, nhánh đó chỉ lấy các lock còn phù hợp. Nếu mã hiện tại dùng thứ tự khác, chỉnh các caller cùng phạm vi T09 và test cạnh tranh trước khi đưa vào dùng.

Không tự thêm unique meal_plan_item_id vào cooking_sessions: cần giữ session đã có, và có thể có nhiều session PLANNED cũ. Trước rollout T09, thống kê item có nhiều session/completed session và item PLANNED nhưng có session completed; chỉ đọc để phân loại. Dữ liệu lịch sử cần xử lý theo quyết định sản phẩm, không xóa session hoặc update hàng loạt trong schema migration. Khi chạy writer cũ/mới song song, quy tắc một item/một lần nấu chưa được bảo đảm từ writer cũ; chuyển đồng bộ các worker API thực hiện completion trước khi công bố quy tắc mới.

#### 5.8.7 Thứ tự migration và file BE phải chạm

Chuỗi revision đang có trong source lúc rà soát:

```text
2ca31dd74ae1 → 7b1f4d2a9c30 → e15d3a9b4c72
                                   ↑ head trong source hiện tại
```

Head này lấy từ file migration, **chưa phải kết quả kiểm tra database deploy**. Khi triển khai phải đọc head/current thực tế; không hard-code lại head trong kế hoạch nếu repo đã có migration mới.

| Migration | Task | Thao tác upgrade | Model/file liên quan | Điều kiện sẵn sàng |
|---|---|---|---|---|
| DB-01: phase2_shopping_mutation_receipts | T08a | CREATE bảng receipt + FK/CHECK/UNIQUE ở mục 5.8.3 | model/shopping_mutation_receipt_model.py, model/__init__.py, migration mới | Semantics key/fingerprint/replay đã chốt |
| DB-02: phase2_waste_reduction_events | T12a | CREATE bảng event + FK/CHECK/UNIQUE/index ở mục 5.8.4; tái sử dụng enum cũ | model/waste_reduction_event_model.py, model/__init__.py, migration mới | T11 metric đã chốt; không backfill bằng dữ liệu thiếu bằng chứng |
| DB-03: phase2_premium_interests | T14 | CREATE bảng interest + PK/FK/default ở mục 5.8.5 | model/premium_interest_model.py, model/__init__.py, migration mới | API đăng ký quan tâm được lên lịch |

DB-01/02/03 là mã công việc, không phải revision ID có thể chạy ngay. Sinh revision ID thực khi triển khai, mỗi revision down_revision trỏ head sau migration đã merge trước đó. Ba bảng không phụ thuộc dữ liệu lẫn nhau, có thể đổi thứ tự theo lịch phát hành; không tạo nhiều head hoặc migration rỗng cho tính năng chưa triển khai.

Service/DTO/router mapping ngoài model:

- DB-01 đi cùng shopping_service và test retry; DTO hiện tại không phải nhận receipt_id/hash. Không thêm public API quản lý receipt.
- DB-02 đi cùng cooking_helper ghi snapshot, reports_service đọc aggregate; giữ field response M7, bổ sung coverage theo T11. Hàm apply_quantity_change hiện có đã trả ledger nên chỉ sửa inventory_service nếu phát hiện một nhu cầu cụ thể khác.
- DB-03 đi cùng subscription_service/upsert; UserModel không cần thêm field hay relationship ngược chỉ để registration hoạt động.

#### 5.8.8 Quy trình nâng cấp, kiểm tra target và rollback

1. **Đối chiếu baseline:** kiểm tra Alembic head/current, kiểu enum, nullability, FK/index/trigger hiện tại. Nếu schema deploy lệch source thì lập migration sửa đúng sai lệch đã kiểm chứng, không reset DB hoặc dùng stamp để bỏ qua schema thiếu.
2. **Tách DB test đúng cách:** fixture pytest đọc TEST_DATABASE_URL, nhưng alembic/env.py hiện ghi URL từ **DATABASE_URL**; chỉ export TEST_DATABASE_URL không chuyển target của CLI Alembic. Dùng test helper đã guard hai URL khác nhau, sau đó truyền DATABASE_URL=URL test **chỉ trong environment của subprocess Alembic**, giữ URL app gốc cho guard. Không sửa `.env` dùng chung, không in credential hoặc giả định sửa alembic.ini sẽ thắng env.py.
3. **Kiểm thử upgrade:** trên DB test đã migrate tới head cũ và có fixture dữ liệu, chạy revision mới bằng Alembic. Không dùng metadata.create_all thay thế kiểm tra upgrade. Snapshot row count/PK/FK/số dư/ledger trước và sau; bảng mới rỗng, các bảng cũ không đổi dữ liệu.
4. **Rà migration sinh tự động:** chỉ có ba bảng/constraint đã chọn. Loại khỏi revision các thao tác drop/rename/type-change ngoài phạm vi hoặc CREATE TYPE trùng enum hiện có; kiểm tra SQL trước khi thực thi.
5. **Phát hành schema trước code:** app cũ phải chạy được trên schema mới. Chỉ triển khai writer receipt/event/interest sau khi bảng cần dùng đã có; không catch undefined-table rồi lặng lẽ bỏ receipt/evidence. Với Reports, triển khai writer snapshot trước, sau đó reader và FE; khoảng trống mixed-version được coverage phản ánh.
6. **Rollback:** ưu tiên rollback app, giữ schema/bản ghi mới; receipt/evidence/interest không bị xóa khi quay lại phiên bản cũ. Sau rollback writer Reports, reader phải coi đó là khoảng trống evidence nếu còn được dùng. Không chạy downgrade xóa bảng có dữ liệu hoặc sửa migration cũ. Nếu hỗ trợ downgrade cho DB test, phải fail rõ khi bảng mới không rỗng; không dùng CASCADE để vượt qua dữ liệu tham chiếu.

Repo còn có [scripts/alembic_baseline_reconcile.py](../../src/backend/scripts/alembic_baseline_reconcile.py) với CURRENT_HEAD=7b1f4d2a9c30 cho quy trình reconcile lịch sử. Không dùng script đó để stamp database Phase 2 về revision cũ, không đổi hằng sang head mới mà chưa cập nhật toàn bộ kiểm tra fingerprint của script. Migration Phase 2 đi bằng Alembic bình thường sau khi baseline đã đúng; nếu cần reconcile DB lịch sử, đó là bước riêng có kiểm chứng.

#### 5.8.9 Bộ nghiệm thu database bắt buộc

| Mã | Fixture / thao tác | Kết quả phải kiểm tra | Task |
|---|---|---|---|
| DB-V01 | DB test có users/plans/items/batches/ledger/favorites trước upgrade | Upgrade giữ nguyên PK, số row và số dư; ledger trigger và unique slot vẫn tồn tại; ba bảng mới chỉ xuất hiện theo revision đã chọn | T08a/T12a/T14 |
| DB-V02 | Inspect Base.metadata và DB sau upgrade | Khớp column/type/null/default/FK/UNIQUE/CHECK/index của 5.8; không enum type trùng hoặc diff ngoài phạm vi | T08a/T12a/T14 |
| DB-V03 | Hai POST add shopping item đồng thời cùng key/body | Một item + một receipt; hai response cùng resource ID; không nhân đôi stock | T08b |
| DB-V04 | Cùng scope/key khác body; cùng key khác user/resource | Trường hợp đầu 409 không ghi thêm; trường hợp sau độc lập theo scope và ownership | T08b |
| DB-V05 | DELETE item xong gọi lại cùng key; lỗi trước commit receipt | Retry replay 204 dù item đã mất; transaction lỗi không để business write hoặc receipt thành công | T08b |
| DB-V06 | Check/uncheck/recheck mua sắm, có default/null/custom và concurrent check | Đúng storage đã resolve; batch.storage_mode vẫn NOT NULL; tối đa một INITIAL_STOCK/batch cho item | T06/T08b |
| DB-V07 | Complete session thành công rồi retry; lỗi khi insert event | Mỗi ledger một event, sum quantity event trùng lượng ledger; lỗi event rollback stock/ledger/session/item | T12b/T09 |
| DB-V08 | Sửa expiry/tên batch sau complete; RAW/KG/GRAM/ML/cooked/unknown-expiry fixtures | Snapshot/tổng lịch sử không đổi; kg/eligibility/reason đúng metric; không tính kép leftover | T12b/T13 |
| DB-V09 | Ledger cũ thiếu event, event bị loại, kỳ rỗng và kỳ giao tuần/năm | Missing evidence khác unsupported unit; period dùng consumed_at/completed_at đã chốt; không leak user khác | T13 |
| DB-V10 | Hai premium-interest POST đồng thời rồi PATCH profile preferences | Một row/user, registered_at đầu tiên không đổi, profile không xóa interest, GET subscription vẫn free/null | T14/T15 |
| DB-V11 | Hai session cùng item complete cạnh tranh với sửa/xóa item | Writer đã nâng cấp giữ một lần nấu/item, conflict có ý nghĩa, không FK error/partial write hoặc deadlock do lock order không nhất quán | T09 |
| DB-V12 | App cũ đọc/ghi trên schema mới; rollback app sau khi có bảng mới | API cũ vẫn hoạt động; không chạy cleanup/drop dữ liệu mới; coverage phản ánh writer cũ không ghi event | Các task có migration |

Các case này phải dùng DB test thật cho lock/constraint/transaction; test DTO/router fake chỉ kiểm chứng HTTP shape. Test fixture không được chạy delete/drop/create-all trên database ứng dụng. Ghi số case pass/skip và target biệt lập trong kết quả triển khai; skip vì thiếu DB test là chưa nghiệm thu database.

## 6. Kế hoạch thực thi theo task

Các file bên dưới là **file dự kiến tác động lúc triển khai**; chưa được sửa/tạo trong lần lập kế hoạch này. Đường dẫn module/test/model tính từ `src/backend/src/`; migration tính từ `src/backend/alembic/versions/`. S = nhỏ, M = trung bình; mỗi task có thể review riêng. Task lớn được tách theo dữ liệu/endpoint để tránh viết lại hàng loạt.

### Nhóm A — khớp contract hiện tại

#### T01 — P0/S: hoàn thiện tài liệu hiện trạng và mapping FE

- **Việc làm:** cập nhật `docs/api-contract.md` theo ma trận mục 3–4; thêm Auth/User/Favorites, ngoại lệ text/204, device 200 hiện tại và 201 mục tiêu, Decimal nullable, inventory reason/summary/adjustment, purchase cho mọi item, barcode query, mock không phân tích request, generate snapshot và chính sách key khi retry.
- **File:** `docs/api-contract.md`; tham chiếu `src/backend/docs/phase5-api-spec.md` và `product-flow.md` chỉ ở phần thực sự cần đồng bộ sau thay đổi.
- **Phụ thuộc:** không có.
- **Nghiệm thu:** [ ] Mọi operation M7 được map sang code hoặc NEW; [ ] 29 route Auth/User/Favorites có body/status/auth đúng, không bị ghi là thiếu BE; [ ] JSON mẫu và lời mô tả không mâu thuẫn DTO.
- **Kiểm chứng:** đối chiếu OpenAPI với các router; review các trường hợp `checked=true`, inventory PATCH reason và plain-text acknowledgment. Không dùng test cũ làm nguồn thay code khi hai bên khác nhau.

#### T02 — P0/S: sửa envelope lỗi OCR/ASR

- **Việc làm:** thay ba nhánh trả JSONResponse lỗi bằng cơ chế lỗi chung hiện có; bổ sung khai báo response lỗi nếu cần codegen.
- **File:** `module/extractions/extraction_route.py`, `test/test_extractions.py`; tái sử dụng `core/exceptions.py`, không tạo error framework.
- **Phụ thuộc:** T01 xác định schema lỗi.
- **Nghiệm thu:** [ ] label/invoice/asr lỗi MIME/size/thiếu file đều 422 đủ ba field; [ ] success và persisted=false giữ nguyên; [ ] detail không lộ nội dung file.
- **Kiểm chứng:** `python -m pytest -q src/test/test_extractions.py` trong BE; kiểm tra response body, không chỉ status.

#### T03 — P0/S: đồng bộ status device

- **Việc làm:** FE chấp nhận 200/201; BE đổi route registration sang 201 theo mục 5.4; giữ disable 204 và upsert theo token.
- **File BE:** `module/notification/notification_router.py`, `test/test_notification_router.py`; cập nhật contract trong cùng đợt. File client FE cần xác định khi triển khai, không đoán đường dẫn từ contract.
- **Phụ thuộc:** T01, điều kiện chuyển đổi FE nhận được cả hai status.
- **Nghiệm thu:** [ ] request cũ/platform cũ/body cũ hoạt động; [ ] đăng ký lần đầu và đăng ký lại trả status đã chốt, không thêm device trùng; [ ] response không lộ fcm_token.
- **Kiểm chứng:** `python -m pytest -q src/test/test_notification_router.py src/test/test_notification_service.py`; kiểm tra OpenAPI và client thật.

**Checkpoint A:** các mismatch P0 có test/ví dụ đúng; chỉ đổi status theo lịch tương thích; không xóa endpoint nào.

### Nhóm B — hoàn thiện luồng FE chính

#### T04 — P1/S: cố định contract list meal plan

- **Việc làm:** khai báo response_model/annotation, thêm order_by ổn định cho get_all, giữ array/path/limit/offset.
- **File:** `module/meal_plans/meal_plan_router.py`, `meal_plan_service.py`, `test/test_meal_plan_router.py`; dùng MealPlanViewDTO hiện có.
- **Phụ thuộc:** T01.
- **Nghiệm thu:** [ ] OpenAPI trả array có đủ timestamp; [ ] user A không thấy plan user B, limit/offset ổn định trên fixture nhiều plan; [ ] GET detail và CRUD item giữ nguyên shape.
- **Kiểm chứng:** mở rộng test list đang thiếu; chạy `python -m pytest -q src/test/test_meal_plan_router.py`, thêm integration query thứ tự trên DB test.

#### T05 — P1/M: bổ sung GET shopping-lists

- **Việc làm:** query DTO, summary/list DTO, route collection, service list/count user-scoped theo mục 5.1; không thêm model mới.
- **File:** `module/shopping_lists/shopping_dto.py`, `shopping_router.py`, `shopping_service.py`, `test/test_shopping_router.py`, test integration shopping phù hợp.
- **Phụ thuộc:** T01; có thể triển khai độc lập T04 nhưng phải xong trước test luồng phục hồi sau đổi máy.
- **Nghiệm thu:** [ ] status/plan/limit/offset hoạt động, 200 empty khi chưa có list; [ ] sort mới nhất ổn định và không lộ user khác; [ ] lấy id từ list rồi GET detail cũ hiển thị đúng items, không phát sinh write.
- **Kiểm chứng:** test route/schema và query DB với nhiều ACTIVE list của nhiều plan/user, boundary limit=0/101, offset âm và invalid enum.

#### T06 — P1/M: default storage khi xác nhận mua

- **Việc làm:** làm ShoppingPurchaseDTO.storage_mode optional; resolve default trong service trước stage_batch, giữ validation inventory. Không bỏ purchase required.
- **File:** `module/shopping_lists/shopping_dto.py`, `shopping_service.py`, `test/test_shopping_router.py`, thêm `test/test_shopping_purchase_service.py` nếu test hiện tại chưa bao phủ service.
- **Phụ thuộc:** T01; trước khi làm xác nhận quy tắc fallback ở mục 5.2 là yêu cầu được chọn, nếu chỉ cần prefill FE thì bỏ thay đổi BE này.
- **Nghiệm thu:** [ ] payload cũ và purchase={} có catalog default tạo đúng storage; [ ] custom/default-null thiếu storage → 422 không tạo batch; [ ] retry/recheck/uncheck giữ một batch và một INITIAL_STOCK, lỗi rollback nguyên transaction.
- **Kiểm chứng:** test service cả manual/generated, explicit override, default null, timezone sai; integration stock+ledger count trước/sau cạnh tranh check.

#### T07 — P1/M: thêm recipe_summary cho recommendation mock

- **Việc làm:** thêm summary DTO và mapping trên RecipeModel đang tải; giữ mock score/analysis/request, summary nutrition default servings.
- **File:** `module/recommendations/recommendation_dto.py`, `recommendation_service.py`, `test/test_recommendation_provider.py`, `test/test_recommendation_router.py`; chỉ sửa mapper `module/recipes/recipe_service.py` nếu thực sự tái sử dụng được.
- **Phụ thuộc:** T01 thống nhất shape mục 5.3.
- **Nghiệm thu:** [ ] mọi field cũ giữ nguyên, is_mock/provider giữ nguyên; [ ] summary id/name và nutrition khớp recipe detail ở default servings, nullable media/nutrition được hỗ trợ; [ ] 0/1/5 recipe hợp lệ, không query N lần hoặc ghi run/kho.
- **Kiểm chứng:** hai file test recommendation + fixture so sánh recipe detail; đếm query bằng spy/fake session để xác nhận không N+1.

**Checkpoint B1:** từ tài khoản trên thiết bị mới tìm được list active; check mua sắm nhập kho đúng một lần; card gợi ý render từ response vẫn ghi rõ mock; GET recipe detail vẫn dùng được.

#### T08a — P1/M: dữ liệu replay cho mutation shopping

- **Database:** thực hiện DB-01 theo mục 5.8.3/5.8.7; nghiệm thu DB-V01/02, giữ raw key và dùng key_hash cho unique scope. Không thêm field vào shopping list/item cũ.
- **Việc làm:** định nghĩa replay scope `(user_id, method, route có resource id, key)`, fingerprint body chuẩn hóa và response status/body. Thêm lưu trữ nhỏ cho shopping mutation nếu không có cơ chế persistence dùng lại được; code hiện tại chưa có replay store cho add/remove. Không đặt state replay vào inventory ledger rồi sửa ledger.
- **File đề xuất:** `model/shopping_mutation_receipt_model.py`, `model/__init__.py`, một migration mới nối head hiện tại, `test/test_planning_schema.py`.
- **Phụ thuộc:** T01; chốt semantics cùng key/khác payload → 409; TTL/giữ lịch sử phải được tài liệu hóa trước khi chọn cleanup.
- **Nghiệm thu:** [ ] constraint unique chống race theo scope; [ ] migration chỉ bổ sung, upgrade không mất list/item/ledger cũ; [ ] chưa có cleanup job hoặc xóa receipt tự động ngoài yêu cầu.
- **Kiểm chứng:** migration trên DB test có dữ liệu và test uniqueness; không sửa các revision cũ.

#### T08b — P1/M: dùng replay trong shopping service

- **Database:** thực hiện quy trình transaction/fingerprint/replay mục 5.8.3; nghiệm thu DB-V03/04/05/06, kiểm tra lookup receipt trước lookup item đã bị xóa.
- **Việc làm:** nối receipt và business write trong cùng transaction cho generate/add/update/remove; giữ rule generate trả ACTIVE snapshot theo plan, bổ sung nhận diện replay request. Giữ row lock/item inventory linkage đang chống nhập kho trùng.
- **File:** `module/shopping_lists/shopping_service.py`, thêm helper receipt trong chính module nếu cần, `test/test_shopping_router.py`, thêm `test/test_shopping_idempotency.py`.
- **Phụ thuộc:** T08a; làm sau T05/T06 nếu cùng sửa shopping_service để tránh diff chồng lấn.
- **Nghiệm thu:** [ ] retry add không tạo item thứ hai, retry DELETE cùng key trả lại 204; [ ] cùng key/scope khác body → 409, user/key khác tách biệt; [ ] hai request đồng thời commit tối đa một mutation/receipt, rollback không lưu thành công giả.
- **Kiểm chứng:** integration concurrent requests trên DB test; route fake đơn thuần không đủ chứng minh transaction/replay.

#### T09 — P1/M, DECISION: vòng đời item khi nấu

- **Database:** không migration field; áp dụng lock order và kiểm tra dữ liệu cũ mục 5.8.6, nghiệm thu DB-V11. Giữ các session hiện hữu, không thêm unique item/session rồi xóa bản ghi trùng để ép constraint.
- **Việc làm:** chốt một item/một lần nấu; lock và kiểm tra item trong completion, update COMPLETED cùng transaction; chặn duplicate completion qua session khác và sửa/xóa item đã tham chiếu session bằng 409. Giữ FK và session snapshot.
- **File:** `module/cooking/cooking_service.py`, `module/meal_plans/meal_plan_service.py`, `test/test_cooking_completion_service.py`, `test/test_meal_plan_router.py`, thêm test DB nếu chưa có.
- **Phụ thuộc:** T01, T04; chỉ triển khai sau khi quy tắc mục 5.5 được chốt. Không tự backfill trạng thái hàng loạt từ tên plan hoặc giả định mọi session là lần nấu hợp lệ duy nhất.
- **Nghiệm thu:** [ ] completion ghi item/session/batch/ledger atomically; [ ] same-key retry trả kết quả cũ, session khác không trừ kho lần hai cho item completed; [ ] GET plan phản ánh trạng thái, generate mới bỏ completed item, ACTIVE list cũ giữ snapshot đã công bố.
- **Kiểm chứng:** integration cạnh tranh hai session cùng item, lỗi giữa transaction, item đã đổi recipe/servings, item của user khác. Chạy cooking + meal-plan + shopping regression.

#### T10 — P1/S: fixture barcode không tìm thấy

- **Việc làm:** duy trì mock; thêm một barcode fixture không tìm thấy được tài liệu hóa, giữ dữ liệu mock thành công hiện tại cho luồng demo. Đề xuất not-found trả 200, status=FAILED, barcode giữ giá trị input, các product field null, warnings có thông báo; không giả rằng tất cả fields rỗng vì barcode bắt buộc trong DTO.
- **File:** `module/extractions/extraction_provider.py`, `test/test_extractions.py`, contract phần ví dụ.
- **Phụ thuộc:** T01/T02; FE/BE chốt status FAILED thay vì PARTIAL trước khi publish ví dụ.
- **Nghiệm thu:** [ ] success/not-found deterministic, không gọi dịch vụ thật; [ ] query barcode và persisted=false giữ nguyên; [ ] FE nhận 200 not-found không crash và không tự lưu kho.
- **Kiểm chứng:** test hai fixture và thiếu query → 422; kiểm tra multipart không thay thế được query.

**Checkpoint B2:** retry không nhân bản dữ liệu shopping; mọi thay đổi cooking đã có quyết định nghiệp vụ và test transaction. Recommendation/extraction vẫn mock. T09 hoặc nhánh direct-cook chưa được chọn phải ghi rõ deferred, không gộp vào tuyên bố hoàn thành.

### Nhóm C — endpoint mới không chặn MVP

#### T11 — P2/S: chốt metric và contract Reports

- **Việc làm:** chốt eligibility, period, weekly_series/labels, timezone, làm tròn, top limit, coverage của dữ liệu lịch sử theo mục 5.6.
- **File:** `docs/api-contract.md`, file này ở phần quyết định, ADR/tài liệu metric ngắn nếu cần lưu quyết định lâu dài.
- **Phụ thuộc:** không chặn nhóm A/B; phải xong trước T12/T13.
- **Nghiệm thu:** [ ] có ví dụ tính tay cho GRAM/KG, expiry, biên tuần/tháng/năm; [ ] phân biệt dùng thực phẩm và ước tính tránh lãng phí, không tính kép leftover; [ ] FE chấp nhận hình dạng series và metadata coverage.
- **Kiểm chứng:** review bộ dữ liệu mẫu có expected totals, bao gồm không dữ liệu và không đổi được đơn vị. Đây là quyết định sản phẩm, không suy ra chỉ từ tên endpoint.

#### T12a — P2/M: thêm bảng evidence báo cáo

- **Database:** thực hiện DB-02 theo mục 5.8.4/5.8.7, nghiệm thu DB-V01/02. Các tên field cụ thể dùng schema mục 5.8.4, bao gồm identity/name/batch-type snapshot để group và giữ nghĩa lịch sử.
- **Việc làm:** thêm model/bảng waste_reduction_events và constraints/FK ở mục 5.6, index theo user/thời điểm để query kỳ; không cập nhật ledger cũ.
- **File:** `model/waste_reduction_event_model.py`, `model/__init__.py`, migration mới, thêm `test/test_report_schema.py`.
- **Phụ thuộc:** T11; migration nối head sau T08a nếu T08a đã merge.
- **Nghiệm thu:** [ ] một event tối đa một ledger entry; [ ] dữ liệu cũ và trigger immutable nguyên vẹn; [ ] event lưu đủ evidence để sửa expires_at của batch sau này không đổi số đã ghi.
- **Kiểm chứng:** upgrade DB test có ledger cũ, thử duplicate event, xác nhận FK/user consistency ở tầng ghi event.

#### T12b — P2/M: ghi evidence cùng transaction nấu

- **Database:** thực hiện writer và coverage mục 5.8.4, nghiệm thu DB-V07/08. Lấy ledger từ return value hiện có của apply_quantity_change; flush để có ID, không commit riêng cho event.
- **Việc làm:** lấy ledger mới tạo và snapshot batch trước deduction để ghi kết quả xét điều kiện cùng lý do loại nếu có; không tạo transaction riêng hoặc network call. Chỉ tách helper nhỏ khi cần tránh làm phình cooking_helper.
- **File:** `module/cooking/cooking_helper.py`, module `reports` helper/service nhỏ, `test/test_cooking_completion_service.py`, thêm `test/test_report_events.py`. Tái sử dụng `module/inventory/inventory_service.py` vì hàm hiện tại đã trả ledger; chưa cần sửa file này chỉ để ghi snapshot.
- **Phụ thuộc:** T12a, quyết định metric T11; chạy lại khi T09 thay completion.
- **Nghiệm thu:** [ ] kg và eligibility đúng tại lúc complete; [ ] rollback cooking không để event, replay không thêm event; [ ] UNKNOWN/expired/cooked leftover/không đổi được kg không bị tính sai.
- **Kiểm chứng:** test fixture thời gian cố định và transaction thật, sửa expires_at sau nấu rồi kiểm tra event không đổi. Không backfill lịch sử thiếu bằng chứng.

#### T13 — P2/M: triển khai GET reports/waste-reduction

- **Database:** query theo user/consumed_at/metric_version và coverage ở 5.8.4, nghiệm thu DB-V08/09. Không migrate bảng aggregate hoặc lấy expires_at hiện tại để suy ra lịch sử.
- **Việc làm:** module `reports` với DTO/query/service/router/dependency theo pattern BE; đăng ký vào app.py và aggregate evidence theo user/kỳ.
- **Chia commit:** (1) `report_dto.py`, `report_service.py`, `test/test_report_service.py`; (2) `report_router.py`, `report_dependency.py`, `app.py`, `test/test_report_router.py`. Không làm một commit gom schema, migrations và UI.
- **Phụ thuộc:** T11/T12a/T12b.
- **Nghiệm thu:** [ ] 200 đúng 4 field M7 + metadata đã chốt, 422 period sai, 401 thiếu auth; [ ] tổng/series/top đúng fixture và ranh thời gian, không lộ user khác; [ ] lịch sử thiếu evidence hiển thị coverage, không trả số liệu mock như dữ liệu thật.
- **Kiểm chứng:** service aggregate trên DB test, query calendar bounds, tổng trước rounding; FE đổi riêng repository Reports từ mock sang API sau nghiệm thu.

#### T14 — P2/M: lưu đăng ký quan tâm premium

- **Database:** thực hiện DB-03 theo mục 5.8.5/5.8.7, nghiệm thu DB-V01/02/10. UserModel và preferences giữ schema cũ; không backfill interest cho mọi user.
- **Việc làm:** bảng premium_interests theo mục 5.7; upsert/do-nothing khi đã có user, ghi lần đầu cùng transaction.
- **File:** `model/premium_interest_model.py`, `model/__init__.py`, migration mới, `module/subscription/subscription_service.py`, thêm `test/test_subscription_service.py`.
- **Phụ thuộc:** T01 chốt body/status; migration nối head hiện tại, không chạy song song tạo nhiều head chưa xử lý.
- **Nghiệm thu:** [ ] hai request đồng thời vẫn một row và first registered_at; [ ] PATCH preferences không xóa trạng thái quan tâm; [ ] không thay plan/role hoặc cấp premium.
- **Kiểm chứng:** service/database test retry, user isolation và rollback.

#### T15 — P2/M: công bố hai route Subscription

- **Việc làm:** DTO/router/dependency, đăng ký vào app.py; GET free/null, POST no-business-body trả registered=true sau persistence.
- **File:** `module/subscription/subscription_dto.py`, `subscription_router.py`, `subscription_dependency.py`, `app.py`, thêm `test/test_subscription_router.py`.
- **Phụ thuộc:** T14.
- **Nghiệm thu:** [ ] hai route Bearer, body/status đúng mục 5.7; [ ] lỗi lưu không trả thành công giả; [ ] toàn bộ tính năng MVP vẫn mở và không có payment/gating.
- **Kiểm chứng:** route tests 200/401/error/retry, E2E đăng ký rồi đăng nhập trên thiết bị khác, kiểm tra record vẫn có. FE bỏ mock Subscription riêng sau khi backend sẵn sàng.

**Checkpoint C:** Reports/Subscription có contract và test thật trước khi FE bỏ mock; không thay recommendation mock thành AI thật trong bất kỳ task nào.

### Dependency và thứ tự triển khai

```text
T01 → T02, T03, T04, T05, T06, T07, T10
T05/T06 → T08a → T08b       (thứ tự tích hợp shopping_service)
T04 + quyết định cooking → T09
T11 → T12a → T12b → T13
T14 → T15                  (không phụ thuộc Reports)
```

T05/T06 không phải dependency dữ liệu của receipt model, nhưng nên merge trước T08b vì cùng sửa shopping service. Migrations T08a/T12a/T14 phải nối tuần tự theo Alembic head thực tế. Việc triển khai có thể chia các phần độc lập cho nhiều người, nhưng kế hoạch này không yêu cầu viết lại kiến trúc hoặc tự động triển khai tất cả nhánh tùy chọn.

## 7. Bảo toàn BE, migration, rủi ro và kiểm thử

### 7.1 Ranh giới thay đổi

- Giữ 77 operation hiện hữu; không xóa Auth/User/Favorites/health/push test vì FE không liệt kê chúng. Giữ DELETE nghiệp vụ hiện có theo điều kiện của chúng; yêu cầu “không xóa trắng BE” không đồng nghĩa cấm tính năng xóa item/favorite của người dùng.
- Không DROP/TRUNCATE bảng, không chạy reset database/reseed xóa dữ liệu, không rewrite baseline migration. Chỉ thêm bảng/cột nullable/default/index thật sự phục vụ task đã chọn.
- Giữ batch model, immutable ledger, ownership, FEFO, enum, header audit và transaction nhập/trừ kho. Không thay bằng CRUD pantry phẳng hoặc xóa ledger để cập nhật số dư.
- Không đổi Decimal response toàn hệ thống thành float. FE parse number/string cho Decimal và xử lý null; không dùng số 0 để thay dữ liệu nutrition chưa biết.
- Thêm field response không đồng nghĩa mọi client đều chịu được: kiểm tra decoder FE; fallback summary khi rollout, không đổi envelope list đang có.
- Rollback ứng dụng về bản cũ và giữ bảng/cột mới thường đủ; không downgrade xóa evidence/interest/receipt đã ghi. Nếu migration thất bại, sửa bằng revision tiếp theo trên dữ liệu còn nguyên.

### 7.2 Rủi ro cần ghi vào implementation issue

| Rủi ro | Mức | Cách xử lý |
|---|---|---|
| 200→201 device làm client kiểm tra status cũ thất bại | Cao | Chuyển client nhận cả hai trước; giữ body, ghi version triển khai |
| Default storage thiếu hoặc khác lựa chọn người dùng | Cao | Explicit luôn thắng; default-null/custom phải nhập storage; không fallback tùy tiện |
| Chỉ test router fake mà kết luận idempotency/atomicity đã đúng | Cao | Test service và DB cạnh tranh, đếm item/batch/ledger/receipt |
| Item “ẩn” tham gia plan/shopping, trùng slot hoặc báo trạng thái sai | Cao | Dùng plan thật; quyết định T09/direct-cook tách riêng; không tạo ngầm bằng tên đặc biệt |
| Báo cáo nhìn expires_at hiện tại rồi suy lịch sử | Cao | Evidence lúc dùng, coverage lịch sử chưa đủ; không sửa ledger cũ |
| Thêm ảnh/time nhưng vẫn thiếu nutrition nên N+1 card còn nguyên | Trung bình | Summary có nutrition/default_servings theo mục 5.3; detail chỉ tải khi mở món |
| Generate list cũ bị FE hiểu là đã refresh | Trung bình | Ghi rõ snapshot; không thay/xóa generated items và liên kết batch mua sắm trong đợt này |
| Leftovers gọi lặp tạo nhiều batch nhưng history detail dùng scalar_one_or_none | Cao, phát hiện liên quan ngoài gap M7 trực tiếp | Tạo issue riêng: chốt một/nhiều leftover mỗi session, optional key/guard hoặc response collection additive; không xóa batch cũ để tránh lỗi |
| Leftover expires_at không có validator timezone riêng như inventory DTO | Trung bình, ngoài thay đổi bắt buộc | FE gửi timezone; issue validation có test nếu siết request, không tuyên bố BE hiện đã chặn mọi datetime naive ở mọi route |
| Catalog detail mới load rules của ingredient, enum CATEGORY dễ bị hiểu là đã fallback category | Trung bình | Document phạm vi thực tế; thêm fallback chỉ khi FE cần rule category có sẵn, không dựng rule giả |
| Public push-test khác quy ước “mọi route trừ Auth cần Bearer” | Trung bình | Ghi đúng hiện trạng/phạm vi test; thay quyền hoặc hạn chế môi trường là task riêng, không xóa route trong gap plan |

Các issue liên quan ngoài M7 trên cần giữ trong backlog, không mặc định mở rộng lần lập kế hoạch thành sửa mọi lỗi BE.

### 7.3 Chiến lược kiểm thử khi triển khai

Chạy từ `src/backend`, dùng `.venv/bin/python` sẵn có hoặc `uv run python` trong môi trường dự án đã chuẩn bị. Không coi DB integration bị skip là đã kiểm chứng DB.

```bash
# Nhóm hợp đồng/route liên quan
.venv/bin/python -m pytest -q src/test/test_extractions.py src/test/test_notification_router.py src/test/test_recommendation_router.py src/test/test_recommendation_provider.py src/test/test_meal_plan_router.py src/test/test_shopping_router.py

# Hồi quy kho/nấu và các API cần giữ
.venv/bin/python -m pytest -q src/test/test_inventory_router.py src/test/test_inventory_service.py src/test/test_cooking_router.py src/test/test_cooking_completion_service.py src/test/test_cooking_leftover_history_router.py src/test/test_auth_router.py src/test/test_user_router.py src/test/test_favorite_router.py

# Kiểm tra migration trước/sau nâng cấp trong DB TEST riêng
.venv/bin/python -m alembic heads
.venv/bin/python -m alembic current
```

Migration upgrade và test DB chỉ chạy trên database test biệt lập theo [conftest.py](../../src/backend/src/test/conftest.py); fixture yêu cầu TEST_DATABASE_URL và có guard khác database ứng dụng. **Alembic CLI vẫn đọc DATABASE_URL từ env.py**, nên phải dùng quy trình subprocess có guard ở mục 5.8.8 để chuyển target sang DB test; không coi TEST_DATABASE_URL là override tự động của Alembic. Cấu hình đó phải có trước test migration/concurrency. Dùng migration đầy đủ, không create/drop toàn schema để thay việc kiểm chứng nâng cấp.

Các test mới được đặt tên ở T06/T08/T11–T15 là **file dự kiến**, không phải test đã tồn tại. Khi viết xong, thêm chúng vào lệnh kiểm chứng cho từng task. Quality checks dùng tooling sẵn trong [pyproject.toml](../../src/backend/pyproject.toml), giới hạn file đã thay đổi trước; không sửa format toàn repo ngoài phạm vi.

Luồng E2E bắt buộc:

1. Login → tạo/đọc plan → xem mock recommendations đủ card → thêm item với recommendation_run_id null → generate list.
2. Xóa local list_id ở client → gọi GET shopping-lists ACTIVE → GET detail → thấy đúng list user đó.
3. Tick generated/manual với metadata tường minh hoặc catalog default → một batch + một ledger; retry cùng key không nhân đôi; uncheck không xóa stock.
4. Preview → create session → complete → stock/ledger/history đúng; thay đổi vòng đời item được kiểm tra theo quyết định T09. Tranh chấp stock → 409, không trừ kho một phần.
5. Upload MIME sai → FE đọc envelope lỗi chung; barcode miss → trạng thái không tìm thấy không bị coi là lỗi HTTP 404; không có extraction tự ghi kho.
6. Reports không dữ liệu/dữ liệu trước coverage/dữ liệu đủ evidence đều hiển thị đúng; interest premium không khóa hoặc mở thêm tính năng.

## 8. API BE hiện có ngoài phần mô tả chi tiết của M7 — giữ lại

### 8.1 Auth — 11 operation, không viết lại

| Endpoint | Request / auth | Response hiện tại |
|---|---|---|
| `POST /auth/register` | Public; phone E.164, password 8–128, name?, email? | 200 `{otp,expires_in_seconds}` |
| `POST /auth/register/resend-otp` | Public; `{phone}` | 200 OTP DTO |
| `POST /auth/verify/register` | Public; `{phone,otp}` | 200 plain text |
| `POST /auth/password/reset` | Public; `{phone}` | 200 OTP DTO |
| `POST /auth/password/change` | Bearer; không body nghiệp vụ | 200 OTP DTO |
| `POST /auth/verify/change-password` | Public ở route; `{phone,otp,purpose,new_password}`; purpose RESET_PASSWORD/CHANGE_PASSWORD | 200 `{message}`; OTP được service xác thực |
| `POST /auth/login` | Public; `{phone,password}` | 200 access_token, refresh_token, token_type, access/refresh_expires_in_seconds, session_id |
| `POST /auth/token/refresh` | Public; `{refresh_token}` | 200 access_token, token_type, access_expires_in_seconds; không trả refresh token mới |
| `POST /auth/logout` | Bearer; `{refresh_token}` | 200 plain text |
| `GET /auth/sessions` | Bearer | 200 array `{id,ip_address,user_agent,expires_at,created_at,last_used_at}` |
| `DELETE /auth/sessions/{id}` | Bearer, ownership | 204 |

OTP response chứa mã OTP là hiện trạng MVP trong code, không tự loại field khi bổ sung contract. Bất kỳ thay đổi bảo mật auth nào cần phạm vi và kế hoạch tương thích riêng.

### 8.2 User — 7 operation, không viết lại

| Endpoint | Request | Response hiện tại — đều Bearer |
|---|---|---|
| `GET /users/me` | Không body | 200 `{user_id,roles}`; không phải profile đầy đủ |
| `GET /users/profile` | Không body | 200 user_id/name/phone/phone_verified_at/email/email_verified_at/preferences |
| `PATCH /users/profile` | `{name?,preferences?}` | 200 profile; preferences được replace khi gửi, không deep-merge |
| `POST /users/me/email/request-verification` | `{email}` | 200 `{otp,expires_in_seconds}` |
| `POST /users/me/email/verify` | `{otp}`; destination lấy từ yêu cầu trước | 200 plain text |
| `POST /users/me/phone/request-change` | `{phone}` E.164 | 200 OTP DTO |
| `POST /users/me/phone/confirm-change` | `{otp}` | 200 plain text |

### 8.3 Favorites — 11 operation, không viết trùng

| Endpoint | Request | Response hiện tại — đều Bearer |
|---|---|---|
| `PUT /recipes/{id}/favorite` | Không body nghiệp vụ | 200 `{recipe_id,is_favorite}` |
| `DELETE /recipes/{id}/favorite` | Không body | **200 `{message}`** theo router/service hiện tại; không tự đổi thành 204 |
| `GET /favorite-recipes` | limit=20, offset=0, max 100 | 200 `{items,total,limit,offset}`; item recipe_id/name/description/media_url/created_at |
| `POST /favorite-menus` | `{name,description?}` | 201 `{id,name,description,created_at,updated_at}` |
| `GET /favorite-menus` | limit/offset | 200 `{items,total,limit,offset}` |
| `GET /favorite-menus/{id}` | UUID | 200 menu + items |
| `PATCH /favorite-menus/{id}` | `{name?,description?}` | 200 menu |
| `DELETE /favorite-menus/{id}` | UUID | Route khai báo 204; service có trả message nhưng không coi message là body FE được bảo đảm |
| `POST /favorite-menus/{id}/items` | `{recipe_id}` | 201 `{id,recipe_id,recipe_name,recipe_description,media_url,created_at}` |
| `PATCH /favorite-menus/{id}/items/{item_id}` | `{recipe_id}` | 200 item; thay recipe giữ item id |
| `DELETE /favorite-menus/{id}/items/{item_id}` | UUID | 204 |

### 8.4 Health và push test — 8 operation, giữ phạm vi hiện tại

`GET /health/liveness`, `GET /health/error` (cố ý phát sinh lỗi), `GET /health/text`, `GET /health/test-login` (Bearer), `GET /health/test-role` (ADMIN qua role dependency), `POST /health/test-email` (202), `POST /send-notification`, `POST /send-web-notification` (200 `{message_id}`). Hai route push nhận `{device_token,title,body,data?}`, hiện public và dùng cho kiểm thử tích hợp Firebase. Đây không phải API inbox cho FE; không gọi gửi email/push thật để lập báo cáo gap.

## 9. Những quyết định còn mở và mặc định để lập kế hoạch

| Quyết định | Mặc định đề xuất | Chặn task nào |
|---|---|---|
| Device phải 201 hay chấp nhận 200 hiện tại? | Theo M7 chuyển 201 sau FE nhận cả hai; giữ body | T03 rollout |
| FE dùng plan thật hay muốn nấu ngoài kế hoạch? | Giữ plan thật theo PRD; không có hidden semantics | Nhánh P3 direct-cook, không chặn T02/T05/T07 |
| Một meal-plan item có đúng một lần nấu? | Đề xuất có; completed không chỉnh sửa bằng API kế hoạch | T09 |
| Default storage ở BE hay chỉ prefill FE? | Đề xuất BE fallback catalog, purchase vẫn required | T06 |
| “Saved kg” và chart period tính thế nào? | Ước tính dùng nguyên liệu sắp hết hạn, evidence tại lúc dùng, kỳ lịch/tuần có labels | T11–T13; FE Reports vẫn mock |
| Unknown barcode trả status gì bên trong 200? | FAILED, barcode giữ nguyên, product fields null, warning rõ | T10 |
| Receipt idempotency giữ bao lâu? | Không tự cleanup trong đợt đầu; công bố phạm vi replay trước rollout | T08a/T08b |

Các mục này là quyết định cho lúc triển khai, không làm dừng việc lập bản gap và kế hoạch. Không đưa giả định chưa chốt thành mô tả “BE hiện đang hỗ trợ”.

## 10. Checklist bàn giao và kết quả kiểm chứng của lần phân tích

- [x] Đọc toàn bộ contract M7 hiện tại, gồm phần ghi chú FE và yêu cầu giữ mock recommendation.
- [x] Kiểm kê 77 operation từ router trong module; OpenAPI của app cũng có 77 operation.
- [x] Đối chiếu request/response, status, auth, header, validation, service và model liên quan.
- [x] Phân biệt GIỮ/DOC/REQ/RES/LOGIC/NEW/DECISION; chỉ ra 4 endpoint cần viết thêm trong phương án chính.
- [x] Lập task có phụ thuộc, file dự kiến, tiêu chí nghiệm thu, cách kiểm chứng và checkpoint.
- [x] Ghi rõ bảo toàn BE/dữ liệu, migration bổ sung và rollout tương thích.
- [x] Bổ sung đặc tả database mục 5.8: ma trận API/model, field/type/null/default/FK/constraint/index của ba bảng mới, luồng ghi/đọc và 12 case nghiệm thu DB; nối tham chiếu vào các task tương ứng.
- [ ] Thực hiện các task BE/FE: **chưa thuộc lần làm việc này**.

Kiểm chứng trực tiếp đã thực hiện bằng import app/DTO, không chạy lifespan hoặc kết nối DB: OpenAPI xác nhận device success 200, barcode là query param, meal-plan list limit/offset, thiếu 4 route NEW; DTO từ chối checked=true thiếu purchase; inventory PATCH yêu cầu reason; summary có hai field đếm expiry; barcode mock với `unknown-barcode` vẫn trả SUCCEEDED/Whole Milk. Những kết quả này nhất quán với các nguồn code trong mục 2.

Bộ pytest route nhiều module đã được thử nhưng dừng do không tiến triển sau phần catalog; trước khi dừng thấy 4 test skip và 1 test đi qua. Không có kết luận bộ test này pass, không quy nguyên nhân treo cho code hoặc hạ tầng khi chưa điều tra.

**Kiểm tra chọn lọc hoàn tất: 5 passed trong 1,00 giây.** Gồm bốn test OpenAPI: catalog/recipe, recommendation, meal plan, shopping; và test service mock recommendation giữ recipe ID/ranking. Lệnh đã chạy (timeout 25 giây bên ngoài để giới hạn thời gian):

```bash
.venv/bin/python -m pytest -q src/test/test_catalog_recipe_api.py::test_catalog_recipe_openapi_documents_queries_schemas_and_read_only_methods src/test/test_recommendation_router.py::test_recommendation_openapi_documents_the_authenticated_request_contract src/test/test_meal_plan_router.py::test_meal_plan_openapi_documents_protected_routes src/test/test_shopping_router.py::test_shopping_openapi_documents_idempotent_mutations src/test/test_recommendation_provider.py -o faulthandler_timeout=15
```

Các test trên xác nhận phần contract hiện hữu được chọn, **không chứng minh toàn bộ BE hoặc các thay đổi đề xuất đã pass**. Liên kết tương đối trong kế hoạch đã kiểm tra không trỏ tới file bị thiếu. Lần phân tích này không chạy migration, không sửa service, không gửi email/push và không sửa file contract đầu vào đang có thay đổi của người dùng.
