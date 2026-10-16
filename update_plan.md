# Kế hoạch cập nhật Backend — FreshCheck với PostgreSQL runtime

**Trạng thái:** Đã chốt hướng PostgreSQL runtime, chờ phê duyệt task trước khi triển khai
**Phạm vi:** Backend FastAPI trong `src/backend`, sử dụng dữ liệu từ `data_freshness` và bộ bàn giao `sweepfood_tools`.
**Không thuộc phạm vi đợt này:** UI mobile/web, huấn luyện mô hình AI, và tự động discard số lượng tồn kho.

## 0. Handoff contract cho AI agent

Kế hoạch này giả định toàn bộ bảng FreshCheck nằm trong **cùng PostgreSQL database** với backend, để dùng foreign key và transaction nguyên tử với inventory/ledger. Không được tự chuyển sang database riêng, thêm dependency mới, đổi public API hoặc sửa dữ liệu nguồn nếu chưa có phê duyệt mới.

AI agent phải tuân thủ các quy tắc sau:

- Làm tuần tự theo task; không bắt đầu task có dependency chưa đạt checkpoint.
- Không áp toàn bộ `sweep-food_be_freshness-api.patch` mù quáng. Dùng nó làm nguồn tham khảo, rồi điều chỉnh theo task và model inventory hiện có.
- Chỉ Alembic được tạo/sửa schema. Không chạy DDL trong `data_freshness/scripts/sync_to_postgres.py` trên môi trường thật.
- Không sửa, ghi đè hoặc normalize lại `data123/normalized/*.json`. Đây là catalog release đầu vào đã chuẩn hóa.
- Không tạo mapping có foreign key `NULL`; không dùng fuzzy match tại request runtime; không tự động map những trường hợp mơ hồ.
- Test chỉ chạy unit và không ghi database.
- Trước mỗi merge checkpoint: chạy focused tests, `ruff`, format check, `mypy --strict`, và báo cáo `git status`.

### 0.1. Nguồn dữ liệu và quyền sở hữu

| Đường dẫn                                                                                    | Vai trò                                                                          | Quy tắc sử dụng                                                                                    |
| ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `data123/normalized/master_ingredients.json`                                                   | Catalog master đã chuẩn hóa, ID UUID và canonical name.                      | Import vào `master_ingredients`; không bổ sung FreshCheck ID vào file này.                     |
| `data123/normalized/ingredient_categories.json`, `recipes.json`, `recipe_ingredients.json` | Catalog liên quan mà importer hiện hữu yêu cầu.                             | Import cùng release để giữ foreign key catalog hợp lệ.                                          |
| `src/backend/scripts/import_data.py`                                                           | Importer hiện có: validate toàn bộ 4 JSON rồi upsert trong một transaction. | Là entry point catalog; cần nâng cấp safety như Task 0.1 trước khi chạy trên database thật. |
| `data_freshness/**/*.yaml`                                                                     | Nguồn biên soạn FreshCheck KB.                                                 | Chỉ review/version qua Git; không phải runtime input.                                              |
| `data_freshness/build/freshcheck_kb.json`                                                      | Artifact KB đã build/validate.                                                  | Input duy nhất cho sync KB vào PostgreSQL.                                                          |
| `data_freshness/mappings/master_ingredient_freshcheck_mappings.yaml`                           | Manifest mapping mới, được review.                                            | Tạo trong Task 4; là source of truth cho seed mapping, không suy luận khi người dùng gọi API. |

### 0.2. Luồng triển khai bắt buộc

```text
normalized catalog JSON
  -> validate + transactional import
  -> master_ingredients có UUID ổn định
  -> build/validate FreshCheck artifact
  -> Alembic tạo KB tables
  -> sync + activate KB version
  -> candidate report -> reviewed mapping manifest -> idempotent mapping seed
  -> engine/repository/API/assessment
  -> notification + AI recommendation regression + rollout
```

### 0.3. Contract mapping manifest

Manifest không chứa dòng có giá trị null. Mỗi record được duyệt trước khi seed, tối thiểu có:

```yaml
kb_version: "0.3.0"
mappings:
  - master_ingredient_id: "<UUID từ master_ingredients.json>"
    freshcheck_ingredient_id: "<ID từ freshcheck_ingredients>"
    match_method: "EXACT_CODE|EXACT_NAME|MANUAL_REVIEW"
    reviewed_by: "<reviewer>"
    note: "<optional non-empty rationale>"
```

Nếu catalog item không map được thì **không tạo record mapping**; candidate script đưa nó vào `unmapped` hoặc `ambiguous` report. Batch dùng `custom_name` nên không có `master_ingredient_id` vẫn hoạt động trong inventory, nhưng FreshCheck phải trả `422 MAPPING_UNAVAILABLE`, không trả con số ước tính.

`master_ingredients.json` hiện không có trường mã FreshCheck ở root contract. Vì vậy candidate script phải coi `EXACT_NAME` là lựa chọn tự động khả dụng hiện tại; `EXACT_CODE` chỉ dùng khi một stable code đã được xác minh từ dữ liệu đã import. Các tên không trùng tuyệt đối chỉ được đưa vào `MANUAL_REVIEW`, không được fuzzy-map tự động.

## 1. Mục tiêu

Đưa FreshCheck vào luồng quản lý lô tồn kho để người dùng có thể đánh giá thực phẩm tươi không có hạn in sẵn. Backend sẽ lấy thời gian bảo quản, câu hỏi cảm quan và quy tắc an toàn từ knowledge base (KB); sau đó trả về khuyến nghị có giải thích và, khi phù hợp, cập nhật hạn dùng an toàn của lô tồn kho.

Luồng mục tiêu:

```text
YAML trong data_freshness (authoring, Git versioned)
  -> build/freshcheck_kb.json (artifact đã kiểm định + checksum)
  -> sync transaction vào PostgreSQL (runtime source of truth)
  -> FreshCheck repository/cache + inference engine
  -> assessment history + inventory audit + expires_at
  -> notification và dữ liệu hours_to_expire cho AI recommendation
```

## 2. Thành phần đầu vào và cách sử dụng

| Thành phần                                          | Vai trò trong đợt tích hợp                                                                 | Cách dùng                                                                                                        |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `data_freshness`                                    | Nguồn authoring chuẩn: ingredient, archetype, shelf-life, rubric cảm quan, claim và source. | Build artifact, validate và sync vào schema PostgreSQL do Alembic quản lý; YAML không là runtime dependency. |
| `sweepfood_tools/sweep-food_be_freshness-api.patch` | Bản khởi tạo cho engine, module FastAPI, router, DTO và test FreshCheck.                    | Đã gộp vào `dev` (commit `77abd5d`); file patch đã xoá, xem lịch sử git nếu cần tham khảo.                |
| `sweepfood_tools/fridge_report.py`                  | Công cụ đánh giá offline hiệu quả gợi ý món từ dữ liệu tủ lạnh thật.            | Chạy sau khi luồng BE đã phát hành; không đưa vào API production.                                        |

## 3. Quyết định kiến trúc đã chốt

1. **PostgreSQL là runtime source duy nhất.** YAML vẫn được review/version qua Git; JSON là release artifact đã kiểm định, được lưu trong database cùng checksum để audit/rollback. Backend không đọc `FRESHCHECK_KB_PATH` khi phục vụ API.
2. **Hạn nhà sản xuất luôn thắng.** Nếu `expiration_source == MANUFACTURER`, FreshCheck chỉ trình bày số ngày còn lại từ hạn in, không ghi đè `expires_at`.
3. **Đánh giá FreshCheck không tự động bỏ thực phẩm.** Dấu hiệu `hard_stop` đặt hạn dùng về hiện tại và trả khuyến nghị bỏ thực phẩm; người dùng vẫn phải dùng API discard hiện có để thay đổi số lượng.
4. **KB bất biến theo version.** Sync cùng `kb_version`/checksum là idempotent; cùng version nhưng checksum khác bị từ chối. Một version active duy nhất được chọn qua workflow stage/activate có audit.
5. **Liên kết nguyên liệu bằng khóa rõ ràng, không chỉ bằng tên.** Mapping versioned nối `master_ingredient` với `freshcheck_ingredient_id`; alias chỉ hỗ trợ tạo mapping và mọi ambiguity phải có báo cáo.
6. **Mỗi lần đánh giá là một bản ghi bất biến.** Assessment lưu answers, claims, KB/rule version, score/tier, expiry áp dụng và idempotency key; batch update và ledger audit cùng một transaction.

## 4. Mô hình dữ liệu đích

| Bảng                                                 | Mục đích                                                               | Quy tắc audit                                                                                                           |
| ----------------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `freshcheck_kb_versions`                            | `kb_version`, status, checksum, source commit, stats và artifact JSON. | Bất biến sau sync; chỉ activate/retire theo workflow.                                                                 |
| `freshcheck_sources`, `freshcheck_claims`         | Evidence nguồn và claim của từng version.                             | Khóa theo `(kb_version, source_id/claim_id)`, không ghi đè lịch sử.                                              |
| `freshcheck_archetypes`, `freshcheck_ingredients` | Rubric/tier/protocol và shelf-life/alias theo version.                   | Khóa theo `(kb_version, id)`; trường phức hợp lưu JSONB.                                                         |
| `master_ingredient_freshcheck_mappings`             | Mapping catalog BE với FreshCheck ingredient của đúng KB version.     | Một mapping active cho mỗi `(master_ingredient_id, kb_version)`.                                                     |
| `freshcheck_assessments`                            | Lịch sử đánh giá một batch.                                         | Bất biến; unique `(user_id, batch_id, idempotency_key)`, lưu answers, outcome, claims, versions và applied expiry. |

`inventory_batches` và `inventory_ledger_entries` không bị thay thế. Assessment hợp lệ cập nhật `expires_at` và ghi `METADATA_UPDATED` zero-delta audit trong cùng transaction.

### 4.1. Foreign key và nullability bắt buộc

| Bảng/cột                                                                       | Constraint đề xuất                                            | Hành vi khi không có dữ liệu                                                 |
| -------------------------------------------------------------------------------- | ---------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `freshcheck_sources.kb_version`                                                | `NOT NULL` FK → `freshcheck_kb_versions.kb_version`         | Không sync source thiếu version.                                                |
| `freshcheck_claims.(kb_version, source_id)`                                    | Cả hai `NOT NULL`, composite FK → `freshcheck_sources`     | Không sync claim thiếu source hợp lệ.                                         |
| `freshcheck_archetypes.kb_version`                                             | `NOT NULL` FK → KB version                                    | Không sync archetype ngoài version.                                             |
| `freshcheck_ingredients.(kb_version, archetype_id)`                            | Cả hai `NOT NULL`, composite FK → `freshcheck_archetypes`  | Không sync ingredient thiếu archetype.                                          |
| `master_ingredient_freshcheck_mappings.master_ingredient_id`                   | `NOT NULL` FK → `master_ingredients.id`                     | Không có master ingredient thì không tạo mapping row.                        |
| `master_ingredient_freshcheck_mappings.(kb_version, freshcheck_ingredient_id)` | Cả hai `NOT NULL`, composite FK → `freshcheck_ingredients` | Không có KB ingredient/version hợp lệ thì không tạo mapping row.           |
| `freshcheck_assessments.user_id`                                               | `NOT NULL` FK → `users.id`                                  | Assessment chỉ tồn tại cho authenticated user.                                 |
| `freshcheck_assessments.inventory_batch_id`                                    | `NOT NULL` FK → `inventory_batches.id`                      | Batch không tồn tại/không thuộc user trả `404`, không insert assessment. |
| `freshcheck_assessments.(kb_version, freshcheck_ingredient_id)`                | Cả hai `NOT NULL`, composite FK → `freshcheck_ingredients` | Mapping unavailable trả `422`, không insert assessment.                       |

`master_ingredient_freshcheck_mappings` có unique `(master_ingredient_id, kb_version)`. `freshcheck_assessments` có unique `(user_id, inventory_batch_id, idempotency_key)` và các cột này đều `NOT NULL`. Quan hệ "batch thuộc user" phải được service kiểm tra trong query lock theo cả `id` và `user_id`; hai FK riêng lẻ không thể tự bảo vệ ownership chéo này.

### 4.2. API contract bắt buộc

| Endpoint                                                     | Request                                                                                                         | Thành công                                                                                                 | Lỗi bắt buộc                                                                                                                                                |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /api/freshness/questions?master_ingredient_id={uuid}` | Bearer token; UUID master ingredient.                                                                           | `200`: `kb_version`, `freshcheck_ingredient_id`, archetype và rubric questions/options/default.       | `401` chưa auth; `422 MAPPING_UNAVAILABLE` khi ingredient chưa map; `503 FRESHCHECK_KB_UNAVAILABLE` khi không có KB active.                          |
| `POST /api/freshness/batches/{batch_id}/assessment`        | Bearer token, `Idempotency-Key`, body gồm `answers`, optional `purchased_at`, optional `storage_mode`. | `200`: `assessment_id`, KB/rule version, score/tier, priority, claims, reasons, tips và `expires_at`. | `401` chưa auth; `404` batch không tồn tại/không thuộc user; `422` mapping hoặc dữ liệu storage/time không đủ; `503` không có KB active. |

Trong `POST`, storage và purchased time được lấy từ body trước, sau đó fallback sang batch. Nếu cả hai nguồn đều thiếu dữ liệu cần thiết thì trả `422` và **không lưu assessment**. Với manufacturer expiry, vẫn có thể lưu assessment cảm quan đã hoàn tất nhưng không được sửa `expires_at` hay `expiration_source`.

## 5. Rủi ro đã xác định

| Rủi ro                                                                                                                        | Mức độ   | Cách giảm thiểu                                                                                                                                                |
| ------------------------------------------------------------------------------------------------------------------------------ | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CreateInventoryBatchRequestDTO` hiện bắt buộc `expires_at`, khiến mọi lô mới bị xem là có hạn nhà sản xuất. | Cao         | Cho phép không gửi hạn dùng; chỉ đánh dấu `MANUFACTURER` khi người dùng thực sự cung cấp hạn in.                                                |
| Patch tìm ingredient bằng tên, trong khi catalog BE chưa có mã FreshCheck.                                               | Cao         | Tạo mapping rõ ràng, kiểm thử coverage và chặn ước tính số khi chưa map được.                                                                      |
| Patch ghi `expires_at` không có lock, idempotency hoặc metadata audit.                                                    | Cao         | Dùng transaction, row lock, ledger audit hiện có và bảng assessment bất biến.                                                                              |
| `SOFT_FREEZE` có trong KB nhưng chưa có trong enum storage của BE.                                                      | Trung bình | Release đầu chỉ hỗ trợ các mode BE đã có; trả kết quả không-ước-tính với mode không được map. Lập feature riêng nếu cần thêm mode mới. |
| KB bị overwrite khi sync hoặc app cache dùng version cũ.                                                                   | Cao         | Composite key theo version, checksum immutable, transaction activate và cache key theo `kb_version`.                                                           |

## 6. Dependency graph

```text
KB artifact đã build và kiểm định
        |
FreshCheck schema + sync/activate transaction
        |
Mapping catalog <---- Hợp đồng tạo lô không có hạn in
        |                         |
        +-----------+-------------+
                    |
       DB repository/cache + FreshCheck engine
                    |
       Questions API -> Assessment có lock/audit
                    |
      expiry/notification/recommendation regression
```

## 7. Task list

### Phase 0 — Import catalog normalized

## Task 0.1: Hardening importer catalog trước khi chạy release

**Description:** Giữ `data123/normalized` nguyên vẹn, nhưng bổ sung kiểm soát target database rõ ràng cho `src/backend/scripts/import_data.py`. Importer phải validate toàn bộ bốn JSON trước mọi write, hỗ trợ dry-run và chỉ đọc URL từ biến môi trường được chọn tường minh để test không vô tình chạm application database.

**Acceptance criteria:**

- [ ] Importer giữ nguyên contract 4 file normalized và không ghi vào input directory.
- [ ] Import dùng `DATABASE_URL` cấu hình cho môi trường Neon được chọn.
- [ ] Dry-run validate toàn bộ catalog và rollback transaction, không để lại dữ liệu.

**Verification:**

- [ ] `uv run python scripts/import_data.py --dry-run` pass từ `src/backend` với input mặc định.
- [ ] Unit tests cover missing file, unexpected field, invalid UUID/enum và foreign key catalog không hợp lệ.
- [ ] Database test chứng minh dry-run không thay đổi row count.

**Dependencies:** None
**Files likely touched:** `src/backend/scripts/import_data.py`, import-data tests, backend runbook
**Estimated scope:** M

## Task 0.2: Import catalog release theo transaction và chứng minh idempotency

**Description:** Chạy importer đã harden trên disposable database sau Alembic head. Import theo dependency hiện hữu: categories, master ingredients, recipes, recipe ingredients. Lưu report số lượng và chạy lại cùng input để chứng minh UUID-based upsert không tạo bản ghi trùng.

**Acceptance criteria:**

- [ ] `master_ingredients` được tạo từ `master_ingredients.json` với UUID/source name ổn định.
- [ ] Import lỗi rollback toàn bộ release, không để catalog bán phần.
- [ ] Import cùng release lần hai giữ nguyên số row và quan hệ recipe ingredient.

**Verification:**

- [ ] `alembic upgrade head` và import chạy trên `DATABASE_URL` của Neon environment được chọn.
- [ ] Chạy import hai lần, so sánh count/checksum logical của 4 catalog tables.
- [ ] Existing catalog API/seed regression tests pass.

**Dependencies:** Task 0.1
**Files likely touched:** import-data tests, release evidence/runbook; không sửa JSON normalized
**Estimated scope:** S

### Checkpoint: Catalog import

- [ ] Catalog normalized được import thành công, rollback được và lặp lại an toàn.
- [ ] `master_ingredients.id` là khóa ổn định dùng cho mapping; không có FreshCheck mapping nào được tạo trong phase này.

### Phase 1 — Data contract và tương thích inventory

## Task 1: Đóng gói và kiểm định bản phát hành FreshCheck KB

**Description:** Chuẩn hóa `data_freshness` thành đầu vào phát hành có thể lặp lại: build artifact, chạy invariant test, ghi nhận `kb_version`, source commit và SHA-256. Artifact là input duy nhất của sync; không copy thành file runtime trong backend.

**Acceptance criteria:**

- [X] `freshcheck_kb.json` build thành công, có `kb_version`, 8 archetype, ingredient/claim/source statistics hợp lệ.
- [X] Invariant test chạy trong môi trường được khai báo và không dùng dữ liệu/môi trường production.
- [X] Artifact dùng cho sync được truy vết tới commit KB và checksum/version trong release note.

**Verification:**

- [X] Chạy `python scripts/build_kb.py` từ `data_freshness` trong môi trường dev đã khai báo.
- [X] Chạy `python -m pytest -q tests` từ `data_freshness`.
- [X] Kiểm tra JSON artifact với schema và ghi nhận `kb_version`.

**Dependencies:** None
**Files likely touched:** `data_freshness/scripts/build_kb.py`, dependency manifest của `data_freshness`, `data_freshness/tests/test_kb_invariants.py`, release documentation
**Estimated scope:** M

## Task 2: Thêm schema FreshCheck versioned qua Alembic

**Description:** Tạo migration/model cho `freshcheck_kb_versions`, sources, claims, archetypes và ingredients. Các record được scoped bằng `kb_version`; artifact JSON và checksum được lưu để audit hoặc rollback mà không ghi đè lịch sử.

**Acceptance criteria:**

- [X] Có composite key/foreign key bảo vệ scope `kb_version` cho KB data.
- [X] Chỉ một KB ở trạng thái `ACTIVE`; historical version không bị runtime service sửa hoặc xóa.
- [X] Database lưu được checksum, source commit, stats và artifact JSON của release.

**Verification:**

- [ ] Migration upgrade/downgrade chạy trên `DATABASE_URL` của Neon environment được chọn.
- [X] Model metadata tests xác nhận composite key/foreign key, `NOT NULL` và partial unique index bảo vệ duplicate version item, missing version và hai active versions.
- [X] Alembic SQL offline xác nhận index/constraint phục vụ lookup KB active.

**Dependencies:** Task 1
**Files likely touched:** Alembic revision mới, FreshCheck model files, model/schema tests
**Estimated scope:** M

## Task 3: Đồng bộ và activate KB bằng transaction có audit

**Description:** Tạo `src/backend/scripts/sync_freshcheck_kb.py` dùng SQLAlchemy/asyncpg của backend, nhận artifact JSON qua `--artifact` và target qua `--database-url-env`. Tool load vào schema Alembic trong một transaction, stage version, kiểm checksum/idempotency và chỉ activate theo lệnh rõ ràng. Script DDL trực tiếp trong `data_freshness/scripts/sync_to_postgres.py` không được dùng để ghi database.

**Acceptance criteria:**

- [X] Command hỗ trợ `--dry-run`, `--stage` và `--activate`; không in database credential.
- [X] Cùng version/cùng checksum sync idempotent; cùng version/khác checksum bị từ chối.
- [X] Activate retire KB active cũ, lưu thời điểm/actor và không tạo hai active versions.
- [X] Sync lỗi rollback toàn bộ; app không đọc KB dở dang.

**Verification:**

- [ ] Integration test import artifact thật vào database disposable và chạy lại lần hai.
- [X] Unit test/mock kiểm tra version collision, claim/source sai và dry-run không tạo database engine.
- [ ] Manual activation/rollback xác nhận version active thay đổi đúng.

**Dependencies:** Tasks 1–2
**Files likely touched:** `src/backend/scripts/sync_freshcheck_kb.py`, FreshCheck persistence service, sync tests, hướng dẫn deprecate direct-DDL script
**Estimated scope:** M

### Checkpoint: Sau Tasks 1–3

- [ ] Artifact đã kiểm định được lưu versioned, truy vết và activate trong PostgreSQL.
- [ ] Không có DDL ad-hoc trong sync script; chỉ Alembic quản lý schema.
- [ ] Review với owner trước khi tiếp tục mapping và API.

### Phase 2 — Mapping, inventory contract và runtime engine

## Task 4: Map catalog BE sang FreshCheck ingredient

**Description:** Tạo bảng mapping versioned, manifest YAML đã review, candidate-report script và seed script idempotent. `master_ingredients.json` không bị normalize lại hoặc thêm field; mapping nối UUID catalog đã import với FreshCheck ID của KB active.

**Acceptance criteria:**

- [ ] `data_freshness/mappings/master_ingredient_freshcheck_mappings.yaml` tuân thủ contract ở §0.3, không có ID/null/duplicate.
- [ ] `build_freshcheck_mapping_candidates.py` chỉ đề xuất `EXACT_CODE`/`EXACT_NAME`; ambiguous và unmatched không tự được seed.
- [ ] `seed_freshcheck_mappings.py` validate FK, chạy lại idempotent và xuất coverage report `mapped/unmapped/ambiguous`.

**Verification:**

- [ ] Unit test migration/import pass mà không cần database test riêng.
- [ ] Test từ chối UUID master không tồn tại, FreshCheck ID/version không tồn tại, null và mapping trùng.
- [ ] Xuất coverage report cho catalog active trước khi enable API production.

**Dependencies:** Tasks 0.2, 2–3
**Files likely touched:** mapping model + Alembic revision, `data_freshness/mappings/master_ingredient_freshcheck_mappings.yaml`, candidate/seed scripts, mapping tests
**Estimated scope:** M

## Task 5: Mở luồng tạo lô không có hạn in sẵn

**Description:** Điều chỉnh contract inventory để `expires_at` là optional khi người dùng không có hạn nhà sản xuất. Nếu hạn in được gửi, hành vi `MANUFACTURER` giữ nguyên; nếu không, dùng legacy shelf-life estimate khi có rule hoặc `UNKNOWN` để FreshCheck đánh giá sau.

**Acceptance criteria:**

- [X] Gửi `expires_at` vẫn tạo batch với `expiration_source=MANUFACTURER`.
- [X] Không gửi `expires_at` không lỗi validation và không bị gắn nhầm `MANUFACTURER`.
- [X] Shopping purchase dùng cùng contract.

**Verification:**

- [X] DTO/service tests bao phủ manufacturer, legacy estimate và unknown expiry.
- [X] API contract regression xác nhận client cũ vẫn tương thích.
- [ ] Unit tests pass mà không cần database integration test.

**Dependencies:** None
**Files likely touched:** inventory DTO/service và inventory/shopping tests
**Estimated scope:** M

## Task 6: Tạo repository PostgreSQL, cache versioned và pure engine

**Description:** Chuyển engine trong patch thành pure inference logic nhận KB từ repository PostgreSQL. Repository tải KB active, cache theo `kb_version` và không đọc `FRESHCHECK_KB_PATH` khi phục vụ API.

**Acceptance criteria:**

- [X] Engine có kết quả theo rule KB nhưng không phụ thuộc local file path.
- [X] Không có KB active thì chỉ FreshCheck trả lỗi domain/`503`; inventory lõi vẫn hoạt động.
- [X] Kết quả luôn mang KB/rule version đã dùng.

**Verification:**

- [X] Unit tests cho manufacturer expiry, tier 1–4, hard-stop, storage/ingredient unknown và timezone-aware timestamps.
- [X] Unit test xác nhận active-version change dùng đúng cache version tiếp theo.
- [X] FreshCheck unit tests pass.

**Owner decision (2026-10-16):** Không dùng database target riêng hay database integration test. Với Task 6, unit tests là gate xác minh bắt buộc; không chặn bàn giao bởi lint/typecheck toàn repository ngoài phạm vi thay đổi.

**Dependencies:** Tasks 2–4
**Files likely touched:** `src/backend/src/service/freshcheck_engine.py`, repository/cache service, FreshCheck unit/integration tests
**Estimated scope:** M

### Checkpoint: Sau Tasks 4–6

- [ ] KB active trong PostgreSQL có mapping coverage được owner duyệt.
- [ ] Lô tươi không có hạn in được tạo an toàn để sẵn sàng assessment.
- [ ] Engine đọc KB active từ database và có handling rõ ràng khi chưa activate KB.

### Phase 3 — FreshCheck API và assessment persistence

## Task 7: Cung cấp API câu hỏi cảm quan có xác thực

**Description:** Áp dụng DTO/dependency/router từ patch cho `GET /api/freshness/questions?master_ingredient_id=...`. Endpoint lookup qua mapping của KB active, trả rubric tiếng Việt, chỉ đọc dữ liệu và không dựa vào so khớp tên tự do.

**Acceptance criteria:**

- [ ] Endpoint yêu cầu bearer token và trả questions/options/default của KB active.
- [ ] Master ingredient không map được trả trạng thái rõ ràng, không tạo estimate giả.
- [ ] OpenAPI phản ánh validation và KB version trả về.

**Verification:**

- [X] Route tests cover 401, valid mapping, unmapped ingredient và invalid query.
- [X] OpenAPI contract test xác nhận route có BearerAuth.
- [X] App factory regression xác nhận router FreshCheck được đăng ký.

**Dependencies:** Tasks 4, 6
**Files likely touched:** freshness DTO/dependency/router, `src/backend/src/app.py`, route tests
**Estimated scope:** M

## Task 8: Lưu assessment bất biến và cập nhật expiry có audit

**Description:** Tạo migration/model `freshcheck_assessments` và hoàn thiện `POST /api/freshness/batches/{batch_id}/assessment`. Trong một transaction: lock batch theo owner, resolve mapping/KB active, infer, persist assessment, update expiry hợp lệ và thêm zero-delta `METADATA_UPDATED` ledger audit.

**Acceptance criteria:**

- [X] Cùng `Idempotency-Key` trả assessment đã lưu, không ghi assessment/audit/expiry lần hai.
- [X] Assessment lưu answers, outcome, claims, KB/rule version, timestamp và expiry applied.
- [X] Hạn manufacturer không bị ghi đè; hard-stop không tự động discard quantity.

**Verification:**

- [X] Service tests cover ownership, lock, retry, manufacturer precedence, hard-stop và mapping unknown.
- [X] Unit test transaction seam xác nhận assessment, batch update và ledger cùng nằm trong một transaction; không chạy database integration theo owner decision Task 6.
- [X] Route tests cover auth, request validation và mandatory `Idempotency-Key`.

**Dependencies:** Tasks 5–7
**Files likely touched:** assessment model + Alembic revision, freshness service/DTO/router, inventory audit helper, FreshCheck tests
**Estimated scope:** M

**Owner decision (2026-10-16):** Unit tests là gate xác minh của Task 8; không cấu hình hoặc chạy database integration test riêng.

### Checkpoint: Sau Tasks 7–8

- [ ] User nhận rubric từ mapped master ingredient và assessment được ghi bất biến.
- [ ] Manufacturer precedence, retry, owner isolation và audit transaction có bằng chứng kiểm thử.

### Phase 4 — Downstream và vận hành

## Task 9: Kiểm chứng downstream, CI và rollout/rollback KB

**Description:** Chứng minh expiry FreshCheck đi vào notification và AI recommendation hiện hữu. Hoàn thiện CI/runbook cho build, sync, activate, migration, backup và rollback KB. `fridge_report.py` chỉ chạy hậu kiểm trên dữ liệu test hoặc đã ẩn danh.

**Acceptance criteria:**

- [X] Notification scan phân loại batch theo expiry mới mà không tạo duplicate.
- [X] Payload AI nhận `hours_to_expire` đúng với expiry đã lưu; FEFO/quantity không đổi ngoài logic hiện hữu.
- [X] CI chặn artifact/sync/migration invalid và có hướng dẫn rollback về KB version trước.

**Verification:**

- [X] Focused freshness, notification và recommendation regression tests pass.
- [X] Artifact dry-run không mở database; unit tests xác minh activate/rollback atomic theo owner decision không dùng database integration riêng.
- [X] Ruff/format và strict mypy pass trên production files Task 9; không chặn bàn giao bởi lỗi type/format toàn repository ngoài phạm vi thay đổi.

**Dependencies:** Tasks 1–8
**Files likely touched:** notification/recommendation tests, CI workflow, `src/backend/README.md` hoặc `COOKBOOK.md`, `.env.example`, runbook
**Estimated scope:** M

**Owner decision (2026-10-16):** CI và bàn giao Task 9 dùng artifact validation, migration-graph check, focused unit regressions và targeted production quality checks; không cấu hình database integration riêng hoặc sửa type/format debt ngoài phạm vi.

### Checkpoint: Hoàn tất

- [X] PostgreSQL là runtime source duy nhất; YAML/JSON chỉ là source/artifact có traceability.
- [X] KB và assessment history đều truy vết được theo version, checksum và audit.
- [X] Chỉ ingredient đã map mới có estimate dạng số; item khác nhận guidance kiểm tra trực tiếp.
- [ ] Toàn bộ task acceptance criteria có bằng chứng kiểm thử và owner phê duyệt rollout.

## 8. Runbook thực thi cho AI agent

Các lệnh dưới đây là target contract. Lệnh có option `--database-url-env` chỉ tồn tại sau khi Task 0.1/Task 3 hoàn thành. Không đưa URL, password hoặc token vào log/commit.

### Bước A — Import catalog normalized

Trước bước này, cấu hình process phải trỏ **rõ ràng** tới database disposable; tuyệt đối không tái sử dụng application database chỉ vì biến `DATABASE_URL` đang có sẵn.

1. Chạy `uv run alembic upgrade head` trên database disposable.
2. Chạy `uv run python scripts/import_data.py --dry-run` từ `src/backend`.
3. Nếu validation pass, chạy cùng command không có `--dry-run` trên database disposable.
4. Chạy lại lần hai, kiểm tra count các bảng categories/master ingredients/recipes/recipe ingredients không tăng.

**Dừng ngay** nếu bất kỳ file normalized nào vi phạm contract hoặc import không atomic. Không sửa JSON để “cho qua”; sửa pipeline/source release trước.

### Bước B — Build, sync và activate FreshCheck KB

1. Từ `data_freshness`, chạy `python scripts/build_kb.py` rồi `python -m pytest -q tests`.
2. Từ `src/backend`, chạy `uv run python -m scripts.sync_freshcheck_kb --artifact ../../data_freshness/build/freshcheck_kb.json --database-url-env DATABASE_URL --dry-run`.
3. Stage artifact đã kiểm định, xác minh version/checksum/stats, rồi activate bằng command riêng.
4. Xác minh database chỉ có một KB `ACTIVE`; record của version cũ vẫn tồn tại để rollback.

**Dừng ngay** nếu checksum version collision, claim/source/archetype không hợp lệ, hoặc sync cần chạy DDL thủ công.

### Bước C — Tạo và seed mapping đã review

1. Chạy `uv run python scripts/build_freshcheck_mapping_candidates.py --database-url-env DATABASE_URL --kb-version <version> --output /tmp/freshcheck-mapping-report.json`.
2. Chỉ đưa các mapping đã review vào `data_freshness/mappings/master_ingredient_freshcheck_mappings.yaml`; dùng `EXACT_CODE`, `EXACT_NAME` hoặc `MANUAL_REVIEW` làm `match_method`.
3. Chạy `uv run python scripts/seed_freshcheck_mappings.py --manifest ../../data_freshness/mappings/master_ingredient_freshcheck_mappings.yaml --database-url-env DATABASE_URL`.
4. Review coverage report. Unmapped/ambiguous item không được tự seed hoặc làm API trả estimate số.

### Bước D — Triển khai và kiểm chứng FreshCheck

1. Hoàn thành repository/engine, sau đó endpoint questions, rồi endpoint assessment theo Task 6–8.
2. Chạy focused tests của mỗi task trước khi chuyển task kế tiếp.
3. Thử nghiệm tối thiểu: lô mapped không có hạn in; lô có manufacturer expiry; hard-stop; unmapped master ingredient; batch của user khác; retry cùng `Idempotency-Key`.
4. Chỉ sau các test trên mới chạy notification/recommendation regression và chuẩn bị rollout.

### Bước E — Rollout và rollback

1. Backup/ghi nhận active `kb_version`, checksum và migration revision trước deploy.
2. Apply migration, sync/stage artifact mới, chạy smoke tests, rồi activate KB.
3. Nếu lỗi rule/data: activate lại KB version trước; không rollback dữ liệu assessment lịch sử.
4. Nếu lỗi schema/app: dùng Alembic rollback theo runbook; không chạy destructive SQL thủ công.

## 9. Thứ tự thực hiện và khả năng song song

`Task 0.1` phải hoàn tất trước `Task 0.2`; catalog import checkpoint phải pass trước mapping. `Task 1` hoàn tất trước `Task 2`; `Task 5` có thể chạy song song với Tasks 1–4. Tasks 2, 3 và 4 là chuỗi migration/data phụ thuộc nên không triển khai song song. Task 6 cần KB active và mapping; Task 7 chờ Task 6; Task 8 chờ Tasks 5–7. Tài liệu CI/runbook của Task 9 có thể soạn sớm, nhưng chỉ hoàn tất sau khi sync/activate và API contract ổn định.

## 10. Câu hỏi cần owner chốt trước khi code

1. Coverage mapping tối thiểu để enable production là chỉ nhóm P0 hay toàn bộ master ingredient active?
2. Ai/role nào được quyền sync hoặc activate một KB version trong production, và approval có cần tách hai người không?
3. Hard-stop chỉ đánh dấu expired và khuyến nghị bỏ như đề xuất, hay cần workflow xác nhận discard riêng ở frontend?
4. Assessment/audit cần lưu vĩnh viễn hay có retention policy theo yêu cầu pháp lý/sản phẩm?

## 11. Definition of Done

- FreshCheck là module backend được auth, typed, documented và có OpenAPI contract.
- Mọi update expiry có owner check, transaction, idempotency và audit trace.
- Không có assessment nào ghi đè hạn nhà sản xuất hoặc tự động trừ inventory.
- KB release immutable, idempotent khi sync, có version/checksum/source commit và rollback path.
- End-to-end flow pass: master ingredient imported → mapping đã review → batch không có hạn in → questions → assessment persisted → expiry/audit idempotent.
- Focused tests, `ruff`, formatter, strict `mypy` và disposable-DB integration tests pass trước khi merge.
