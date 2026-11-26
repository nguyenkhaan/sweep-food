# Implementation Plan: Hướng 3 — Cá nhân hoá dinh dưỡng (Phạm vi FE + BE)

> **Trạng thái:** Sẵn sàng review & triển khai  
> **Phạm vi thực hiện:** Frontend (`src/frontend/`) & Backend (`src/backend/src/`), cập nhật hợp đồng (`docs/api-contract.md`).  
> **Ngoài phạm vi (teammate Gia Huy phụ trách):** AI Engine (`src/backend/AI/recommendation/*` — các đầu việc 3.2, 3.3, phần tính `fit_reasons` của 3.5, và bộ test 3.9).  
> **Skills áp dụng:** `planning-and-task-breakdown`, `sweepfood-flutter-feature`, `sweepfood-design-system`, quy chuẩn Python strict (`src/backend/AGENT.md`).

---

## 1. Overview

Người dùng khai báo **Hồ sơ ăn uống** một lần (số người ăn, chế độ ăn, tình trạng sức khoẻ, dị ứng, nguyên liệu không ăn) và lưu bền vững vào trường JSONB `users.preferences` đã có sẵn trên PostgreSQL (không cần migration). Backend sẽ tự đọc hồ sơ này từ database khi xử lý `POST /recommendations` để điền đầy đủ tham số sang AI Engine (không phụ thuộc payload lỗi cũ từ FE) và nối tiếp trường `fit_reasons` trả về từ engine lên FE. Frontend sửa triệt để lỗi map sai `"Nhiều rau" -> "vegetarian"`, bổ sung tùy chọn `"Ăn chay"` ở Onboarding (đồng bộ lên BE), xây màn **"Hồ sơ ăn uống"** đầy đủ trong Cài đặt, hiển thị `fit_reasons` trên thẻ món & chi tiết điểm, xử lý trạng thái rỗng sau lọc, và luôn gắn khuyến cáo *"Gợi ý tham khảo, không thay lời khuyên của bác sĩ"*.

---

## 2. Architecture Decisions

| # | Quyết định | Chi tiết & Lý do |
|---|---|---|
| AD-1 | **Lưu hồ sơ trong `users.preferences` (JSONB), không migration** | Cột `UserModel.preferences` đã có sẵn kiểu `JSONB` với default `{}`. Chuẩn hoá bộ key cố định: `household_size`, `diet`, `health_conditions`, `allergies`, `disliked_ingredients`. |
| AD-2 | **`PATCH /users/profile` dùng shallow-merge + strict validation** | `UserService.update_profile` hiện đang ghi đè toàn bộ dict `user.preferences`, làm mất các key khác (`locale`, `avatar_url`, `onboarding_completed`). Đổi sang shallow-merge (tạo dict mới để SQLAlchemy track thay đổi JSONB chắc chắn) và validate chặt 5 key dinh dưỡng (trả `422` khi vi phạm), vẫn giữ nguyên các key hợp lệ khác. |
| AD-3 | **BE là nguồn sự thật (authoritative) cho hồ sơ khi gọi AI Engine** | `RecommendationAIService.recommend()` tự truy vấn `UserModel.preferences` theo `user_id` của JWT, dựng request gửi `RecommendationEngine.recommend(...)`. FE không còn tự quyết định `dietary_restrictions` hay `scenario_type` sức khoẻ. |
| AD-4 | **Hợp đồng biên giới BE ↔ AI Engine tương thích song song** | Để FE + BE triển khai độc lập không bị block bởi nhánh AI của Gia Huy: (1) BE gửi đồng thời `scenario_types: list[str]` (gộp `"an_chay"` nếu `diet == "vegetarian"` + `health_conditions`), `scenario_type` (tương thích ngược: phần tử đầu của `scenario_types` hoặc `"custom"`), `diet`, `household_size`, `allergies`, `disliked_ingredients`; (2) BE đọc `fit_reasons` từ `EngineRecommendation` qua helper có fallback `[]` cho đến khi nhánh AI thêm field chính thức. |
| AD-5 | **Tách Onboarding gọn & màn Hồ sơ ăn uống đầy đủ trong Cài đặt** | Onboarding (`DietaryPreferenceScreen`) giữ nhẹ nhàng với 5 lựa chọn chế độ ăn (thêm `Ăn chay`) + đồng bộ `PATCH /users/profile` (fallback lưu local nếu offline). Cài đặt có màn riêng `NutritionProfileScreen` dùng lại cùng widget chọn chế độ ăn và bổ sung đủ 5 trường. |
| AD-6 | **Tương thích ngược `dietary_preference` cũ** | Khi đọc `users.preferences` (cả BE & FE): ưu tiên key `diet`; nếu chưa có thì fallback đọc key cũ `dietary_preference` (lowercase) để không mất dữ liệu người dùng cũ. |
| AD-7 | **Mock parity & Design System trên FE** | Cập nhật `assets/mock/recommendations.json` có `fit_reasons` để `BACKEND=mock` vẫn chạy đủ UI. Mọi UI dùng token từ `context.colors`, `context.sweep`, `Gap`, `Radii`, `context.l10n`, đảm bảo Light/Dark parity và `kMinTapTarget >= 48dp`. |

---

## 3. Contract đề xuất (BE ↔ FE ↔ AI Engine)

### 3.1. `users.preferences` (các key hồ sơ ăn uống)

```json
{
  "household_size": 2,
  "diet": "balanced",
  "health_conditions": ["nguoi_cao_huyet_ap", "nguoi_tieu_duong"],
  "allergies": ["shellfish", "peanut"],
  "disliked_ingredients": ["rau mùi"]
}
```

- `household_size`: `int`, phạm vi `1..10`, mặc định `4` nếu chưa thiết lập.
- `diet`: `"balanced" | "high_protein" | "low_calorie" | "more_veg" | "vegetarian"` (mặc định `"balanced"`).
- `health_conditions`: danh sách không trùng thuộc `{"nguoi_tieu_duong", "nguoi_cao_huyet_ap", "nguoi_benh_gout", "nguoi_dau_da_day", "an_kieng_keto_lowcarb"}` (khớp trực tiếp `scenario_rules.py`).
- `allergies`: danh sách không trùng thuộc `{"shellfish", "fish", "peanut", "egg", "dairy", "soy", "gluten", "sesame"}` (8 nhóm trong spec — cần xác nhận lại nếu Gia Huy đổi tên mã nào, vd `dairy` vs `milk`).
- `disliked_ingredients`: `list[str]`, tối đa 50 phần tử, mỗi chuỗi trim không rỗng tối đa 100 ký tự, loại trùng không phân biệt hoa/thường.

### 3.2. `POST /recommendations` & biên giới BE → AI Engine

- **FE gửi lên BE**: chỉ cần gửi `items` (các trường `household_size`, `scenario_type`, `dietary_restrictions`, `allergies`, `disliked_ingredients`, `preferred_cuisines` giữ optional/default trên DTO để tương thích ngược, nhưng BE sẽ ghi đè phần hồ sơ từ `users.preferences`).
- **BE điền vào request chuyển cho `RecommendationEngine.recommend(...)`**:
  - `household_size`: từ `preferences.household_size` (fallback `4`).
  - `diet`: từ `preferences.diet` (fallback `"balanced"`).
  - `scenario_types`: `(["an_chay"] if diet == "vegetarian" else []) + health_conditions` (giữ thứ tự, không trùng).
  - `scenario_type`: `scenario_types[0]` nếu không rỗng, ngược lại `"custom"` (đảm bảo engine hiện tại chạy được ngay cho kịch bản đơn trước khi Gia Huy merge 3.2).
  - `dietary_restrictions`: `[diet]` (tương thích ngược với các chỗ đọc cũ).
  - `allergies`: từ `preferences.allergies`.
  - `disliked_ingredients`: từ `preferences.disliked_ingredients`.
- **Response `POST /recommendations`**:
  - Mỗi phần tử trong `items[]` có thêm `"fit_reasons": list[str]` (ví dụ: `["Ít muối, hợp người cao huyết áp", "≈ 420 kcal/suất · 28 g đạm", "Không có tôm"]`).
  - Khi `ai_response.status == "empty"` và `body.items` không rỗng: `analysis.summary` phản ánh `ai_response.message` và `warnings` có mã `"NO_MATCH_AFTER_FILTERS"` để FE hiển thị đúng thông báo gợi ý thêm nguyên liệu / xem lại hồ sơ.

---

## 4. Dependency Graph

```text
Task 1: Chốt docs/api-contract.md (BE ↔ FE ↔ AI)
   │
   ├──► Task 2: BE User preferences merge + validation (PATCH /users/profile)
   │        │
   │        └──► Task 3: BE RecommendationAIService đọc hồ sơ + nối fit_reasons
   │                 │
   │                 └──► [Checkpoint 1: BE & Contract Gate]
   │
   └──► Task 4: FE NutritionProfile domain + DietaryPreference.vegetarian + User/Session + l10n
            │
            ├──► Task 5: FE sửa SuggestionRequest (3.7) + nối fit_reasons DTO/Entity/Mock
            │        │
            │        └──► [Checkpoint 2: FE Domain & Data Gate]
            │                 │
            │                 ├──► Task 8: FE hiển thị fit_reasons trên Card & Breakdown + disclaimer
            │                 │
            │                 └──► Task 9: FE empty-after-filter UX + full E2E verification
            │
            └──► Task 6: FE Onboarding 5 chế độ ăn + sync PATCH /users/profile + widget dùng chung
                     │
                     └──► Task 7: FE màn "Hồ sơ ăn uống" trong Cài đặt + auto-refresh gợi ý
                              │
                              └──► [Checkpoint 3: Nutrition Profile Flow]
```

*Khả năng song song:* Sau khi xong **Task 1**, nhánh BE (**Task 2 → 3**) và nhánh FE domain (**Task 4 → 5/6**) có thể chạy song song hoàn toàn mà không chờ nhánh AI của Gia Huy.

---

## 5. Detailed Task Breakdown

### Phase 1: Contract & Backend Foundation

#### Task 1: Chốt API Contract cho Hồ sơ ăn uống & Recommendations (3.1)

**Description:** Cập nhật `docs/api-contract.md` để chốt cấu trúc JSON `users.preferences`, cơ chế shallow-merge của `PATCH /users/profile`, hợp đồng `POST /recommendations` (BE tự đọc hồ sơ + `fit_reasons` + warning khi lọc rỗng), và bảng mã chuẩn (`diet`, `health_conditions`, `allergies`) làm nguồn sự thật chung giữa FE, BE và AI Engine.

**Acceptance criteria:**
- [ ] Mục 12 (`GET/PATCH /users/profile`) mô tả rõ schema 5 trường hồ sơ ăn uống, quy tắc validate (422), và hành vi shallow-merge giữ nguyên các key khác.
- [ ] Mục 3 (`POST /recommendations`) mô tả rõ BE tự đọc `users.preferences` để điền `scenario_types`, `diet`, `household_size`, `allergies`, `disliked_ingredients` gửi AI engine; response có `fit_reasons: string[]` và warning `NO_MATCH_AFTER_FILTERS`.
- [ ] Ghi rõ bảng mã wire cố định cho `diet` (5), `health_conditions` (5), `allergies` (8) và gửi Gia Huy đối chiếu.

**Verification:**
- [ ] Manual check: đối chiếu toàn bộ tên trường & enum với [scenario_rules.py](file:///c:/Projects/sweep-food/src/backend/AI/recommendation/scenario_rules.py) và spec Hướng 3.

**Dependencies:** None

**Files likely touched:**
- `docs/api-contract.md`

**Estimated scope:** Small (1 file)

---

#### Task 2: BE — Validate hồ sơ ăn uống & shallow-merge ở `PATCH /users/profile`

**Description:** Chuẩn hoá validation cho các key hồ sơ ăn uống trong `user_dto.py` và sửa `UserService.update_profile` sang shallow-merge thay vì ghi đè toàn bộ dict `user.preferences`, giúp FE cập nhật từng phần (vd chỉ đổi `diet` lúc Onboarding hoặc lưu cả 5 mục trong Cài đặt) mà không xoá mất `locale`, `avatar_url`, `onboarding_completed`.

**Acceptance criteria:**
- [ ] Gửi `household_size` ngoài `1..10`, hoặc `diet` / `health_conditions` / `allergies` ngoài tập mã hợp lệ trả về `422` theo error envelope chung.
- [ ] `disliked_ingredients` tự trim, bỏ chuỗi rỗng, loại trùng case-insensitive, và giới hạn hợp lý (tối đa 50 mục, ≤ 100 ký tự/mục).
- [ ] `PATCH /users/profile` với `{"preferences": {"diet": "vegetarian"}}` giữ nguyên các key cũ (`locale`, `onboarding_completed`, `allergies`, ...) và tạo dict mới gán lại cho `user.preferences` để PostgreSQL JSONB commit chắc chắn.

**Verification:**
- [ ] Tests pass: `cd src/backend && pytest src/test/test_user_service.py src/test/test_user_router.py`
- [ ] Linters pass: `cd src/backend && ruff check src/module/user src/test/test_user_*.py && mypy --strict src/module/user`

**Dependencies:** Task 1

**Files likely touched:**
- `src/backend/src/module/user/user_dto.py`
- `src/backend/src/module/user/user_service.py`
- `src/backend/src/test/test_user_service.py`
- `src/backend/src/test/test_user_router.py`

**Estimated scope:** Medium (4 files)

---

#### Task 3: BE — Tự đọc hồ sơ người dùng trong `RecommendationAIService` & nối `fit_reasons` (3.4 + 3.5 BE)

**Description:** Nối `RecommendationAIService.recommend()` với `UserModel.preferences` của user đang đăng nhập để BE tự xây request hoàn chỉnh chuyển cho `RecommendationEngine`, không tin tưởng chế độ ăn/dị ứng do FE gửi lên. Đồng thời mở rộng `RecommendationItemDTO` thêm `fit_reasons` (đọc an toàn từ kết quả engine) và gắn warning/summary rõ ràng khi engine trả `status == "empty"` do bộ lọc cứng.

**Acceptance criteria:**
- [ ] `RecommendationAIService` truy vấn `UserModel.preferences` của `_user_id` và điền `household_size`, `diet`, `scenario_types`, `scenario_type`, `dietary_restrictions`, `allergies`, `disliked_ingredients` vào request truyền cho `self._engine.recommend(...)`, ghi đè giá trị từ FE.
- [ ] User có `diet == "vegetarian"` luôn được map thêm `"an_chay"` vào `scenario_types` (và `scenario_type` tương thích ngược), đảm bảo gọi API thực tế không trả món có thịt ngay cả với engine hiện tại.
- [ ] `RecommendationItemDTO` trả kèm `fit_reasons: list[str]` lấy từ `EngineRecommendation` (mặc định `[]` nếu nhánh AI chưa bổ sung field), và khi `ai_response.status == "empty"` với kho không rỗng thì response có warning `"NO_MATCH_AFTER_FILTERS"` cùng `analysis.summary = ai_response.message`.

**Verification:**
- [ ] Tests pass: `cd src/backend && pytest src/test/test_recommendation_ai_service.py src/test/test_recommendation_router.py`
- [ ] Linters pass: `cd src/backend && ruff check src/module/recommendations src/test/test_recommendation_*.py && ruff format --check src/module/recommendations && mypy --strict src/module/recommendations && pylint src/module/recommendations`

**Dependencies:** Task 1, Task 2

**Files likely touched:**
- `src/backend/src/module/recommendations/recommendation_dto.py`
- `src/backend/src/module/recommendations/recommendation_ai_service.py`
- `src/backend/src/test/test_recommendation_ai_service.py`
- `src/backend/src/test/test_recommendation_router.py`

**Estimated scope:** Medium (4 files)

---

### Checkpoint 1: Backend & Contract Gate (Sau Tasks 1–3)
- [ ] `docs/api-contract.md` đã khớp với code BE và gửi Gia Huy xác nhận mã `allergies` / `health_conditions` / `scenario_types`.
- [ ] Toàn bộ `pytest src/test/test_user_*.py src/test/test_recommendation_*.py` pass.
- [ ] `ruff check`, `ruff format --check`, `mypy --strict`, `pylint` đều 0 lỗi trên các module đã sửa.
- [ ] Review nhanh với người dùng trước khi chuyển sang phần FE.

---

### Phase 2: Frontend Domain & Data Layer

#### Task 4: FE — Domain `NutritionProfile`, thêm `DietaryPreference.vegetarian`, nối `User`/`Session` & l10n

**Description:** Xây tầng domain bất biến (Freezed) cho hồ sơ ăn uống và cập nhật `DietaryPreference` thêm `vegetarian`, tạo enum `HealthCondition` (5 mục) & `AllergyGroup` (8 nhóm), gắn `NutritionProfile` vào `User` + `UserProfileDto` + cache của `SessionController`, đồng thời khai báo đầy đủ khóa l10n (`app_vi.arb`, `app_en.arb`) bao gồm câu khuyến cáo y tế bắt buộc.

**Acceptance criteria:**
- [ ] `DietaryPreference` có đủ 5 giá trị (`balanced`, `highProtein`, `lowCalorie`, `moreVeg`, `vegetarian`) kèm `label`/`description` song ngữ VI/EN.
- [ ] `NutritionProfile` (`@freezed`) parse chính xác từ `Map<String, dynamic>` của `GET /users/profile` (có fallback đọc `dietary_preference` cũ nếu `diet` null), serialize đúng key wire sang `PATCH /users/profile`, và được lưu/khôi phục trong `SessionController` cache.
- [ ] Cả `app_vi.arb` và `app_en.arb` có đầy đủ chuỗi cho 5 chế độ ăn, 5 bệnh nền, 8 nhóm dị ứng + ví dụ, màn Hồ sơ ăn uống, trạng thái lọc rỗng, và đúng nguyên văn `"Gợi ý tham khảo, không thay lời khuyên của bác sĩ"`.

**Verification:**
- [ ] Codegen & l10n: `cd src/frontend && dart run build_runner build --delete-conflicting-outputs && flutter gen-l10n`
- [ ] Tests pass: `cd src/frontend && flutter test test/unit/auth/`

**Dependencies:** Task 1

**Files likely touched:**
- `src/frontend/lib/shared/domain/dietary_preference.dart`
- `src/frontend/lib/shared/domain/nutrition_profile.dart` *(new)*
- `src/frontend/lib/features/auth/domain/entities/user.dart`
- `src/frontend/lib/features/auth/data/models/auth_dto.dart`
- `src/frontend/lib/features/auth/presentation/controllers/session_controller.dart`
- `src/frontend/lib/l10n/app_vi.arb` & `src/frontend/lib/l10n/app_en.arb`

**Estimated scope:** Medium (5 source files + 2 ARB files; giữ phạm vi tập trung 1 tầng domain/auth)

---

#### Task 5: FE — Sửa bug `SuggestionRequest` (3.7) & nối `fit_reasons` ở tầng Data/Mock

**Description:** Sửa lỗi `"Nhiều rau"` bị đổi thành `'vegetarian'` trong `suggestion_request.dart`, bỏ phần FE tự gửi `dietary_restrictions`/`allergies`/`disliked_ingredients` và không gửi `mealType` làm `scenario_type` sức khoẻ vì BE đã tự đọc từ hồ sơ người dùng. Bổ sung parse `fit_reasons` (và `warnings`/`analysis.summary`) xuyên suốt `RecommendationItemDto` → `DishSuggestion` → `SuggestionRepositoryImpl` và cập nhật `assets/mock/recommendations.json`.

**Acceptance criteria:**
- [ ] `SuggestionRequest.toBody()` không còn chứa nhánh `DietaryPreference.moreVeg => 'vegetarian'` và không tự gửi chế độ ăn/dị ứng/scenario sức khoẻ lên BE.
- [ ] `RecommendationItemDto` parse `fit_reasons` (tolerant khi null hoặc thiếu) và map sang `DishSuggestion.fitReasons: List<String>`.
- [ ] `assets/mock/recommendations.json` có `fit_reasons` mẫu trên từng món để chế độ `BACKEND=mock` hiển thị được đầy đủ.

**Verification:**
- [ ] Codegen & analyze: `cd src/frontend && dart run build_runner build --delete-conflicting-outputs && flutter analyze`
- [ ] Tests pass: `cd src/frontend && flutter test test/unit/suggestions/`

**Dependencies:** Task 1, Task 4

**Files likely touched:**
- `src/frontend/lib/features/suggestions/domain/entities/suggestion_request.dart`
- `src/frontend/lib/features/suggestions/data/models/recommendation_dto.dart`
- `src/frontend/lib/features/suggestions/domain/entities/dish_suggestion.dart`
- `src/frontend/lib/features/suggestions/data/repositories/suggestion_repository_impl.dart`
- `src/frontend/assets/mock/recommendations.json`
- `src/frontend/test/unit/suggestions/suggestion_list_controller_test.dart`

**Estimated scope:** Medium (5 files + test)

---

### Checkpoint 2: FE Domain & Data Gate (Sau Tasks 4–5)
- [ ] `dart run build_runner build --delete-conflicting-outputs && flutter gen-l10n` chạy sạch.
- [ ] `flutter analyze` báo `No issues found!`.
- [ ] Toàn bộ unit tests trong `test/unit/auth/` và `test/unit/suggestions/` pass.

---

### Phase 3: Frontend UI — Onboarding & Màn Hồ sơ ăn uống (3.6)

#### Task 6: FE — Tách `DietaryPreferenceSelector` dùng chung & cập nhật Onboarding đồng bộ API

**Description:** Tách phần chọn 1 trong 5 chế độ ăn (gồm thêm `Ăn chay`) thành widget tái sử dụng chuẩn Design System (`DietaryPreferenceSelector`) và widget khuyến cáo (`NutritionDisclaimerBanner`). Cập nhật `DietaryPreferenceScreen` (Onboarding bước 1) sử dụng widget này, lưu local + gọi `PATCH /users/profile` với `{'diet': selected.wire}` (cập nhật `SessionController`, best-effort nếu offline không chặn luồng onboarding).

**Acceptance criteria:**
- [ ] Onboarding hiển thị đủ 5 lựa chọn chế độ ăn (Cân bằng, Nhiều đạm, Ít calo, Nhiều rau, Ăn chay) kèm dòng *"Gợi ý tham khảo, không thay lời khuyên của bác sĩ"*.
- [ ] Khi bấm Tiếp tục, `DietaryPreferenceController` cập nhật local và đồng bộ `diet` qua `PATCH /users/profile` + `SessionController.applyUpdatedUser`.
- [ ] Zero raw `Colors.*` / `Color(0x...)` mới; hiển thị sạch ở cả Light và Dark mode.

**Verification:**
- [ ] Tests pass: `cd src/frontend && flutter test test/widget/onboarding/` *(tạo test mới nếu chưa có)*
- [ ] Analyze: `cd src/frontend && flutter analyze`

**Dependencies:** Task 4

**Files likely touched:**
- `src/frontend/lib/shared/widgets/dietary_preference_selector.dart` *(new)*
- `src/frontend/lib/shared/widgets/nutrition_disclaimer_banner.dart` *(new)*
- `src/frontend/lib/features/onboarding/presentation/screens/dietary_preference_screen.dart`
- `src/frontend/lib/features/onboarding/presentation/controllers/onboarding_controller.dart`
- `src/frontend/test/widget/onboarding/dietary_preference_screen_test.dart` *(new)*

**Estimated scope:** Medium (4–5 files)

---

#### Task 7: FE — Màn "Hồ sơ ăn uống" trong Cài đặt & tự làm mới gợi ý (3.6)

**Description:** Tạo màn `NutritionProfileScreen` và controller `NutritionProfileController` (`@riverpod`) cho phép người dùng xem & chỉnh đầy đủ 5 trường hồ sơ ăn uống (số người ăn 1–10, chế độ ăn tái sử dụng `DietaryPreferenceSelector`, chọn nhiều tình trạng sức khoẻ, chọn nhiều 8 nhóm dị ứng, nhập tự do + gợi ý từ catalog cho món/nguyên liệu không ăn), lưu qua `PATCH /users/profile`, cập nhật `SessionController` và invalidate gợi ý để kết quả phản ánh ngay.

**Acceptance criteria:**
- [ ] Truy cập được từ `SettingsHomeScreen` (và liên kết từ `PreferencesScreen`) qua route mới `Routes.settingsNutritionProfile` (`/settings/nutrition-profile`).
- [ ] Đủ 5 phần tương tác mượt (stepper 1–10 có tap target ≥ 48dp, 5 chế độ ăn, 5 bệnh nền multi-select, 8 nhóm dị ứng multi-select kèm ví dụ, ô nhập nguyên liệu không ăn hỗ trợ autocomplete qua `ingredientSearchControllerProvider` + thêm tự do + chip xoá) và có `NutritionDisclaimerBanner`.
- [ ] Bấm Lưu gọi `PATCH /users/profile`, cập nhật `SessionController`, invalidate `suggestionListControllerProvider` và `homeDashboardProvider`, hiện snackbar thành công; đóng và mở lại app vẫn giữ nguyên hồ sơ đã lưu.

**Verification:**
- [ ] Codegen & analyze: `cd src/frontend && dart run build_runner build --delete-conflicting-outputs && flutter analyze`
- [ ] Tests pass: `cd src/frontend && flutter test test/widget/settings/`
- [ ] Manual check: mở màn ở cả Light & Dark theme, kiểm tra bàn phím IME không che ô nhập nguyên liệu không ăn.

**Dependencies:** Task 2, Task 4, Task 6

**Files likely touched:**
- `src/frontend/lib/features/settings/presentation/controllers/nutrition_profile_controller.dart` *(new)*
- `src/frontend/lib/features/settings/presentation/screens/nutrition_profile_screen.dart` *(new)*
- `src/frontend/lib/features/settings/presentation/screens/settings_home_screen.dart`
- `src/frontend/lib/app/router/routes.dart` & `src/frontend/lib/app/router/app_router.dart`
- `src/frontend/test/widget/settings/nutrition_profile_screen_test.dart` *(new)*

**Estimated scope:** Medium (5 files + test)

---

### Checkpoint 3: Nutrition Profile Flow (Sau Tasks 6–7)
- [ ] Luồng Onboarding chọn chế độ ăn lưu được lên `users.preferences.diet` (kể cả `vegetarian`).
- [ ] Màn Hồ sơ ăn uống trong Cài đặt load/save/reopen giữ đủ 5 trường, không mất key `preferences` khác.
- [ ] `flutter analyze` sạch và widget tests `onboarding` + `settings` pass 100%.

---

### Phase 4: Frontend UI — `fit_reasons`, Trạng thái lọc rỗng & Polish (3.8)

#### Task 8: FE — Hiển thị `fit_reasons` trên thẻ món & chi tiết điểm + Disclaimer (3.8)

**Description:** Mở rộng `SuggestionCard` để hiển thị 1–3 lý do hợp với hồ sơ (`fit_reasons`) gọn gàng, truyền dữ liệu ở cả 3 màn dùng `SuggestionCard` (`SuggestionListScreen`, `HomeScreen`, `CookableRecipesScreen`). Cập nhật `ScoreBreakdownSheet` để hiện mục riêng "Vì sao hợp với bạn" liệt kê đầy đủ `fit_reasons` và gắn `NutritionDisclaimerBanner` trên màn gợi ý và chi tiết điểm.

**Acceptance criteria:**
- [ ] `SuggestionCard` hiển thị tối đa 3 `fit_reasons` (khi danh sách không rỗng), text tiếng Việt dài wrap gọn không overflow ở màn nhỏ và rõ tương phản trên cả Light & Dark theme.
- [ ] `ScoreBreakdownSheet` hiển thị đầy đủ `fit_reasons` (khi có) cùng dòng *"Gợi ý tham khảo, không thay lời khuyên của bác sĩ"*.
- [ ] `SuggestionListScreen`, `HomeScreen` và `CookableRecipesScreen` đều truyền `fitReasons` xuống `SuggestionCard`; màn gợi ý có hiển thị dòng khuyến cáo tham khảo rõ ràng.

**Verification:**
- [ ] Tests pass: `cd src/frontend && flutter test test/widget/suggestions/ test/widget/home/`
- [ ] Analyze: `cd src/frontend && flutter analyze`

**Dependencies:** Task 5, Task 6

**Files likely touched:**
- `src/frontend/lib/core/widgets/suggestion_card.dart`
- `src/frontend/lib/features/suggestions/presentation/screens/suggestion_list_screen.dart`
- `src/frontend/lib/features/suggestions/presentation/widgets/score_breakdown_sheet.dart`
- `src/frontend/lib/features/home/presentation/screens/home_screen.dart`
- `src/frontend/lib/features/pantry/presentation/screens/cookable_recipes_screen.dart`

**Estimated scope:** Medium (5 files)

---

#### Task 9: FE — Xử lý trạng thái "lọc hết món" & Kiểm thử tổng thể FE + BE

**Description:** Khi `POST /recommendations` trả rỗng nhưng kho người dùng vẫn đang có nguyên liệu active (do bộ lọc bệnh nền/dị ứng/món không ăn khắt khe), hiển thị empty state rõ ràng giải thích lý do và dẫn tới 2 hành động ("Thêm nguyên liệu" và "Xem hồ sơ ăn uống") — tuyệt đối không tự nới lỏng bộ lọc dị ứng. Hoàn thiện widget tests (cả Light & Dark mode) và chạy toàn bộ verification gate của cả BE và FE.

**Acceptance criteria:**
- [ ] Phân biệt được 2 trạng thái rỗng ở `SuggestionListScreen`: kho trống (CTA thêm nguyên liệu) vs kho có đồ nhưng lọc hết món (thông báo rõ "thử thêm nguyên liệu" + nút mở Hồ sơ ăn uống, không tự tắt lọc dị ứng).
- [ ] Có widget test kiểm chứng: hiển thị `fit_reasons` trên card & sheet, hiển thị disclaimer, và empty-after-filter state ở cả Light/Dark mode.
- [ ] Toàn bộ verification gate của BE và FE pass sạch 0 lỗi, 0 warning.

**Verification:**
- [ ] BE gate: `cd src/backend && ruff check . && ruff format --check . && mypy --strict src/module/user src/module/recommendations && pylint src/module/user src/module/recommendations && pytest src/test/test_user_service.py src/test/test_user_router.py src/test/test_recommendation_ai_service.py src/test/test_recommendation_router.py`
- [ ] FE gate: `cd src/frontend && dart run build_runner build --delete-conflicting-outputs && flutter gen-l10n && dart format . && flutter analyze && flutter test`

**Dependencies:** Task 3, Task 7, Task 8

**Files likely touched:**
- `src/frontend/lib/features/suggestions/presentation/screens/suggestion_list_screen.dart`
- `src/frontend/lib/features/suggestions/presentation/controllers/suggestion_list_controller.dart`
- `src/frontend/test/widget/suggestions/suggestion_list_screen_test.dart`
- `src/frontend/test/unit/suggestions/suggestion_chips_and_badge_test.dart`

**Estimated scope:** Small–Medium (4 files)

---

### Checkpoint 4: Complete & Integration Readiness (Sau Tasks 8–9)
- [ ] Tất cả acceptance criteria của các đầu việc thuộc FE + BE (3.1, 3.4, 3.5 [BE], 3.6, 3.7, 3.8) đã đạt.
- [ ] Chạy thử end-to-end với live BE (`BACKEND=live`): đổi hồ sơ sang `Ăn chay` → màn Gợi ý không còn món có thịt ngay lập tức (kể cả khi nhánh AI mới chưa merge).
- [ ] Sẵn sàng ghép nhánh AI của Gia Huy (3.2, 3.3, 3.5 [AI], 3.9) mà không cần sửa lại FE hay BE contract.

---

## 6. Risks and Mitigations

| Rủi ro | Mức độ | Cách giảm thiểu |
|---|---|---|
| Teammate (Gia Huy) dùng mã `allergies` hoặc `health_conditions` khác bản nháp (vd `milk` thay vì `dairy`, `keto` thay vì `an_kieng_keto_lowcarb`) | **High** | Chốt bảng mã ngay ở **Task 1** trong `docs/api-contract.md` và xác nhận với Gia Huy trước khi code Task 2 & Task 4. |
| SQLAlchemy không phát hiện thay đổi in-place trên cột `JSONB` (`user.preferences`) | **High** | Luôn tạo dict mới `user.preferences = {**(user.preferences or {}), **incoming}` trong `UserService.update_profile` và có unit test kiểm chứng commit + giữ key cũ. |
| Nhánh AI của Gia Huy chưa kịp thêm `fit_reasons` hoặc `scenario_types` khi BE/FE merge trước | **Med** | BE giữ trường `scenario_type` tương thích ngược song song với `scenario_types`, và đọc `fit_reasons` an toàn với default `[]`. FE chỉ render khu vực `fit_reasons` khi list không rỗng. |
| Lọc quá chặt (nhiều bệnh nền + dị ứng) khiến danh sách gợi ý trống | **Med** | BE gắn warning `NO_MATCH_AFTER_FILTERS` + message rõ; FE hiện thông báo gợi ý thêm nguyên liệu hoặc xem lại hồ sơ ăn uống, tuyệt đối không tự nới lỏng bộ lọc dị ứng. |
| Chuỗi `fit_reasons` tiếng Việt dài làm vỡ layout `SuggestionCard` trên màn nhỏ | **Low** | Giới hạn 1–3 mục trên card, dùng `Wrap` hoặc `Expanded` + `maxLines: 2, overflow: TextOverflow.ellipsis`, test với text dài trong widget test. |

---

## 7. Phối hợp với Teammate AI (Checklist bàn giao contract sau Task 1)

Sau khi hoàn thành **Task 1**, gửi nhanh Gia Huy 3 điểm chốt để 2 bên khớp 100% khi merge:
1. **Input BE truyền cho `RecommendationEngine.recommend(request)`**: `items`, `household_size` (`1..10`), `diet`, `scenario_types` (list gồm `"an_chay"` nếu ăn chay + các mã trong `health_conditions`), `scenario_type` (fallback phần tử đầu hoặc `"custom"`), `allergies` (8 mã chuẩn), `disliked_ingredients` (`list[str]`).
2. **Output `EngineRecommendation` trả về cho BE**: bổ sung `fit_reasons: list[str] = field(default_factory=list)` (1–3 câu tiếng Việt ngắn gọn, không dùng dấu quá dài).
3. **Trạng thái rỗng**: giữ `EngineResult(status="empty", message=...)` với câu thông báo tiếng Việt thân thiện khi lọc cứng loại hết ứng viên.
