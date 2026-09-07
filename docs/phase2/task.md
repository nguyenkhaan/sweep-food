# Phase 2 — Danh sách Phase và Task triển khai Backend

> Nguồn duy nhất của phạm vi: [plan.md](./plan.md) và [api-contract.md](../api-contract.md).
> Tài liệu này chia nhỏ kế hoạch thành các đơn vị triển khai; không thay đổi quyết định kỹ thuật trong `plan.md`.
> Trạng thái ban đầu: tất cả task chưa thực hiện.

## 1. Nguyên tắc thực hiện

- Giữ toàn bộ API, module, bảng và dữ liệu BE hiện có. Không DROP/TRUNCATE hoặc reset database để áp dụng Phase 2. Ngoại lệ duy nhất là Task 0.2: xóa **file migration cũ** trong source, không xóa schema hoặc dữ liệu của database.
- Các thay đổi chính không thêm hoặc xóa field trong bảng hiện hữu. Chỉ thêm ba bảng khi task tương ứng được triển khai: `shopping_mutation_receipts`, `waste_reduction_events`, `premium_interests`.
- Giữ InventoryBatchModel, immutable inventory ledger, FEFO, ownership, transaction và các enum hiện tại.
- Recommendation và Extractions tiếp tục dùng mock. Không tích hợp LLM, OCR/ASR provider thật hoặc payment provider trong Phase 2.
- Reports và Subscription là P2. FE tiếp tục dùng mock đến khi endpoint BE và kiểm thử của Phase tương ứng hoàn thành.
- Task 0.2 xóa toàn bộ script cũ trong `src/backend/alembic/versions/`. Người phụ trách sẽ tự tạo migration mới và tự chạy `alembic upgrade head`; các task không chạy hai lệnh này. Sau đó, migration mới ở các Phase sau phải nối tiếp Alembic head thực tế và không sửa migration đã được tạo.
- Phase 0 không chỉnh sửa `docs/api-contract.md`; file này chỉ được dùng làm tài liệu tham chiếu khi cần.
- Mỗi task chỉ được đánh dấu hoàn thành khi acceptance criteria và verification của chính task đã đạt.

## 2. Thứ tự Phase

```text
Phase 0: Cập nhật model, migration source và seed data
    ↓
Phase 1: Sửa các mismatch P0 của API hiện có
    ↓
Phase 2: Hoàn thiện các response/read flow phục vụ FE
    ↓
Phase 3: Thêm persistence idempotency cho Shopping Lists
    ↓
Phase 4: Hoàn thiện vòng đời Meal Plan Item khi nấu
    ↓
Phase 5: Thêm Reports và dữ liệu evidence
    ↓
Phase 6: Thêm Subscription/Premium Interest
    ↓
Phase 7: Migration, regression và E2E tổng thể

Phase 8: Direct cooking — chỉ thực hiện nếu quyết định sản phẩm thay đổi
```

Phase 5 và Phase 6 độc lập về nghiệp vụ nhưng migration phải được tạo tuần tự theo head đã merge. Phase 8 là nhánh có điều kiện, không nằm trong phạm vi mặc định.

### Đối chiếu task gốc trong plan.md

| Task gốc | Task triển khai trong file này |
|---|---|
| T01 | Không thực hiện trong Phase 0 (giữ nguyên `docs/api-contract.md`) |
| T02 | 1.1 |
| T03 | 1.2 |
| T04 | 1.3 |
| T05 | 2.1, 2.2 |
| T06 | 2.3 |
| T07 | 2.4, 2.5 |
| T08a | 3.1, 3.2, 3.3 |
| T08b | 3.4, 3.5 |
| T09 | 4.1, 4.2, 4.3, 4.4 |
| T10 | 2.6 |
| T11 | 5.1 |
| T12a | 5.2, 5.3 |
| T12b | 5.4, 5.5 |
| T13 | 5.6, 5.7 |
| T14 | 6.1, 6.2, 6.3 |
| T15 | 6.4 |
| Kiểm thử/migration/E2E mục 7 của plan | 7.1–7.4 |
| Nhánh P3 direct cooking mục 5.5 của plan | 8.1–8.2, chỉ thực hiện khi được quyết định |

---

## Phase 0 — Cập nhật model, migration source và seed data

### Task 0.1 — Chỉnh sửa SQLAlchemy model theo schema Phase 2

**Mục tiêu:** cập nhật các file model để phản ánh schema Phase 2 đã chốt trước khi tạo migration mới và cập nhật seed data.

**Các bước:**

1. Rà `plan.md` và các model liên quan để xác định field, enum, FK, relationship, constraint và index cần có trong schema mục tiêu.
2. Chỉnh các file SQLAlchemy model và đăng ký model/import liên quan theo schema mục tiêu; giữ các bất biến Inventory ledger, FEFO, ownership và transaction đã có.
3. Đồng bộ metadata ORM cần cho autogenerate migration, gồm `nullable`, default, unique/index và tên FK/constraint khi có thay đổi.
4. Không chỉnh sửa route, DTO, service hoặc `docs/api-contract.md` trong task này.
5. Không chạy `alembic revision --autogenerate` hoặc `alembic upgrade head`; hai thao tác này do người phụ trách thực hiện sau khi model được duyệt.

**Acceptance criteria:**

- [ ] Model ORM phản ánh đầy đủ schema Phase 2 đã chốt, với FK, enum, relationship, constraint và index nhất quán.
- [ ] Metadata có thể dùng làm đầu vào để người phụ trách sinh migration mới mà không cần sửa tay model.
- [ ] Không thay đổi API contract, route, DTO hoặc dữ liệu database.

**Verification:**

- [ ] Kiểm tra import/metadata của model và các test schema/model liên quan.
- [ ] Chạy các kiểm tra tĩnh hoặc test đơn vị không yêu cầu migration database.
- [ ] Người phụ trách review diff model trước khi tự sinh migration mới.

**Dependencies:** Không có.

**Files liên quan:** `src/backend/src/model/**/*.py`, `src/backend/src/model/__init__.py`, các test model/schema tương ứng.

**Estimated scope:** M — chỉ model và đăng ký metadata liên quan.

### Task 0.2 — Dọn migration cũ và cập nhật seed data

**Mục tiêu:** chuẩn bị source cho migration mới do người phụ trách sinh và bảo đảm seed data phù hợp với model đã cập nhật.

**Các bước:**

1. Xóa toàn bộ file migration cũ trong `src/backend/alembic/versions/`; giữ nguyên `alembic/env.py`, cấu hình Alembic và thư mục versions.
2. Không tự sinh migration và không chạy `alembic upgrade head`. Người phụ trách sẽ tự thực hiện hai bước này sau khi nhận thay đổi model.
3. Cập nhật file seed data/factory/fixture dùng chung để khớp field bắt buộc, enum, relationship và constraint của model mới.
4. Giữ seed có tính xác định, không ghi credential hoặc dữ liệu nhạy cảm, và không đưa logic API vào seed.
5. Không chỉnh sửa `docs/api-contract.md`.

**Acceptance criteria:**

- [ ] Không còn file migration cũ trong `src/backend/alembic/versions/`; schema và dữ liệu database hiện hữu không bị xóa.
- [ ] Seed data tạo được dữ liệu hợp lệ theo model mới sau khi người phụ trách đã tự sinh và áp dụng migration mới.
- [ ] Không có lệnh `alembic revision --autogenerate` hoặc `alembic upgrade head` được chạy trong task.
- [ ] `docs/api-contract.md` không thay đổi.

**Verification:**

- [ ] Kiểm tra `src/backend/alembic/versions/` chỉ còn cấu trúc thư mục, không còn script migration cũ.
- [ ] Kiểm tra seed/factory/fixture khởi tạo đủ các field bắt buộc của model mới.
- [ ] Sau khi người phụ trách hoàn tất migration và `upgrade head`, người phụ trách chạy seed trên database test biệt lập.

**Dependencies:** Task 0.1.

**Files likely touched:** `src/backend/alembic/versions/*.py` (xóa), các file seed/factory/fixture đang dùng trong backend.

**Estimated scope:** M — dọn migration source và đồng bộ seed data.

### Checkpoint Phase 0

- [ ] Model ORM đã được cập nhật và sẵn sàng để sinh migration mới.
- [ ] Toàn bộ migration script cũ đã được xóa; người phụ trách đã nhận bàn giao để tự sinh migration và chạy upgrade.
- [ ] Seed data phù hợp model mới; `docs/api-contract.md` không bị chỉnh sửa trong Phase 0.

---

## Phase 1 — Sửa mismatch P0 của API hiện có

### Task 1.1 — Chuẩn hóa error envelope cho OCR/ASR

**Mục tiêu:** mọi lỗi upload/validation của extraction trả envelope `{status_code, detail, path}`.

**Các bước:**

1. Thay ba nhánh `JSONResponse({detail})` của label OCR, invoice OCR và ASR bằng cơ chế lỗi chung trong `core/exceptions.py`.
2. Giữ status 422 và detail hiện hữu; không thay success response, multipart input, provider mock hoặc `persisted=false`.
3. Bổ sung khai báo response lỗi trong OpenAPI nếu codegen hiện chưa nhìn thấy schema chung.
4. Bổ sung test thiếu file, MIME sai và vượt kích thước cho đủ ba field envelope.

**Acceptance criteria:**

- [ ] Mọi lỗi 422 của ba route có `status_code`, `detail`, `path` chính xác.
- [ ] Success contract và mock data không đổi.
- [ ] Nội dung file hoặc dữ liệu nhạy cảm không xuất hiện trong lỗi.

**Verification:**

- [ ] Chạy `.venv/bin/python -m pytest -q src/test/test_extractions.py`.
- [ ] Kiểm tra OpenAPI của ba route extraction.

**Dependencies:** Task 0.1.

**Files likely touched:** `src/backend/src/module/extractions/extraction_route.py`, `src/backend/src/test/test_extractions.py`.

**Estimated scope:** S — hai file.

### Task 1.2 — Đồng bộ HTTP status đăng ký device

**Mục tiêu:** đưa `POST /users/me/devices` về status 201 theo contract sau khi client đã tương thích.

**Các bước:**

1. Xác nhận FE đã chấp nhận cả 200 và 201 trong giai đoạn chuyển đổi.
2. Thêm `status_code=201` vào route đăng ký/upsert device.
3. Giữ nguyên request `{fcm_token, platform}`, response body, logic upsert và DELETE 204.
4. Cập nhật route test và OpenAPI assertion; test đăng ký lại không tạo device trùng.

**Acceptance criteria:**

- [ ] POST trả 201 và response không lộ FCM token.
- [ ] Đăng ký lại cùng token cập nhật record hiện hữu.
- [ ] DELETE device vẫn trả 204 và kiểm tra ownership.

**Verification:**

- [ ] Chạy `.venv/bin/python -m pytest -q src/test/test_notification_router.py src/test/test_notification_service.py`.
- [ ] Kiểm tra OpenAPI chỉ đổi success status của POST device.

**Dependencies:** Task 0.1 và điều kiện FE nhận cả 200/201.

**Files likely touched:** `src/backend/src/module/notification/notification_router.py`, `src/backend/src/test/test_notification_router.py`.

**Estimated scope:** S — hai file.

### Task 1.3 — Cố định response và thứ tự GET meal plans

**Mục tiêu:** công bố schema chính xác và trả danh sách plan theo thứ tự ổn định.

**Các bước:**

1. Khai báo `response_model=list[MealPlanViewDTO]` và return annotation cho `GET /meal-plans/`.
2. Giữ response là array, path có dấu `/` cuối, query `limit/offset` và fields hiện hữu.
3. Thêm `ORDER BY created_at DESC, id DESC` trước `OFFSET/LIMIT`.
4. Bổ sung test nhiều plan, phân trang, ownership và OpenAPI.

**Acceptance criteria:**

- [ ] OpenAPI mô tả đúng array `MealPlanViewDTO`.
- [ ] Hai lần query cùng dữ liệu trả cùng thứ tự và phân trang.
- [ ] User không đọc được plan của user khác.

**Verification:**

- [ ] Chạy `.venv/bin/python -m pytest -q src/test/test_meal_plan_router.py`.
- [ ] Chạy test DB cho order, limit và offset.

**Dependencies:** Task 0.1.

**Files likely touched:** `src/backend/src/module/meal_plans/meal_plan_router.py`, `src/backend/src/module/meal_plans/meal_plan_service.py`, `src/backend/src/test/test_meal_plan_router.py`.

**Estimated scope:** M — ba file.

### Checkpoint Phase 1

- [ ] Extraction lỗi theo envelope chung.
- [ ] Device status được rollout tương thích.
- [ ] Meal-plan list có schema và thứ tự ổn định.
- [ ] Không endpoint hiện hữu nào bị xóa hoặc đổi body ngoài contract.

---

## Phase 2 — Hoàn thiện read/response flow phục vụ FE

### Task 2.1 — Thêm DTO query và response cho danh sách shopping list

**Mục tiêu:** định nghĩa contract nội bộ cho `GET /shopping-lists` trước khi viết query và route.

**Các bước:**

1. Tạo query DTO có `status`, `meal_plan_id`, `limit=20`, `offset=0`; giới hạn limit 1–100 và offset >= 0.
2. Tạo summary DTO gồm `id`, `meal_plan_id`, `status`, `generated_at`, `created_at`, `updated_at`.
3. Tạo list response DTO `{items,total,limit,offset}`.
4. Không thêm field `active_shopping_list_id` vào meal plan và không load items trong summary DTO.

**Acceptance criteria:**

- [ ] DTO chấp nhận filter hợp lệ và từ chối enum/phân trang sai bằng 422.
- [ ] Response DTO đúng shape trong `plan.md` mục 5.1.
- [ ] Không có thay đổi SQLAlchemy model hoặc migration.

**Verification:**

- [ ] Bổ sung unit test schema DTO và OpenAPI expectation dự kiến.

**Dependencies:** Task 0.1.

**Files likely touched:** `src/backend/src/module/shopping_lists/shopping_dto.py`, `src/backend/src/test/test_shopping_router.py`.

**Estimated scope:** S — hai file.

### Task 2.2 — Triển khai service và route GET shopping-lists

**Mục tiêu:** cho FE tìm lại shopping list theo tài khoản sau khi mất local `list_id`.

**Các bước:**

1. Thêm service query theo `user_id`; áp dụng optional status và meal_plan_id.
2. Đếm total trước pagination; sắp xếp `created_at DESC, id DESC`.
3. Thêm route collection `GET /shopping-lists` có Bearer auth, đặt trước/không xung đột route `/{list_id}`.
4. Trả 200 với items rỗng nếu không có list; FE dùng `status=ACTIVE&limit=1` để lấy list mới nhất.
5. Giữ `GET /shopping-lists/{id}` và mọi mutation hiện hữu.

**Acceptance criteria:**

- [ ] Filter status/plan và pagination trả đúng dữ liệu user.
- [ ] Không có list trả collection rỗng; không tiết lộ plan/list user khác.
- [ ] Lấy ID từ collection rồi gọi detail cũ trả đúng items.

**Verification:**

- [ ] Chạy route test với nhiều ACTIVE list, nhiều plan và nhiều user.
- [ ] Chạy boundary test limit 0/101, offset âm, UUID và enum sai.
- [ ] Xác nhận không có migration và index `ix_shopping_lists_user_status` hiện hữu được giữ.

**Dependencies:** Task 2.1.

**Files likely touched:** `src/backend/src/module/shopping_lists/shopping_router.py`, `src/backend/src/module/shopping_lists/shopping_service.py`, `src/backend/src/test/test_shopping_router.py`.

**Estimated scope:** M — ba file.

### Task 2.3 — Cho phép purchase dùng default storage từ catalog

**Mục tiêu:** giữ `purchase` bắt buộc nhưng cho phép bỏ `purchase.storage_mode` khi catalog có default.

**Các bước:**

1. Đổi `ShoppingPurchaseDTO.storage_mode` thành optional; giữ mọi validator timezone/cost/note/media hiện có.
2. Khi check lần đầu, ưu tiên storage_mode tường minh; nếu thiếu thì lấy `MasterIngredientModel.default_storage_mode`.
3. Nếu item là custom hoặc catalog default null, trả 422 yêu cầu storage_mode; không tự chọn REFRIGERATED.
4. Resolve default trước khi tạo InventoryBatchDTO; DB `inventory_batches.storage_mode` vẫn NOT NULL.
5. Giữ check/batch/INITIAL_STOCK/link item trong một transaction; uncheck không hoàn kho, recheck không tạo batch mới.

**Acceptance criteria:**

- [ ] Payload cũ có storage_mode vẫn hoạt động và có ưu tiên cao nhất.
- [ ] `purchase={}` chỉ hoạt động khi master ingredient có default; custom/default-null trả 422 và không ghi dữ liệu.
- [ ] Mỗi item được check chỉ tạo tối đa một batch và một INITIAL_STOCK ledger.

**Verification:**

- [ ] Test manual/generated, explicit/default/null/custom và timezone sai.
- [ ] Test rollback và concurrent check trên database test.
- [ ] Chạy `test_shopping_router.py` cùng inventory regression liên quan.

**Dependencies:** Task 2.2; thực hiện trước Phase 3 vì cùng sửa shopping service.

**Files likely touched:** `src/backend/src/module/shopping_lists/shopping_dto.py`, `src/backend/src/module/shopping_lists/shopping_service.py`, `src/backend/src/test/test_shopping_router.py`, `src/backend/src/test/test_shopping_purchase_service.py` nếu cần.

**Estimated scope:** M — ba đến bốn file.

### Task 2.4 — Định nghĩa recipe_summary cho recommendation response

**Mục tiêu:** thêm DTO card recipe vào item recommendation mà không thay các field hiện hữu.

**Các bước:**

1. Tạo summary DTO chứa id/name/media_url/estimated_cooking_minutes/default_servings/nutrition.
2. Dùng nutrition tổng cho default servings; giữ Decimal nullable và `other_nutrients`.
3. Thêm `recipe_summary` nullable/default None vào `RecommendationItemDTO` để fixture/client cũ không vỡ trong rollout.
4. Không thêm cột recipe_summary vào RecipeModel hoặc bảng recipes.

**Acceptance criteria:**

- [ ] Schema mới là additive và giữ nguyên mọi field recommendation cũ.
- [ ] Nutrition semantics khớp recipe detail ở default servings.
- [ ] Không có model/migration database mới.

**Verification:**

- [ ] Test Pydantic/OpenAPI với nutrition null và Decimal serialize dạng number/string.

**Dependencies:** Task 0.1.

**Files likely touched:** `src/backend/src/module/recommendations/recommendation_dto.py`, `src/backend/src/test/test_recommendation_router.py`.

**Estimated scope:** S — hai file.

### Task 2.5 — Populate recipe_summary trong mock recommendation service

**Mục tiêu:** trả đủ dữ liệu card từ RecipeModel đã được query, không tạo N+1.

**Các bước:**

1. Map summary từ RecipeModel đang có trong `_to_item`/mapper tương ứng.
2. Tái sử dụng RecipeNutritionDTO/mapping hiện hữu khi thật sự phù hợp; không gọi HTTP `GET /recipes` nội bộ.
3. Giữ `analysis.is_mock=true`, `provider=MOCK`, E/A/P/U giả lập, 0–5 item, missing/near-expiry hiện tại và không ghi recommendation run.
4. Bổ sung test so sánh summary với recipe detail ở default servings và test query count.

**Acceptance criteria:**

- [ ] Mọi recipe được trả có summary đúng ID/name/card/nutrition.
- [ ] Service không query thêm từng recipe và không ghi kho/run.
- [ ] Response vẫn được nhận diện rõ là mock.

**Verification:**

- [ ] Chạy `.venv/bin/python -m pytest -q src/test/test_recommendation_provider.py src/test/test_recommendation_router.py`.
- [ ] Dùng fake/spy session xác nhận không N+1.

**Dependencies:** Task 2.4.

**Files likely touched:** `src/backend/src/module/recommendations/recommendation_service.py`, `src/backend/src/test/test_recommendation_provider.py`, `src/backend/src/test/test_recommendation_router.py`.

**Estimated scope:** M — ba file.

### Task 2.6 — Thêm barcode mock không tìm thấy

**Mục tiêu:** hỗ trợ FE kiểm tra nhánh barcode miss nhưng vẫn giữ HTTP 200 và provider mock.

**Các bước:**

1. Thêm một fixture barcode miss xác định trong extraction provider.
2. Trả status `FAILED`, giữ barcode input, đặt product fields nullable về null và thêm warning rõ; giữ `persisted=false`.
3. Giữ barcode là query parameter, không chuyển thành multipart/body và không gọi provider thật.
4. Bổ sung test fixture success, miss và thiếu query.

**Acceptance criteria:**

- [ ] Success và miss đều deterministic; miss trả HTTP 200 theo contract.
- [ ] Miss không tự lưu kho và không trả dữ liệu Whole Milk giả.
- [ ] Thiếu query vẫn trả 422 theo error envelope chung.

**Verification:**

- [ ] Chạy `.venv/bin/python -m pytest -q src/test/test_extractions.py`.

**Dependencies:** Task 1.1 và contract đã chốt status FAILED.

**Files likely touched:** `src/backend/src/module/extractions/extraction_provider.py`, `src/backend/src/test/test_extractions.py`.

**Estimated scope:** S — hai file.

### Checkpoint Phase 2

- [ ] FE có thể tìm shopping list active từ tài khoản.
- [ ] Check mua sắm có thể dùng catalog default mà vẫn nhập kho đúng một lần.
- [ ] Recommendation trả đủ card và vẫn là mock.
- [ ] Barcode miss hoạt động mà không đổi transport contract.

---

## Phase 3 — Persistence idempotency cho Shopping Lists

### Task 3.1 — Viết ShoppingMutationReceiptModel

**Mục tiêu:** khai báo ORM model append-only cho kết quả replay mutation shopping.

**Các bước:**

1. Tạo `ShoppingMutationReceiptModel` kế thừa `CreatedAtUUIDModel`.
2. Khai báo fields: `user_id`, `method`, `request_path`, `idempotency_key`, `key_hash`, `request_fingerprint`, `response_status`, `response_body`.
3. Khai báo FK user, unique `(user_id, method, request_path, key_hash)` và CHECK method/status/key/hash/body theo `plan.md` mục 5.8.3.
4. `response_body` nullable chỉ cho 204; không thêm FK tới shopping item vì item có thể đã bị DELETE.
5. Import model và cập nhật `__all__` trong `model/__init__.py`.

**Acceptance criteria:**

- [ ] Model/type/null/default/FK/UNIQUE/CHECK khớp mục 5.8.3.
- [ ] Base.metadata nhận diện bảng mới.
- [ ] Không sửa field ShoppingListModel/ShoppingListItemModel/InventoryLedgerEntryModel.

**Verification:**

- [ ] Test metadata/model schema trong `test_planning_schema.py`.

**Dependencies:** Task 0.1, Task 2.2 và Task 2.3.

**Files likely touched:** `src/backend/src/model/shopping_mutation_receipt_model.py`, `src/backend/src/model/__init__.py`, `src/backend/src/test/test_planning_schema.py`.

**Estimated scope:** M — ba file.

### Task 3.2 — Tạo migration DB-01 shopping_mutation_receipts

**Mục tiêu:** thêm bảng receipt vào database mà không thay dữ liệu cũ.

**Các bước:**

1. Sinh revision mới từ Alembic head thực tế, không dùng tên DB-01 làm revision ID.
2. CREATE bảng, FK, CHECK và UNIQUE đúng model; không thêm index trùng unique.
3. Rà autogenerate và loại mọi DROP/ALTER/CREATE TYPE ngoài phạm vi.
4. Chạy upgrade trên DB test có dữ liệu; so sánh snapshot trước/sau.
5. Nếu viết downgrade cho test, không cho xóa bảng khi đã có receipt; rollback production ưu tiên rollback app và giữ schema.

**Acceptance criteria:**

- [ ] Upgrade chỉ thêm bảng receipt và không đổi row/PK/balance/ledger cũ.
- [ ] ORM metadata và schema database khớp.
- [ ] Source vẫn có một Alembic head.

**Verification:**

- [ ] Thực hiện DB-V01 và DB-V02 trong `plan.md`.
- [ ] Chạy test migration/schema trên DB test biệt lập.

**Dependencies:** Task 3.1.

**Files likely touched:** `src/backend/alembic/versions/<revision>_phase2_shopping_mutation_receipts.py`, `src/backend/src/test/test_planning_schema.py`.

**Estimated scope:** S — migration và test.

### Task 3.3 — Cài đặt lookup, fingerprint và replay receipt

**Mục tiêu:** cung cấp logic dùng receipt nhất quán cho mutation shopping.

**Các bước:**

1. Canonicalize method/path có resource ID; path không chứa query string.
2. Hash key bằng SHA-256 để lookup; vẫn lưu raw key và so sánh raw key để tránh hash collision.
3. Fingerprint payload đã validate với field được gửi, sort key ổn định và giữ khác biệt omitted/null; tính trước khi resolve catalog default.
4. Nếu receipt tồn tại: fingerprint/raw key khớp thì replay status/body; khác thì 409 không mutation.
5. Chỉ lưu receipt thành công 200/201/204; 204 dùng SQL NULL, lỗi rollback không ghi receipt.

**Acceptance criteria:**

- [ ] Cùng scope/key/body replay đúng response snapshot.
- [ ] Cùng scope/key khác body trả 409.
- [ ] Key giống nhau ở user/resource khác không xung đột sai phạm vi.

**Verification:**

- [ ] Unit test canonicalization, omitted/null, hash/fingerprint, JSON body và 204.
- [ ] Test unique conflict: rollback transaction lỗi trước khi đọc receipt winner.

**Dependencies:** Task 3.2.

**Files likely touched:** `src/backend/src/module/shopping_lists/shopping_service.py`, `src/backend/src/test/test_shopping_idempotency.py`.

**Estimated scope:** S — hai file.

### Task 3.4 — Áp dụng receipt cho generate và add item

**Mục tiêu:** retry generate/add không tạo list/item trùng.

**Các bước:**

1. Với generate, lock plan và tra receipt; giữ behavior trả ACTIVE snapshot hiện hữu theo plan.
2. Với add item, lock shopping list thuộc user và tra receipt trước business write.
3. Thực hiện mutation, dựng public DTO, ghi receipt và commit trong cùng transaction.
4. Xử lý unique race bằng rollback rồi đọc receipt winner.

**Acceptance criteria:**

- [ ] Hai request add cùng key/body tạo một item và trả cùng resource ID.
- [ ] Retry generate không tạo list thứ hai và giữ snapshot contract hiện tại.
- [ ] Failure không để mutation hoặc receipt thành công một phần.

**Verification:**

- [ ] Thực hiện DB-V03/DB-V04 với database test và request cạnh tranh.
- [ ] Chạy shopping route/service regression.

**Dependencies:** Task 3.3.

**Files likely touched:** `src/backend/src/module/shopping_lists/shopping_service.py`, `src/backend/src/test/test_shopping_idempotency.py`, `src/backend/src/test/test_shopping_router.py`.

**Estimated scope:** M — ba file.

### Task 3.5 — Áp dụng receipt cho update và delete item

**Mục tiêu:** retry check/update/delete trả lại kết quả cũ mà không lặp mutation.

**Các bước:**

1. Tra receipt trước lookup item có thể đã bị DELETE.
2. Với PATCH, giữ atomic link batch/INITIAL_STOCK và public response snapshot.
3. Với DELETE, lưu receipt 204 trong cùng transaction và replay 204 sau khi item không còn.
4. Giữ rule chỉ manual unchecked item được xóa; generated/checked trả 409.

**Acceptance criteria:**

- [ ] Retry DELETE cùng key trả 204 thay vì 404.
- [ ] Retry PATCH/check không tạo batch hoặc ledger thứ hai.
- [ ] Key mới cho recheck vẫn tuân theo inventory_batch_id hiện hữu và không nhập kho lại.

**Verification:**

- [ ] Thực hiện DB-V05/DB-V06, gồm concurrent check và rollback.
- [ ] Chạy `test_shopping_router.py`, `test_inventory_router.py` và test idempotency mới.

**Dependencies:** Task 3.4.

**Files likely touched:** `src/backend/src/module/shopping_lists/shopping_service.py`, `src/backend/src/test/test_shopping_idempotency.py`, `src/backend/src/test/test_shopping_router.py`.

**Estimated scope:** M — ba file.

### Checkpoint Phase 3

- [ ] DB-01 nâng cấp an toàn và Base.metadata khớp database.
- [ ] Generate/add/update/delete có replay đúng phạm vi.
- [ ] Concurrent request không nhân đôi item, batch, ledger hoặc receipt.
- [ ] Không có cleanup/TTL hoặc public receipt API ngoài kế hoạch.

---

## Phase 4 — Vòng đời Meal Plan Item khi nấu

### Task 4.1 — Xác nhận quy tắc một item cho một lần nấu

**Mục tiêu:** chốt điều kiện được ghi trong `plan.md` trước khi sửa transaction cooking.

**Các bước:**

1. Dùng mặc định của plan: cooking tiếp tục bắt buộc `meal_plan_item_id`; không có hidden item semantics.
2. Xác nhận một meal-plan item chỉ được complete một lần và item chuyển từ PLANNED sang COMPLETED.
3. Kiểm kê dữ liệu chỉ đọc: item có nhiều session, nhiều completed session, hoặc status PLANNED nhưng có completed session.
4. Không xóa session, không backfill/update hàng loạt trong migration.

**Acceptance criteria:**

- [ ] Quy tắc và dữ liệu ngoại lệ hiện hữu được ghi trước khi code.
- [ ] Không thêm unique constraint gây lỗi dữ liệu cũ.
- [ ] Nhánh direct cooking vẫn deferred trừ khi có quyết định sản phẩm riêng.

**Verification:**

- [ ] Query audit chạy trên DB test/clone, không mutation.

**Dependencies:** Task 1.3.

**Files liên quan:** `src/backend/src/model/meal_plan_item_model.py`, `src/backend/src/model/cooking_session_model.py`, tài liệu quyết định hiện có.

**Estimated scope:** S — audit và chốt rule.

### Task 4.2 — Cập nhật completion transaction và lock order

**Mục tiêu:** completion cập nhật item/session/inventory/ledger atomically.

**Các bước:**

1. Áp dụng lock order nhất quán `plan → item → session → inventory batches` cho nhánh ghi liên quan.
2. Kiểm tra item còn PLANNED và recipe/servings snapshot phù hợp với session trước khi trừ kho.
3. Sau khi trừ kho thành công, chuyển MealPlanItemModel.status thành COMPLETED trong cùng transaction.
4. Same-key retry trả completion cũ; session khác của cùng item không được trừ kho lần hai.
5. Không thêm/xóa field model hoặc migration.

**Acceptance criteria:**

- [ ] Item, session, batch và ledger commit/rollback cùng nhau.
- [ ] Hai completion cạnh tranh chỉ có một lần trừ kho.
- [ ] GET meal plan phản ánh status COMPLETED sau commit.

**Verification:**

- [ ] Test DB cạnh tranh hai session cùng item và failure giữa transaction.
- [ ] Thực hiện DB-V07 và phần completion của DB-V11.

**Dependencies:** Task 4.1.

**Files likely touched:** `src/backend/src/module/cooking/cooking_service.py`, `src/backend/src/module/cooking/cooking_helper.py`, `src/backend/src/test/test_cooking_completion_service.py`.

**Estimated scope:** M — ba file.

### Task 4.3 — Chặn sửa/xóa meal-plan item đã được sử dụng

**Mục tiêu:** giữ lịch sử cooking/session/ledger khi FE sửa hoặc xóa plan item.

**Các bước:**

1. Trong PATCH/DELETE item, lock plan và item theo cùng thứ tự Phase 4.
2. Kiểm tra item đã COMPLETED hoặc đã được cooking session tham chiếu.
3. Trả 409 có detail rõ thay vì để lỗi FK hoặc làm dữ liệu session lệch item.
4. Giữ CRUD bình thường cho item PLANNED chưa được session tham chiếu.

**Acceptance criteria:**

- [ ] Item có session/completed không bị sửa recipe/servings hoặc xóa.
- [ ] Item PLANNED chưa dùng vẫn sửa/xóa theo API cũ.
- [ ] Không xóa/cascade session, consumption hoặc ledger.

**Verification:**

- [ ] Test PATCH/DELETE cạnh tranh với complete và cross-user.
- [ ] Chạy `test_meal_plan_router.py` và cooking regression.

**Dependencies:** Task 4.2.

**Files likely touched:** `src/backend/src/module/meal_plans/meal_plan_service.py`, `src/backend/src/test/test_meal_plan_router.py`, `src/backend/src/test/test_cooking_completion_service.py`.

**Estimated scope:** M — ba file.

### Task 4.4 — Kiểm tra tác động tới shopping snapshot

**Mục tiêu:** xác nhận trạng thái cooking không âm thầm sửa ACTIVE shopping list đã generate.

**Các bước:**

1. Tạo plan/item, generate list, complete item và đọc lại ACTIVE list.
2. Xác nhận ACTIVE list cũ giữ snapshot và inventory_batch_id liên quan.
3. Xác nhận lần generate/list mới theo logic hiện có chỉ lấy item PLANNED.
4. Ghi hành vi này trong contract, không triển khai refresh/replace generated items.

**Acceptance criteria:**

- [ ] Shopping list cũ không bị xóa hoặc tính lại ngầm.
- [ ] Query/generate mới không tính item COMPLETED.
- [ ] Contract mô tả rõ snapshot behavior.

**Verification:**

- [ ] Chạy integration flow meal-plan → shopping → cooking → read shopping.

**Dependencies:** Task 4.3 và Phase 3 hoàn thành.

**Files likely touched:** `src/backend/src/test/test_shopping_idempotency.py`, `src/backend/src/test/test_cooking_completion_service.py`, `docs/api-contract.md`.

**Estimated scope:** M — ba file.

### Checkpoint Phase 4

- [ ] Một item không bị complete/trừ kho hai lần.
- [ ] Không có schema migration hoặc field mới cho lifecycle.
- [ ] Session/ledger/history cũ được giữ.
- [ ] Shopping snapshot behavior đã được test và ghi tài liệu.

---

## Phase 5 — Reports và Waste Reduction Evidence (P2)

### Task 5.1 — Chốt metric và response Reports

**Mục tiêu:** chốt nghĩa số liệu trước khi tạo model/bảng báo cáo.

**Các bước:**

1. Dùng metric v1 trong plan: ước tính khối lượng RAW_INGREDIENT được dùng khi chưa hết hạn và nằm trong warning window tại lúc complete.
2. Chỉ GRAM/KG quy đổi sang kg; không quy đổi ML/LITER/PIECE/PACK/OTHER khi thiếu density/mass.
3. Chốt kỳ lịch Asia/Ho_Chi_Minh: week bắt đầu thứ Hai, month từ ngày 1, year từ 01/01; query bằng khoảng nửa mở sau khi đổi sang UTC.
4. Giữ bốn field M7 và bổ sung metadata coverage/labels đã nêu trong plan.
5. Chốt exclusion priority và `metric_version=near-expiry-v1`.
6. Tạo ví dụ tính tay cho empty, eligible, expired, unknown expiry, unsupported unit và cooked leftover.

**Acceptance criteria:**

- [ ] Metric, period, series, labels, rounding, top 5 và coverage không còn mơ hồ.
- [ ] Không gọi mọi COOKING_CONSUMPTION là saved kg.
- [ ] FE tiếp tục mock cho đến Checkpoint Phase 5.

**Verification:**

- [ ] Review expected totals từ dataset mẫu trước khi viết SQL/model.

**Dependencies:** Task 0.1.

**Files likely touched:** `docs/api-contract.md`, `docs/phase2/plan.md` chỉ nếu quyết định đã chốt khác phần mặc định tương ứng.

**Estimated scope:** S — tài liệu contract/metric.

### Task 5.2 — Viết WasteReductionEventModel

**Mục tiêu:** khai báo evidence snapshot cho từng inventory ledger consumption được xét.

**Các bước:**

1. Tạo model kế thừa `CreatedAtUUIDModel`.
2. Khai báo fields: `inventory_ledger_entry_id`, `user_id`, `inventory_batch_id`, `cooking_session_id`, `master_ingredient_id`, `ingredient_name_snapshot`, `batch_type_snapshot`, `quantity`, `unit`, `mass_kg`, `expires_at_snapshot`, `consumed_at`, `warning_days`, `metric_version`, `is_eligible`, `exclusion_reason`.
3. Tái sử dụng enum PostgreSQL `measurement_unit` và `inventory_batch_type`; không tạo type trùng.
4. Thêm FK, unique ledger ID, index `(user_id, consumed_at)` và CHECK eligibility/exclusion/positive numeric theo mục 5.8.4.
5. Import model vào `model/__init__.py`; không thêm field vào ledger/batch/user.

**Acceptance criteria:**

- [ ] Model đầy đủ type/null/default/FK/UNIQUE/CHECK/index của plan.
- [ ] `mass_kg` và `expires_at_snapshot` nullable đúng nghĩa unknown/unsupported.
- [ ] Base.metadata nhận bảng và enum cũ không bị khai báo trùng.

**Verification:**

- [ ] Thêm test metadata tại `test_report_schema.py`.

**Dependencies:** Task 5.1.

**Files likely touched:** `src/backend/src/model/waste_reduction_event_model.py`, `src/backend/src/model/__init__.py`, `src/backend/src/test/test_report_schema.py`.

**Estimated scope:** M — ba file.

### Task 5.3 — Tạo migration DB-02 waste_reduction_events

**Mục tiêu:** thêm bảng evidence mà không sửa ledger bất biến hoặc backfill sai dữ liệu.

**Các bước:**

1. Sinh revision mới từ head sau migration đã merge gần nhất.
2. CREATE bảng/FK/CHECK/UNIQUE/index đúng Task 5.2; tái sử dụng enum hiện có.
3. Không backfill từ expires_at hiện tại và không tạo event 0 cho lịch sử.
4. Rà autogenerate; loại DROP/ALTER/CREATE TYPE ngoài phạm vi.
5. Upgrade DB test có dữ liệu và xác nhận ledger trigger vẫn hoạt động.

**Acceptance criteria:**

- [ ] Migration chỉ thêm schema reports đã định nghĩa.
- [ ] Bảng mới rỗng sau upgrade, dữ liệu cũ và immutable ledger giữ nguyên.
- [ ] Alembic vẫn chỉ có một head.

**Verification:**

- [ ] Thực hiện DB-V01/DB-V02 và test duplicate inventory_ledger_entry_id.

**Dependencies:** Task 5.2 và migration Phase 3 đã merge nếu có.

**Files likely touched:** `src/backend/alembic/versions/<revision>_phase2_waste_reduction_events.py`, `src/backend/src/test/test_report_schema.py`.

**Estimated scope:** S — migration và test.

### Task 5.4 — Viết logic phân loại và snapshot waste event

**Mục tiêu:** tạo evidence đúng tại thời điểm consumption, gồm cả eligible và excluded.

**Các bước:**

1. Nhận ledger object từ `apply_quantity_change()` hiện đã return `InventoryLedgerEntryModel`; không sửa inventory service chỉ để lấy ledger ID.
2. Chụp batch metadata trước mutation và dùng một `consumed_at` chung với `session.completed_at`.
3. Phân loại theo priority: cooked food → unknown expiry → expired → outside warning window → unsupported unit.
4. Quy đổi KG/GRAM bằng Decimal; từ chối NaN/Infinity; ghi `mass_kg=null` khi không đổi được.
5. Ghi cả event excluded để phân biệt thiếu evidence với unsupported/ineligible.

**Acceptance criteria:**

- [ ] Mỗi consumption được xét sinh đúng một event snapshot.
- [ ] Eligibility, exclusion_reason và mass_kg đúng dataset Task 5.1.
- [ ] Không nhận evidence field từ request FE.

**Verification:**

- [ ] Unit test clock cố định cho boundary expiry/warning và mọi unit/batch type.

**Dependencies:** Task 5.3.

**Files likely touched:** `src/backend/src/module/reports/report_service.py` hoặc helper trong module reports, `src/backend/src/test/test_report_events.py`.

**Estimated scope:** S — hai file.

### Task 5.5 — Ghi event trong cooking completion transaction

**Mục tiêu:** session, item, consumption, batch, ledger và report evidence commit cùng nhau.

**Các bước:**

1. Giữ object ledger do mỗi lần `apply_quantity_change()` trả về.
2. Flush ledger nếu cần ID rồi stage WasteReductionEventModel; không commit ở giữa.
3. Kết hợp với status item COMPLETED từ Phase 4 trong cùng transaction.
4. Same-key replay không thêm event; lỗi insert event rollback toàn bộ completion.

**Acceptance criteria:**

- [ ] Một ledger consumption có tối đa một event.
- [ ] Lỗi event không để stock/session/item/ledger thay đổi một phần.
- [ ] Sửa expiry/tên batch sau đó không đổi snapshot event.

**Verification:**

- [ ] Thực hiện DB-V07/DB-V08 bằng database test.
- [ ] Chạy cooking completion regression.

**Dependencies:** Task 5.4 và Phase 4 hoàn thành.

**Files likely touched:** `src/backend/src/module/cooking/cooking_helper.py`, `src/backend/src/test/test_cooking_completion_service.py`, `src/backend/src/test/test_report_events.py`.

**Estimated scope:** M — ba file.

### Task 5.6 — Viết Report DTO và aggregate service

**Mục tiêu:** tính response `/reports/waste-reduction` từ evidence theo user và kỳ.

**Các bước:**

1. Tạo query DTO period default month và enum week/month/year.
2. Tạo DTO cho total, period, weekly_series, top_saved_ingredients cùng labels/period bounds/timezone/coverage đã chốt.
3. Query theo `user_id`, `consumed_at`, `metric_version`; cộng `mass_kg` chỉ khi eligible.
4. Group top theo master ingredient; dùng snapshot name mới nhất trong kỳ và tie-break ổn định.
5. Tính `missing_evidence_count` từ cooking ledger/session LEFT JOIN event; tính unsupported riêng từ event mass_kg null.
6. Empty data trả 200-shaped DTO với total 0, series phù hợp và coverage rõ.

**Acceptance criteria:**

- [ ] Tổng mọi eligible event khác top 5 subtotal và được làm tròn ở output.
- [ ] Series/kỳ/labels đúng timezone và ranh lịch.
- [ ] Dữ liệu user khác, event version khác hoặc excluded không bị cộng.

**Verification:**

- [ ] Chạy `test_report_service.py` với empty, boundary, top, coverage và user isolation.
- [ ] Thực hiện DB-V08/DB-V09.

**Dependencies:** Task 5.5.

**Files likely touched:** `src/backend/src/module/reports/report_dto.py`, `src/backend/src/module/reports/report_service.py`, `src/backend/src/test/test_report_service.py`.

**Estimated scope:** M — ba file.

### Task 5.7 — Setup module và route GET reports/waste-reduction

**Mục tiêu:** công bố Reports API qua `/api` với Bearer auth.

**Các bước:**

1. Tạo package `module/reports` và `report_dependency.py` cung cấp ReportService từ DB session.
2. Tạo `report_router.py` prefix `/reports`, route GET `/waste-reduction`, response model và query DTO Task 5.6.
3. Import/include router trong `src/app.py` dưới `API_PREFIX=/api`.
4. Bổ sung route tests 200/401/422 và OpenAPI schema.
5. Không thêm cache/worker/report mutation route.

**Acceptance criteria:**

- [ ] `GET /api/reports/waste-reduction?period=...` trả đúng DTO và Bearer auth.
- [ ] Period sai trả 422 envelope chung; user không dữ liệu trả 200.
- [ ] App cũ vẫn đăng ký toàn bộ router hiện hữu.

**Verification:**

- [ ] Chạy `test_report_router.py` và `test_report_service.py`.
- [ ] Kiểm tra OpenAPI có route mới và không mất route cũ.

**Dependencies:** Task 5.6.

**Files likely touched:** `src/backend/src/module/reports/__init__.py`, `src/backend/src/module/reports/report_dependency.py`, `src/backend/src/module/reports/report_router.py`, `src/backend/src/app.py`, `src/backend/src/test/test_report_router.py`.

**Estimated scope:** M — năm file.

### Checkpoint Phase 5

- [ ] Evidence writer đã chạy trước hoặc đồng thời với reader theo rollout đã ghi.
- [ ] Report trả dữ liệu thật có coverage, không trả mock dưới dạng dữ liệu thật.
- [ ] Migration không backfill/sửa ledger cũ.
- [ ] Chỉ sau checkpoint này FE mới chuyển màn Reports khỏi mock.

---

## Phase 6 — Subscription/Premium Interest (P2)

### Task 6.1 — Viết PremiumInterestModel

**Mục tiêu:** lưu một đăng ký quan tâm premium cho mỗi user.

**Các bước:**

1. Tạo model dùng `Base` trực tiếp với `user_id` UUID làm PK/FK users.id.
2. Thêm `registered_at` TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP.
3. Không thêm `id`, updated_at, plan, expires_at, payment_status hoặc email snapshot.
4. Import model trong `model/__init__.py`; không sửa UserModel/preferences.

**Acceptance criteria:**

- [ ] Model đúng hai field và một row/user.
- [ ] Base.metadata nhận bảng mới.
- [ ] UserModel schema giữ nguyên.

**Verification:**

- [ ] Test metadata/model trong `test_subscription_service.py` hoặc schema test phù hợp.

**Dependencies:** Task 0.1.

**Files likely touched:** `src/backend/src/model/premium_interest_model.py`, `src/backend/src/model/__init__.py`, `src/backend/src/test/test_subscription_service.py`.

**Estimated scope:** M — ba file.

### Task 6.2 — Tạo migration DB-03 premium_interests

**Mục tiêu:** tạo persistence premium interest mà không thêm subscription/payment schema.

**Các bước:**

1. Sinh revision mới từ Alembic head đã merge gần nhất.
2. CREATE `premium_interests(user_id PK/FK, registered_at)` đúng model.
3. Không backfill user hiện hữu và không copy mock state vào database.
4. Upgrade DB test có dữ liệu, kiểm tra một head và schema diff.

**Acceptance criteria:**

- [ ] Migration chỉ thêm bảng premium_interests.
- [ ] Bảng rỗng sau upgrade; user/profile/preferences cũ không đổi.
- [ ] PK user_id đủ cho lookup/upsert, không có index trùng.

**Verification:**

- [ ] Thực hiện DB-V01/DB-V02 cho DB-03.

**Dependencies:** Task 6.1 và migration gần nhất đã merge.

**Files likely touched:** `src/backend/alembic/versions/<revision>_phase2_premium_interests.py`, `src/backend/src/test/test_subscription_service.py`.

**Estimated scope:** S — hai file.

### Task 6.3 — Viết Subscription DTO và service

**Mục tiêu:** cung cấp GET free/null và POST đăng ký quan tâm idempotent theo user.

**Các bước:**

1. Tạo response DTO GET `{plan: free|premium, expires_at}` và POST `{registered:true}`.
2. GET MVP luôn trả `free/null`, không phụ thuộc premium interest.
3. POST insert premium interest; on conflict user_id giữ row và registered_at đầu tiên.
4. Commit trước khi trả registered=true; lỗi DB dùng envelope chung.
5. Không dùng UserModel.preferences, không đổi role/plan và không thêm Idempotency-Key bắt buộc.

**Acceptance criteria:**

- [ ] GET luôn free/null trong MVP.
- [ ] POST lặp/concurrent chỉ có một row và giữ registered_at đầu tiên.
- [ ] PATCH profile preferences không làm mất interest.

**Verification:**

- [ ] Chạy service/database test retry, concurrent insert, rollback và user isolation.
- [ ] Thực hiện DB-V10.

**Dependencies:** Task 6.2.

**Files likely touched:** `src/backend/src/module/subscription/subscription_dto.py`, `src/backend/src/module/subscription/subscription_service.py`, `src/backend/src/test/test_subscription_service.py`.

**Estimated scope:** M — ba file.

### Task 6.4 — Setup module và hai route Subscription

**Mục tiêu:** công bố hai endpoint Subscription qua `/api` với Bearer auth.

**Các bước:**

1. Tạo package/module dependency từ DB session.
2. Tạo router prefix `/subscription` với GET `""` và POST `/premium-interest`.
3. POST không nhận business body; giữ status 200 và response `{registered:true}`.
4. Import/include router trong `src/app.py`.
5. Bổ sung route tests 200/401/error/retry và OpenAPI.

**Acceptance criteria:**

- [ ] `/api/subscription` và `/api/subscription/premium-interest` có Bearer auth và đúng body/status.
- [ ] Không có payment, checkout, webhook hoặc feature gating.
- [ ] Router mới không làm mất/đổi router hiện hữu.

**Verification:**

- [ ] Chạy `test_subscription_router.py` và `test_subscription_service.py`.
- [ ] Kiểm tra OpenAPI có đúng hai operation mới.

**Dependencies:** Task 6.3.

**Files likely touched:** `src/backend/src/module/subscription/__init__.py`, `src/backend/src/module/subscription/subscription_dependency.py`, `src/backend/src/module/subscription/subscription_router.py`, `src/backend/src/app.py`, `src/backend/src/test/test_subscription_router.py`.

**Estimated scope:** M — năm file.

### Checkpoint Phase 6

- [ ] Premium interest được lưu đúng một row/user.
- [ ] GET Subscription vẫn free/null và không mở premium.
- [ ] Không có payment/gating ngoài contract.
- [ ] Chỉ sau checkpoint này FE mới chuyển màn Subscription khỏi mock.

---

## Phase 7 — Migration, regression và E2E tổng thể

### Task 7.1 — Kiểm tra toàn bộ chuỗi migration Phase 2

**Mục tiêu:** xác nhận các migration mới nâng cấp an toàn theo đúng thứ tự merge.

**Các bước:**

1. Kiểm tra chỉ có một Alembic head và mỗi `down_revision` trỏ revision trước đó.
2. Nâng một DB test có dữ liệu từ head cũ qua toàn bộ revision Phase 2.
3. So sánh snapshot row/PK/balance/ledger/trigger trước/sau.
4. Đối chiếu Base.metadata với schema DB; không có enum/index/type trùng hoặc schema diff ngoài phạm vi.
5. Kiểm tra app version cũ vẫn chạy trên schema mới và rollback app không xóa bảng mới.

**Acceptance criteria:**

- [ ] DB-V01, DB-V02 và DB-V12 đạt cho mọi migration đã chọn triển khai.
- [ ] Không DROP/TRUNCATE/backfill không có bằng chứng.
- [ ] Script baseline reconcile không bị dùng để stamp Phase 2 về revision cũ.

**Verification:**

- [ ] Chạy Alembic heads/current/upgrade trên DB test biệt lập.
- [ ] Chạy schema/model tests của shopping, reports và subscription.

**Dependencies:** Phase 3, Phase 5 và Phase 6 tương ứng với các migration thực tế đã triển khai.

**Files likely touched:** các migration mới và schema tests; không sửa migration cũ.

**Estimated scope:** M — kiểm thử tích hợp migration.

### Task 7.2 — Chạy regression API giữ lại

**Mục tiêu:** chứng minh các route hiện hữu không bị mất hoặc thay đổi ngoài contract.

**Các bước:**

1. Chạy test contract/route của extraction, notification, recommendation, meal plan và shopping.
2. Chạy inventory/cooking/auth/user/favorite regression.
3. Kiểm tra OpenAPI vẫn chứa 77 operation cũ cộng đúng 4 endpoint mới: GET shopping lists, GET reports, GET subscription, POST premium interest.
4. Ghi rõ test DB bị skip; skip không được coi là database đã nghiệm thu.

**Acceptance criteria:**

- [ ] Mọi test liên quan pass hoặc có failure được xử lý trước release.
- [ ] Không mất Auth/User/Favorites/health/push-test route hiện hữu.
- [ ] Recommendation/Extraction vẫn ghi rõ mock.

**Verification:**

- [ ] Chạy các lệnh regression ở `plan.md` mục 7.3.
- [ ] Chạy quality checks trong `pyproject.toml` trên file đã sửa.

**Dependencies:** Các Phase được chọn triển khai đã qua checkpoint.

**Files likely touched:** chỉ sửa file gây failure đúng phạm vi; không format toàn repository.

**Estimated scope:** M — kiểm tra toàn hệ thống liên quan.

### Task 7.3 — Chạy E2E theo api-contract

**Mục tiêu:** xác nhận luồng FE chính hoạt động từ auth đến cooking/report/subscription.

**Các bước:**

1. Login → recommendations mock đủ card → tạo/đọc plan → thêm item với recommendation_run_id null → generate list.
2. Xóa local list_id giả lập → GET shopping-lists ACTIVE → GET detail.
3. Check manual/generated item bằng explicit/default storage → retry cùng key → kiểm tra một batch/một ledger.
4. Preview → create session → complete → kiểm tra item status, stock, ledger, history và shopping snapshot.
5. Kiểm tra upload MIME sai và barcode miss không ghi kho.
6. Kiểm tra Reports empty/coverage/evidence và Premium Interest retry; GET Subscription vẫn free/null.

**Acceptance criteria:**

- [ ] Sáu luồng đạt đúng status/body/transaction trong contract.
- [ ] Không leak dữ liệu giữa hai user test.
- [ ] Không có partial write sau lỗi 409/422/DB rollback.

**Verification:**

- [ ] Lưu kết quả pass/fail, target DB test và số row kiểm chứng cho từng luồng.

**Dependencies:** Task 7.1 và Task 7.2.

**Files likely touched:** test E2E/integration hiện hữu hoặc file test Phase 2 phù hợp.

**Estimated scope:** M — E2E kiểm chứng.

### Task 7.4 — Hoàn thiện tài liệu bàn giao BE

**Mục tiêu:** đồng bộ contract với code cuối cùng và ghi rõ phần deferred.

**Các bước:**

1. Cập nhật `docs/api-contract.md` theo status/request/response/OpenAPI cuối cùng.
2. Đánh dấu Reports/Subscription khỏi MOCK ONLY chỉ khi checkpoint tương ứng đạt; Recommendation vẫn mock.
3. Ghi migration revision thực tế, thứ tự rollout và coverage start của Reports.
4. Ghi các quyết định chưa thực hiện: direct cooking, leftover retry/multiple leftovers và các issue ngoài M7.
5. Không thay `plan.md` bằng lịch sử triển khai; task nào hoàn thành thì đánh dấu trong file này.

**Acceptance criteria:**

- [ ] BE có thể tra từ endpoint → DTO/service/model/migration/test đã triển khai.
- [ ] FE biết endpoint nào còn mock và cách retry/status compatibility.
- [ ] Không có tuyên bố “đã hoàn thành” khi DB test/E2E bị skip.

**Verification:**

- [ ] Review contract với OpenAPI và kết quả Task 7.3.
- [ ] Chạy `git diff --check` và kiểm tra link tài liệu.

**Dependencies:** Task 7.3.

**Files likely touched:** `docs/api-contract.md`, `docs/phase2/task.md`, tài liệu BE liên quan nếu contract thay đổi.

**Estimated scope:** S — tài liệu bàn giao.

### Checkpoint Phase 7 — Hoàn thành Phase 2

- [ ] Tất cả task bắt buộc của Phase 0–4 đã đạt.
- [ ] Phase 5/6 chỉ được công bố nếu checkpoint riêng đạt; nếu chưa, FE tiếp tục mock.
- [ ] Migration và dữ liệu cũ được bảo toàn.
- [ ] Regression, DB integration và E2E có kết quả rõ ràng.
- [ ] API contract, OpenAPI và code không mâu thuẫn.

---

## Phase 8 — Nhánh có điều kiện: Direct Cooking (P3)

> Không thực hiện Phase này theo mặc định. Chỉ mở khi sản phẩm quyết định cho phép nấu ngoài meal plan. Không triển khai đồng thời workaround “hidden meal-plan item”.

### Task 8.1 — Xác nhận schema và contract direct cooking

**Mục tiêu:** kiểm tra nền hiện hữu trước khi mở request mới.

**Các bước:**

1. Xác nhận ORM và DB deploy đều cho phép `cooking_sessions.meal_plan_item_id` null.
2. Chốt request preview/create-session nhận đúng một trong `{meal_plan_item_id}` hoặc `{recipe_id, servings?}`.
3. Chốt servings mặc định theo recipe và validation dương/hữu hạn.
4. Không thêm route `/cooking/quick`, không xóa FK và không thay request planned hiện hữu.

**Acceptance criteria:**

- [ ] Schema deploy nullable thật; nếu không, lập migration additive phù hợp trước code.
- [ ] XOR request được ghi trong contract.
- [ ] Luồng meal-plan cũ giữ nguyên.

**Verification:**

- [ ] Inspect schema DB và OpenAPI dự kiến.

**Dependencies:** Quyết định sản phẩm explicit và Phase 4 hoàn thành.

**Files liên quan:** `src/backend/src/model/cooking_session_model.py`, `src/backend/src/module/cooking/cooking_dto.py`, `docs/api-contract.md`.

**Estimated scope:** S.

### Task 8.2 — Mở rộng preview và create-session cho recipe trực tiếp

**Mục tiêu:** tái sử dụng cooking/FEFO hiện hữu cho direct cooking.

**Các bước:**

1. Mở rộng DTO XOR theo Task 8.1 cho cả preview và create session.
2. Resolve recipe/default servings khi không có meal-plan item; giữ ownership/catalog validation.
3. Tái sử dụng build_preview, kiểm tra tồn kho, completion, leftover và history hiện hữu.
4. Lưu CookingSessionModel.meal_plan_item_id null cho direct session; không tạo meal-plan item ẩn.
5. Bổ sung test direct/planned/cross-user và invalid XOR.

**Acceptance criteria:**

- [ ] Direct và planned flow dùng cùng FEFO/transaction và response hiện hữu.
- [ ] Request có cả hai hoặc không có cả hai identity trả 422.
- [ ] Không làm thay đổi behavior của planned cooking.

**Verification:**

- [ ] Chạy cooking router/service/completion/history regression và test direct mới.

**Dependencies:** Task 8.1.

**Files likely touched:** `src/backend/src/module/cooking/cooking_dto.py`, `src/backend/src/module/cooking/cooking_service.py`, `src/backend/src/test/test_cooking_router.py`, `src/backend/src/test/test_cooking_service.py`.

**Estimated scope:** M — bốn file.

---

## 3. Bảng phụ thuộc task rút gọn

| Task | Phụ thuộc trực tiếp |
|---|---|
| 0.1 | Không có |
| 0.2 | 0.1 |
| 1.1, 1.3 | 0.1 |
| 1.2 | 0.1 + FE nhận 200/201 |
| 2.1 | 0.1 |
| 2.2 | 2.1 |
| 2.3 | 2.2 |
| 2.4 | 0.1 |
| 2.5 | 2.4 |
| 2.6 | 1.1 |
| 3.1 | 0.1, 2.2, 2.3 |
| 3.2 | 3.1 |
| 3.3 | 3.2 |
| 3.4 | 3.3 |
| 3.5 | 3.4 |
| 4.1 | 1.3 |
| 4.2 | 4.1 |
| 4.3 | 4.2 |
| 4.4 | 4.3 + Phase 3 |
| 5.1 | 0.1 |
| 5.2 | 5.1 |
| 5.3 | 5.2 + migration head hiện tại |
| 5.4 | 5.3 |
| 5.5 | 5.4 + Phase 4 |
| 5.6 | 5.5 |
| 5.7 | 5.6 |
| 6.1 | 0.1 |
| 6.2 | 6.1 + migration head hiện tại |
| 6.3 | 6.2 |
| 6.4 | 6.3 |
| 7.1 | Các migration Phase 3/5/6 đã chọn |
| 7.2 | Các Phase đã chọn qua checkpoint |
| 7.3 | 7.1, 7.2 |
| 7.4 | 7.3 |
| 8.1 | Quyết định sản phẩm + Phase 4 |
| 8.2 | 8.1 |

## 4. Definition of Done dùng cho mọi task code

- [ ] Request validation, authentication và ownership đúng contract.
- [ ] Response model, status code và error envelope được phản ánh trong OpenAPI.
- [ ] Test task pass; test DB không bị skip nếu task liên quan transaction/constraint/migration.
- [ ] Không xóa route, table, field hoặc dữ liệu hiện hữu; chỉ Task 0.2 được xóa các file migration cũ theo phạm vi đã chốt.
- [ ] Không tạo abstraction/dependency/schema ngoài phần đã ghi trong `plan.md`.
- [ ] File thay đổi vượt khoảng năm file phải được tách thành task/commit theo ranh DTO/service/model/migration/route đã liệt kê.
- [ ] `git diff --check` và quality checks của `src/backend/pyproject.toml` đạt trên phạm vi thay đổi.
