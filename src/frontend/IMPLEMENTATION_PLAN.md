# SweepFood Frontend — Kế hoạch triển khai source

> Tài liệu này = **lộ trình code** cho frontend. Đi kèm:
> - `plan.md` — danh sách screen, IA, hợp đồng API, domain model (từ giai đoạn design)
> - Design canvas (Claude Design) — 80 artboard sáng+tối, mỗi artboard ứng 1 screen
> - `lib/` — đã scaffold sẵn ~260 file **stub** (chỉ comment + `TODO`, chưa có logic)

---

## Tình trạng hiện tại

| Milestone | Trạng thái |
|---|---|
| **M0 — Nền tảng + khung 5 tab** | ✅ Xong |
| M1 — Kho (vertical slice) | ⬜ Chưa — làm tiếp |
| M2 — Trang chủ | ⬜ Chưa |
| M3 — Gợi ý + Món + Nấu (vòng lặp lõi) | ⬜ Chưa |
| M4 — Nhập liệu đa phương thức | ⬜ Chưa |
| M5 — Auth + Onboarding + phần còn lại | ⬜ Chưa |
| M6 — Hoàn thiện, i18n, test, build | ⬜ Chưa |

### M0 đã hoàn thành (2026-08-30)

- **`core/config/`** — `app_config.dart` (đọc `--dart-define`), `flavor.dart` (Flavor / Backend enum), `app_constants.dart`, `app_config_provider.dart`
- **`app/theme/`** — `app_colors.dart` (BrandPalette + `SweepColors` ThemeExtension: 4 mức expiry + 4 tint tầng), `app_typography.dart` (thang chữ Inter), `app_spacing.dart` (Gap/Radii/Shadows/Insets), `app_theme.dart` (light + dark ThemeData), `theme_mode_controller.dart` (persist prefs)
- **`core/error/`** — `failure.dart` (sealed, 11 loại, message tiếng Việt), `error_mapper.dart` (DioException/…→ Failure), `app_exception.dart`
- **`core/utils/`** — `result.dart` (`typedef Result<T> = Either<Failure,T>`), `logger.dart`, `formatters/{currency_vnd,expiry_text,quantity_format}.dart`, `extensions/{build_context_x,date_time_x,num_x}.dart`
- **`shared/domain/`** — `storage_tier.dart`, `measurement_unit.dart`, `nutrition_info.dart`, `expiry_status.dart` (`Expiry.levelFromDays` / `isNearExpiry` / `daysUntil`), `dietary_preference.dart`, `paginated.dart`
- **`core/network/`** — `api_client.dart` (abstract), `dio_api_client.dart`, `mock_api_client.dart` (đọc `assets/mock/*.json`, echo cho write), `api_paths.dart`, `api_result.dart` (`guard()` / `guardVoid()`), `interceptors/{auth,logging}_interceptor.dart`, `network_providers.dart` (`apiClientProvider` chọn mock/live)
- **`core/storage/`** — `secure_storage.dart` (`SecureStore`), `prefs.dart` (`sharedPreferencesProvider`, override trong bootstrap), `storage_providers.dart`
- **`core/entitlements/`** — `premium_flag.dart` (`kPremiumEnabled`), `entitlements.dart` (`allUnlocked` / `freeTier`), `entitlements_provider.dart` (`entitlementsProvider` + `featureAllowedProvider`), `gated.dart` (`Gated` widget)
- **`core/widgets/`** — `feature_placeholder.dart`, `async_value_widget.dart`, `empty_state.dart`, `error_view.dart`, `loading_skeleton.dart` (`SkeletonBox`/`SkeletonList`), `app_scaffold.dart`, `primary_button.dart`, `secondary_button.dart`, `app_text_button.dart`, `app_icon_button.dart`, `app_fab.dart`, `app_bottom_nav.dart`, `app_bottom_sheet.dart` (`showAppBottomSheet` + `SheetBody`), `app_snackbar.dart`, `app_search_field.dart`, `filter_chip_row.dart`, `section_header.dart`, `expiry_badge.dart`, `tier_chip.dart`, `macro_ring.dart` (CustomPaint), `macro_chips.dart`, `waste_saved_pill.dart`, `quick_action_sheet.dart`, `pantry_item_card.dart` (param-based — M1 map entity → param), `suggestion_card.dart` (param-based — M3)
- **`app/`** — `router/{routes,route_guards,app_router}.dart` (GoRouter + `StatefulShellRoute.indexedStack` 5 nhánh; `appRedirect` đang **dev-bypass**), `shell/app_shell.dart`, `app.dart` (`MaterialApp.router` + theme + locale `vi`), `bootstrap.dart`, `main.dart`
- **5 placeholder screen** cho các tab (`home/pantry/suggestions/shopping_list/settings` → screen thật ở milestone tương ứng). Settings có sẵn nút đổi theme để test dark mode.
- `dart run build_runner build` chạy OK (7 file `.g.dart`, **commit kèm** để teammate không cần chạy codegen mới build được).
- ✅ `flutter analyze` → **No issues**. ✅ `flutter build web --dart-define-from-file=config/dev.json` → build thành công.

**Chạy thử:** `flutter run -d chrome --dart-define-from-file=config/dev.json` — khung 5 tab, đổi tab OK, vào tab Cá nhân đổi Sáng/Tối/Hệ thống thấy theme đổi.

> Cập nhật bảng này khi hoàn thành từng milestone.

---

## Quy ước chung (áp dụng toàn bộ)

- **Mọi file đích đã tồn tại dưới dạng stub** trong `lib/`. Làm việc = **thay nội dung stub** rồi chạy codegen. Không tạo cấu trúc song song.
- **State management: Riverpod 3.1 + riverpod_annotation 4.0 + riverpod_generator 4.0** — dùng `@riverpod` codegen. Controller = `@riverpod class Foo extends _$Foo` (`Notifier` / `AsyncNotifier` qua `build()`). Singleton toàn app (`sessionController`, `appConfig`, `dio`, storage) = `@Riverpod(keepAlive: true)`. `ref.watch` / `ref.read` / `ref.listen`.
  Vòng lặp dev: `dart run build_runner watch -d`.
- **Model: freezed 3.2** — khai báo `@freezed abstract class X with _$X` (freezed 3 bắt buộc modifier `abstract`/`sealed`). Union/sealed (`Failure`, `ScanStatus`…) dùng `sealed`. DTO thêm `factory X.fromJson`.
- **Luồng lỗi:** datasource `throw` (`DioException`, `FormatException`) → repository `try/catch` → `error_mapper.dart` → trả `Either<Failure, T>` (`typedef Result<T> = Either<Failure, T>` trong `core/utils/result.dart`, dùng fpdart). Controller đổi thành `AsyncValue` cho UI. UI render qua `core/widgets/async_value_widget.dart` (loading skeleton / error view / data).
- **Mock-first:** `core/network/mock_api_client.dart` implement `ApiClient`; khớp `core/network/api_paths.dart`; đọc `assets/mock/<name>.json` qua `rootBundle`; trễ ~320ms; write thì echo lại payload kèm id sinh ra. `network_providers.dart` chọn Mock vs `DioApiClient` theo `AppConfig.backend`.
- **Design → code:** 1 artboard `*.dc.html` → 1 file screen/widget. `core/widgets/*` ứng 1:1 với artboard "Components"; `app/theme/*` ứng artboard "Foundations" (primary `#2D6A4F`, secondary `#95D5B2`, tertiary `#8D4D4E`, expiry `expired/critical/soon/ok`, 4 tint tầng, thang chữ Inter, spacing 4–40, radius 8/12/16/24, đổ bóng, dark bg `#101511` / surface `#1A211C`).
- **Chuỗi text:** hardcode **tiếng Việt** thẳng trong widget cho nhanh. Tách ra `app_vi.arb` ở M6. Không có "tiền tiết kiệm" ở đâu cả (đã bỏ — dùng số nguyên liệu dùng trước hạn / kg).
- **`premiumEnabled = false`** (`core/entitlements/premium_flag.dart`): `entitlementsProvider` trả `Entitlements.allUnlocked()`; widget `Gated` render child vô điều kiện; không có `QuotaBanner` / màn I-08.
- **Chạy app:** luôn `flutter run --dart-define-from-file=config/dev.json` (thêm `-d chrome` / `-d <emulator>`). Giữ `flutter analyze` sạch sau mỗi milestone (hiện đang sạch — đừng làm hỏng).
- **Package name** hiện là `frontend` (org `com.example.frontend`). Import dạng `package:frontend/...`. Đổi tên → M6.

---

## Milestones

### M0 — Nền tảng & khung 5 tab
**Mục tiêu:** app chạy được (web + android) với hạ tầng thật, Material 3 light/dark từ design tokens, bottom nav 5 tab, mỗi tab 1 placeholder.

- `core/config/` — `app_config.dart` (đọc `String/bool/int.fromEnvironment`), `flavor.dart`, `app_constants.dart` ✅
- `app/theme/` — `app_colors.dart` (+ `SweepColors` ThemeExtension cho màu expiry/tầng), `app_typography.dart`, `app_spacing.dart`, `app_theme.dart` (light+dark), `theme_mode_controller.dart` (`@riverpod` Notifier + prefs) — *đang làm*
- `core/error/` — `failure.dart` (`sealed`), `error_mapper.dart`, `app_exception.dart`
- `core/utils/` — `result.dart` (typedef fpdart `Either`), `logger.dart`, `formatters/{expiry_text,quantity_format,currency_vnd}.dart`, `extensions/{build_context_x,date_time_x,num_x}.dart`
- `shared/domain/` — `storage_tier.dart` (enum), `measurement_unit.dart`, `nutrition_info.dart`, `expiry_status.dart` (near-expiry = `daysUntil <= NEAR_EXPIRY_DAYS`), `dietary_preference.dart`, `paginated.dart`
- `core/network/` — `api_client.dart` (abstract), `dio_api_client.dart`, `mock_api_client.dart`, `api_paths.dart`, `api_result.dart`, `interceptors/{auth,logging}_interceptor.dart`, `network_providers.dart`
- `core/storage/` — `secure_storage.dart`, `prefs.dart` ✅, `storage_providers.dart`
- `core/entitlements/` — `entitlements.dart`, `premium_flag.dart`, `entitlements_provider.dart`, `gated.dart`
- `core/widgets/` — từ artboard "Components", ưu tiên: `app_scaffold`, `primary_button`, `secondary_button`, `app_text_button`, `app_icon_button`, `app_fab`, `app_bottom_nav`, `app_bottom_sheet`, `app_snackbar`, `app_search_field`, `filter_chip_row`, `section_header`, `expiry_badge`, `tier_chip`, `macro_ring`, `macro_chips`, `pantry_item_card`, `suggestion_card`, `quick_action_sheet`, `waste_saved_pill`, `empty_state`, `error_view`, `loading_skeleton`, `async_value_widget`. (`confidence_field`, `waveform_recorder`, `viewfinder_overlay` để M4.)
- `app/router/` — `routes.dart` (hằng path), `route_guards.dart` (**dev-bypass: redirect luôn null** ở M0–M4), `app_router.dart` (`@riverpod` `GoRouter`, `StatefulShellRoute.indexedStack` cho 5 tab), `app/shell/app_shell.dart`
- `app/app.dart` (`MaterialApp.router` + theme + `themeModeProvider` + `flutter_localizations`), `bootstrap.dart` (guarded zone, `WidgetsFlutterBinding.ensureInitialized`, preload prefs, `runApp(ProviderScope(...))`), `main.dart` → `bootstrap()`
- Chạy `dart run build_runner build` lần đầu; xác nhận `*.g.dart` / `*.freezed.dart` bị loại khỏi analyze (đã cấu hình trong `analysis_options.yaml`)

**Kiểm tra:** `flutter run -d chrome --dart-define-from-file=config/dev.json` → khung có theme, chuyển tab OK, đổi dark mode hệ thống thì đổi theme; `flutter analyze` sạch.

### M1 — Kho (vertical slice) — chứng minh pipeline data→domain→presentation→mock
- `features/pantry/domain/` — `pantry_item.dart` (freezed; computed `daysUntilExpiry`, `expiryStatus`, `priorityScore`), `pantry_summary.dart`, `pantry_repository.dart`
- `features/pantry/data/` — `pantry_item_dto.dart` (freezed+json), `pantry_remote_data_source.dart`, `pantry_repository_impl.dart` (DTO↔entity, catch→`Result`)
- `features/catalog/` — `ingredient.dart`, `ingredient_dto.dart`, `ingredient_remote_data_source.dart`, `ingredient_repository_impl.dart`, `ingredient_search_controller.dart` (autocomplete K-03)
- `features/pantry/presentation/controllers/` — `pantry_list_controller.dart` (`AsyncNotifier`; lọc tầng, sort priority/tên/mới, tìm kiếm), `pantry_item_controller.dart`, `add_ingredient_controller.dart` (form)
- `features/pantry/presentation/screens/` — `pantry_screen.dart` (K-01), `pantry_item_detail_screen.dart` (K-02), `add_ingredient_screen.dart` (K-03); `widgets/adjust_quantity_sheet.dart` (K-04), `widgets/tier_segmented_control.dart`
- Fixture: viết `assets/mock/pantry_items.json`, `pantry_summary.json`, `ingredients.json` khớp DTO (≥ 8 item đủ 4 tầng, có mix cận hạn)
- Tab Kho + FAB → tạm mở thẳng `add_ingredient_screen` (AddEntryChooser thật ở M4)

**Kiểm tra:** thủ công — list theo tầng, sort, tìm, mở detail, thêm/sửa/xoá/consume (mock echo lại). Unit test mẫu `test/unit/pantry/pantry_repository_impl_test.dart` (mapping + nhánh lỗi, mocktail).

### M2 — Trang chủ (H-01)
- `features/home/presentation/` — `home_controller.dart` (`pantry_summary` + slice cận hạn + top suggestions [suggestions stub tới M3]), `home_screen.dart`
- Dùng `waste_saved_pill` (số nguyên liệu dùng trước hạn, số mock), mini-bar tổng quan 4 tầng, "Cần dùng sớm" (card ngang `pantry_item_card`), state empty/loading/error

**Kiểm tra:** thủ công; trỏ mock vào fixture kho rỗng để xem empty state.

### M3 — Gợi ý + Món + Nấu (đóng vòng lặp lõi)
- `features/suggestions/` — `dish_suggestion.dart`, `score_breakdown.dart`, `suggestion_request.dart`; DTO; `suggestion_remote_data_source.dart`; repo impl; `suggestion_list_controller.dart` (lọc: bữa, thời gian nấu, ưu tiên dinh dưỡng); `suggestion_list_screen.dart` (S-01); `widgets/score_breakdown_sheet.dart` (S-02, `0.4E+0.3A+0.2P+0.1U`)
- `features/dishes/` — `dish.dart`, `dish_ingredient.dart`, `cooking_step.dart`; DTO; ds; repo impl; `dish_detail_controller.dart` (đổi khẩu phần → tính lại lượng + dinh dưỡng); `dish_detail_screen.dart` (D-01); `widgets/ingredient_checklist.dart`, `widgets/cooking_steps_view.dart` (list, chưa làm chế độ toàn màn D-02)
- `features/cooking/` — `cook_confirmation.dart` (mode: exact/half/all/custom), `cook_result.dart` (before→after mỗi item + `wasteAvoidedGrams`), `cooked_food.dart`; DTO; ds; repo impl; `cooking_controller.dart` + `custom_usage_controller.dart` + `leftover_controller.dart`; `cook_result_screen.dart` (D-05/D-07); `widgets/{post_cook_confirm_sheet,custom_usage_sheet,leftover_save_sheet}.dart` (D-03/D-04/D-06)
- `features/nutrition/presentation/widgets/macro_breakdown.dart` (ring + chips)
- Xác nhận đã nấu → mock trả pantry items mới → `ref.invalidate(pantryListController)` + `homeController` → số chống lãng phí ở Home cập nhật. "Thêm phần thiếu vào danh sách mua" = stub tới M5.
- Fixture: `assets/mock/suggestions.json`, `dish.json`, `cook_result.json`

**Kiểm tra:** `integration_test/core_loop_test.dart` — thêm nguyên liệu → mở gợi ý → mở món → "Đã nấu" → chọn thao tác → xác nhận trừ kho → assert lượng trong kho giảm + số ở Home tăng. Thủ công trên emulator.

### M4 — Nhập liệu đa phương thức
- `core/permissions/permission_service.dart` + `permission_prime_sheet.dart` (G-04); `core/media/image_capture_service.dart` (**image_picker** — camera hệ thống, ít setup nhất; `camera` là phương án thay nếu cần viewfinder trong app đúng như design I-01), `audio_recorder_service.dart` (`record` — bỏ comment trong `pubspec.yaml`)
- `features/ingest/domain/` — `scan_job.dart`, `parsed_item_draft.dart`, `scan_type.dart`, `scan_repository.dart`
- `features/ingest/data/` — `scan_job_dto.dart`, `scan_remote_data_source.dart` (multipart), `scan_repository_impl.dart`
- `features/ingest/presentation/controllers/` — `scan_controller.dart` (chụp→upload→poll→draft), `label_review_controller.dart`, `receipt_review_controller.dart`, `voice_capture_controller.dart`
- Screens — `add_entry_chooser_sheet.dart` (G-03), `camera_capture_screen.dart` (I-01/I-04), `image_crop_screen.dart` (I-02, image_cropper), `label_review_screen.dart` (I-03), `receipt_review_screen.dart` (I-05), `voice_capture_screen.dart` (I-06), `voice_review_screen.dart` (I-07), `scan_failed_screen.dart` (I-09). Widget — `confidence_field.dart`, `waveform_recorder.dart`, `viewfinder_overlay.dart`, `parsed_item_row.dart`
- Mock: `POST /scan/{label,receipt,voice}` → `ScanJob` mẫu có `parsedItems`; confirm → tạo hàng loạt pantry items (dùng lại `pantry_repository`)
- FAB mọi nơi → `AddEntryChooser` thật

**Kiểm tra:** thủ công trên máy android thật (camera + mic thật); analyze.

### M5 — Auth gate + Onboarding + phần còn lại
- **Auth (A-01..A-04)** — `features/auth/`: `user.dart`, `session.dart`, `auth_dto.dart`, `auth_remote_data_source.dart`, `auth_repository_impl.dart`, `session_controller.dart` (`@Riverpod(keepAlive:true)`, token → `secure_storage`), `login/register/forgot_password_controller.dart`; screens splash/welcome/login/register/forgot. **Bật `route_guards.dart` thật** (chưa có session → `/welcome`). `auth_interceptor.dart` gắn token; 401 → refresh → logout.
- **Onboarding (A-05, A-06)** — `onboarding_controller.dart`, `dietary_preference_screen.dart`, `onboarding_pantry_screen.dart`; ưu tiên dinh dưỡng → `prefs` → vào `suggestion_request`
- **Thông báo (T-01, T-02) — mock** — `features/notifications/` entities/dto/ds/repo, `notifications_controller.dart`, `notification_center_screen.dart`, `near_expiry_detail_sheet.dart`, `notification_tile.dart`; icon chuông ở Home → center. `core/notifications/local_notifications.dart` đặt nhắc cận hạn cục bộ (không cần FCM). `fcm_service.dart` / `device_remote_data_source.dart` để no-op.
- **Danh sách mua sắm (B-01, B-02)** — full; "Thêm phần thiếu" từ dish detail → đổ vào đây; tab Mua sắm
- **Thực đơn tuần (M-01, M-02)** — full; "Tạo danh sách mua sắm" → generate shopping list
- **Báo cáo (R-01)** — `waste_reduction_summary.dart`, ds/repo, `reports_controller.dart`, `reports_screen.dart` ("Chống lãng phí": số + kg + số món đã nấu), `period_selector.dart`, `report_bar_chart.dart` (fl_chart)
- **Cài đặt (P-01..P-06)** — `app_preferences.dart`, `notification_preferences.dart`, `pantry_member.dart`; ds/repo; controllers; screens (settings_home, profile, preferences, notification_settings, pantry_sharing "Sắp có", about). Preferences nối `themeModeProvider` + ưu tiên dinh dưỡng + đơn vị mặc định. Tab Cá nhân.
- **Subscription (P-02, G-05)** — `subscription.dart`, `plan_option.dart`; ds/repo; `subscription_controller.dart` + `paywall_controller.dart`; `subscription_screen.dart`, `paywall_screen.dart` (thu thập quan tâm → `POST /subscription/premium-interest` mock)
- `core/analytics/` — `analytics_service.dart` (abstract) + `noop_analytics_service.dart` (chỉ log); phát `analytics_events.dart` tại: hoàn tất setup kho lần đầu, thêm nguyên liệu (theo phương thức), sửa field OCR, mở/nấu món, dùng đồ cận hạn, mở paywall
- Viết nốt `assets/mock/*.json`

**Kiểm tra:** thủ công toàn bộ 5 tab + auth gate; analyze.

### M6 — Hoàn thiện, i18n, test, live-swap, build
- **i18n:** tách chuỗi vi → `lib/l10n/app_vi.arb` + `AppL10n` (`flutter gen-l10n`); thêm `app_en.arb` khung
- **`docs/api-contract.md`** (gốc repo): FE tự viết hợp đồng REST từ `plan.md §9` + domain model, để BE implement theo. Chốt với team BE: base path (`/api/v1`), **port (config đang `8000`, plan.md giả định `4000`)**, tên endpoint (BE stub dùng `/ingestion/ocr/receipt`, `/recipes/recommend` vs plan.md `/scan/*`, `/suggestions/dishes`), envelope lỗi, pagination
- **Live swap:** `config/prod.json` `BACKEND=live`; chạy với backend thật; verify `DioApiClient` + `auth_interceptor`; ghi chú CORS cho web
- **Firebase/FCM** (khi có project): `flutterfire configure`; bật `firebase_core`/`firebase_messaging` trong `pubspec.yaml`; implement `fcm_service.dart` + `device_remote_data_source.dart`; xử lý deep-link trong `app_router.dart`
- **Test (tối thiểu):** `test/helpers/{test_providers,mocks}.dart` (`ProviderContainer` + mocktail); ~1 unit test mỗi loại tầng (repo mapping, controller state, 1 formatter); `integration_test/core_loop_test.dart` (từ M3, mở rộng chút)
- `flutter analyze` + `flutter test` xanh; script CI `flutter analyze && flutter test`
- **Tuỳ chọn:** đổi tên package `frontend`→`sweep_food`, org `com.example`→`com.cloudian`; app icon + splash; build flavor; build web + APK demo

---

## Kiểm tra end-to-end (theo milestone)

- **M0:** `flutter run -d chrome --dart-define-from-file=config/dev.json` → khung 5 tab có theme, chuyển tab OK, dark mode hệ thống đổi theme; `flutter analyze` → no issues
- **M1–M2:** thủ công trên emulator android — Kho list/detail/add/edit/consume trên mock; Home render tổng quan + cận hạn + waste pill; empty/error state qua fixture khác
- **M3 (vòng lặp lõi):** `flutter test integration_test/core_loop_test.dart` — thêm nguyên liệu → gợi ý → chi tiết món → "Đã nấu" → trừ kho được xác nhận + số ở Home cập nhật. Lặp lại thủ công trên emulator
- **M4:** thủ công trên máy android thật — camera (tem/hóa đơn) + mic (giọng nói) → draft → item xuất hiện trong Kho; priming quyền hiện trước prompt hệ thống
- **M5:** thủ công toàn bộ — auth gate chặn khi chưa đăng nhập; mọi tab + screen phụ load từ mock không lỗi
- **M6:** `flutter analyze && flutter test` xanh; với backend thật, `flutter run --dart-define-from-file=config/prod.json` và lặp lại đường vòng-lặp-lõi M3 thủ công
- **Mỗi milestone:** giữ `flutter analyze` sạch (hiện đang sạch — đừng làm hỏng)

---

## Rủi ro / việc còn treo

- **Riverpod 3.x + freezed 3.x là major mới** — cú pháp generated khác nhiều tutorial cũ; dành thêm thời gian cho vài class `@riverpod` / `@freezed` đầu tiên ở M0–M1
- **Fixture mock viết tay** khớp shape DTO — việc thật, làm dần theo milestone
- **Hợp đồng API với backend chưa chốt** (port, tên endpoint, envelope lỗi) — chỉ chặn live swap ở M6; mock-first giữ M0–M5 không bị chặn
- **FCM hoãn** → nhắc cận hạn dùng local notification tới khi có Firebase project; không có push từ server
- **Camera:** plan dùng `image_picker`; nếu cần viewfinder trong app đúng như design I-01, đổi sang package `camera` (nhiều setup hơn)
- **Đổi tên package/org** hoãn tới M6 (thao tác cơ học, rủi ro thấp)

---

## Nhận task thế nào

1. Chọn 1 mục chưa làm trong milestone đang mở (bảng trạng thái ở đầu file). **Không nhảy milestone.**
2. Mở file stub tương ứng trong `lib/` + artboard tương ứng trên design canvas + phần liên quan trong `plan.md` (§5 screen, §9 API/domain).
3. Code theo "Quy ước chung" ở trên. Chạy `dart run build_runner watch -d` khi làm.
4. `flutter analyze` phải sạch trước khi push. Chạy `flutter run --dart-define-from-file=config/dev.json` để xem thật.
5. Cập nhật bảng trạng thái khi xong milestone.
