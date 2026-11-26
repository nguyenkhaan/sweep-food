# Todo Checklist: Hướng 3 — Cá nhân hoá dinh dưỡng (FE + BE)

> Xem kế hoạch chi tiết tại [nutrition-personalization-plan.md](file:///c:/Projects/sweep-food/tasks/nutrition-personalization-plan.md).

## Phase 1: Contract & Backend Foundation
- [x] **Task 1 (3.1):** Chốt API Contract trong `docs/api-contract.md` (`users.preferences`, `PATCH /users/profile` shallow-merge, `POST /recommendations` + `fit_reasons` + `NO_MATCH_AFTER_FILTERS`, bảng mã BE ↔ AI)
- [x] **Task 2 (BE Profile):** Validate schema 5 trường hồ sơ ăn uống trong `user_dto.py` (`nutrition_profile.py`, 422 khi sai) và đổi `UserService.update_profile` sang shallow-merge + unit/router tests
- [x] **Task 3 (3.4 + 3.5 BE):** `RecommendationAIService` tự đọc `UserModel.preferences` điền request gửi AI engine (authoritative), nối `fit_reasons` an toàn, trả warning `NO_MATCH_AFTER_FILTERS` khi lọc rỗng + unit/router tests

### Checkpoint 1: Backend & Contract Gate
- [ ] Xác nhận mã wire `allergies` / `health_conditions` / `scenario_types` với Gia Huy
- [ ] Chạy `pytest`, `ruff`, `mypy --strict`, `pylint` trong venv/Docker BE (máy local chưa cài `uv`/`pytest`; đã pass `py_compile` & smoke test Python 3.13)

## Phase 2: Frontend Domain & Data Layer
- [x] **Task 4 (FE Domain):** Thêm `DietaryPreference.vegetarian`, tạo `NutritionProfile` (`@freezed`) + `HealthCondition` + `AllergyGroup`, nối `User`/`UserProfileDto`/`SessionController`, thêm l10n VI/EN (kèm câu khuyến cáo y tế) + unit tests
- [x] **Task 5 (3.7 + 3.8 FE Data):** Sửa lỗi `moreVeg => 'vegetarian'` trong `suggestion_request.dart`, bỏ phần FE tự gửi chế độ ăn/scenario sức khoẻ, nối `fit_reasons` qua `RecommendationItemDto` → `DishSuggestion` → `SuggestionRepositoryImpl` + cập nhật `assets/mock/recommendations.json` + unit tests

### Checkpoint 2: FE Domain & Data Gate
- [x] `dart run build_runner build --delete-conflicting-outputs && flutter gen-l10n` pass
- [x] `flutter analyze` báo `No issues found!`
- [x] `flutter test test/unit/auth/ test/unit/suggestions/` pass

## Phase 3: Frontend UI — Onboarding & Màn Hồ sơ ăn uống (3.6)
- [x] **Task 6 (3.6a Onboarding):** Tách `DietaryPreferenceSelector` (5 chế độ ăn) và `NutritionDisclaimerBanner`; cập nhật `DietaryPreferenceScreen` đồng bộ `PATCH /users/profile` + widget test
- [x] **Task 7 (3.6b Settings):** Xây `NutritionProfileController` + `NutritionProfileScreen` (đủ 5 mục, autocomplete catalog cho nguyên liệu không ăn, disclaimer), gắn route `/settings/nutrition-profile` vào `SettingsHomeScreen` & `PreferencesScreen` + auto-invalidate gợi ý khi lưu + widget tests (Dark mode)

### Checkpoint 3: Nutrition Profile Flow
- [x] Onboarding lưu được `diet` lên BE (kể cả `vegetarian`)
- [x] Màn Hồ sơ ăn uống trong Cài đặt lưu & mở lại app vẫn giữ đủ 5 mục
- [x] `flutter analyze` sạch và `flutter test test/widget/onboarding/ test/widget/settings/` pass

## Phase 4: Frontend UI — `fit_reasons`, Empty-Filter State & Polish (3.8)
- [x] **Task 8 (3.8 UI):** Hiển thị 1–3 `fit_reasons` trên `SuggestionCard` (S-01, Home, CookableRecipes), hiện đầy đủ `fit_reasons` + disclaimer trong `ScoreBreakdownSheet` và màn gợi ý
- [x] **Task 9 (Empty-Filter UX & Final Verification):** Phân biệt empty state "kho trống" vs "lọc hết món" (gợi ý thêm nguyên liệu / mở Hồ sơ ăn uống, không tự nới lỏng dị ứng), hoàn thiện widget tests (Light/Dark), chạy full FE verification gate

### Checkpoint 4: Complete & Integration Readiness
- [ ] BE gate (trong venv/Docker): `ruff`, `mypy --strict`, `pylint`, `pytest`
- [x] FE gate: `build_runner`, `gen-l10n`, `dart format`, `flutter analyze`, `flutter test` pass
- [ ] Kiểm thử end-to-end với live BE sau khi ghép nhánh AI của Gia Huy
