# SweepFood Frontend

Ứng dụng Flutter (mobile + web) cho **SweepFood** — trợ lý quản lý nguyên liệu và gợi ý bữa ăn thông minh (team Phantoms, AISC 2026).

> **Trạng thái:** đang triển khai theo `IMPLEMENTATION_PLAN.md`.
> **M0 (Nền tảng + khung 5 tab) đã xong** — app chạy được, có theme sáng/tối từ design tokens, bottom nav 5 tab, hạ tầng network/error/storage/entitlements + thư viện component. Các tab hiện là placeholder; feature thật làm từ M1.
> App đang chạy **mock-first**: dữ liệu lấy từ `assets/mock/*.json`, chưa cần backend.

## Tài liệu

| File | Nội dung |
| --- | --- |
| [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) | Lộ trình code (M0–M6), quy ước, "nhận task thế nào" — **đọc trước khi code** |
| [`plan.md`](plan.md) | Danh sách screen, IA, hợp đồng API, domain model (giai đoạn design) |
| Design canvas (Claude Design) | 80 artboard sáng + tối, mỗi artboard ứng 1 screen |
| [`../../docs/requirement.md`](../../docs/requirement.md) | Đặc tả sản phẩm gốc |

## Công nghệ

| Nhóm | Thư viện |
| --- | --- |
| Framework | Flutter / Dart (`sdk: ^3.5.0`) |
| State management + DI | **Riverpod 3** (`flutter_riverpod`, `riverpod_annotation` + `riverpod_generator` codegen) |
| Model | `freezed` + `json_serializable` (codegen) |
| Functional | `fpdart` — `Either<Failure, T>` cho repository |
| Điều hướng | `go_router` (`StatefulShellRoute` cho bottom nav) |
| HTTP | `dio` — bọc sau `ApiClient` abstract → `DioApiClient` \| `MockApiClient` |
| Lưu trữ | `shared_preferences` (prefs), `flutter_secure_storage` (token) |
| Media (M4) | `image_picker`, `image_cropper`, `permission_handler` · `record` (đang comment) |
| UI / chart | `flutter_svg`, `cached_network_image`, `fl_chart`, `intl` |
| Thông báo | `flutter_local_notifications` · `firebase_messaging` hoãn tới khi có Firebase project |
| Lint / test | `flutter_lints`, `custom_lint`, `riverpod_lint` · `mocktail` |

> Version trong `pubspec.yaml` đang để `any` cho giai đoạn scaffold; `pubspec.lock` đã chốt bộ hoạt động (Riverpod 3.1, freezed 3.2…). Siết lại thành caret range ở M6.

Nền tảng bật: **Android, iOS, Web** (macOS/Linux/Windows có sẵn nhưng không ưu tiên). Ưu tiên test trên **Android emulator + Chrome**.

## Chạy local

```powershell
cd src/frontend
flutter pub get
dart run build_runner build            # sinh *.g.dart / *.freezed.dart (đã commit sẵn, chạy lại khi cần)
flutter run -d chrome --dart-define-from-file=config/dev.json
# hoặc:  flutter run -d <emulator-id> --dart-define-from-file=config/dev.json
```

**Luôn truyền `--dart-define-from-file=config/dev.json`** — nếu không, `AppConfig` dùng giá trị mặc định (mock, `10.0.2.2:8000`).
Khi code, chạy song song codegen ở chế độ watch:

```powershell
dart run build_runner watch -d
```

Lần đầu build Android có thể cần: `flutter doctor --android-licenses`.

## Cấu hình (`config/*.json`)

Chạy qua `--dart-define-from-file`; `lib/core/config/app_config.dart` đọc các khóa:

| Khóa | dev.json | Ý nghĩa |
| --- | --- | --- |
| `BACKEND` | `mock` | `mock` = đọc `assets/mock/*.json`; `live` = gọi Dio thật |
| `API_BASE_URL` | `http://10.0.2.2:8000/api/v1` | base URL khi `BACKEND=live` (10.0.2.2 = localhost cho Android emulator) |
| `PREMIUM_ENABLED` | `false` | MVP mở hết tính năng, không gating |
| `NEAR_EXPIRY_DAYS` | `3` | ngưỡng "cận hạn" cho xếp hạng gợi ý + đếm chống lãng phí |
| `FLAVOR` | `dev` | dev / prod |

Không commit token, khóa API, keystore, `.env`. Token đăng nhập lưu bằng `flutter_secure_storage` (không dùng `shared_preferences`).

## Kiến trúc

Clean architecture, **feature-first**. Mỗi feature: `data/{datasources,models,repositories}` · `domain/{entities,repositories,usecases}` · `presentation/{controllers,screens,widgets}`.

```text
lib/
├── main.dart                     # → bootstrap()
├── bootstrap.dart                # guarded zone, preload prefs, ProviderScope
├── app/
│   ├── app.dart                  # MaterialApp.router + theme + locale
│   ├── router/                   # routes · route_guards (đang dev-bypass) · app_router (GoRouter)
│   ├── shell/app_shell.dart      # khung bottom nav 5 tab
│   └── theme/                    # app_colors (+ SweepColors ext) · app_typography · app_spacing · app_theme · theme_mode_controller
├── core/
│   ├── config/                   # AppConfig (từ --dart-define), flavor, constants
│   ├── network/                  # ApiClient (abstract) | DioApiClient | MockApiClient · api_paths · api_result (guard()) · interceptors
│   ├── error/                    # Failure (sealed) · error_mapper
│   ├── storage/                  # secure_storage · prefs
│   ├── entitlements/             # kPremiumEnabled · entitlementsProvider (allUnlocked) · Gated
│   ├── utils/                    # result (Either typedef) · logger · formatters · extensions
│   └── widgets/                  # ~26 component tái dùng (ExpiryBadge, TierChip, MacroRing, PantryItemCard…)
├── shared/domain/                # StorageTier · MeasurementUnit · NutritionInfo · Expiry · DietaryPreference · Paginated
└── features/                     # auth · onboarding · home · pantry · catalog · ingest · suggestions · dishes ·
                                  # cooking · nutrition · meal_plan · shopping_list · notifications · reports ·
                                  # subscription · settings   (đa số còn là stub, làm dần theo milestone)
assets/mock/                      # fixture JSON cho MockApiClient
config/                           # dev.json · prod.json
```

Quy tắc:
- Screen/widget nói chuyện với **controller Riverpod** (`@riverpod`), không gọi Dio / prefs trực tiếp.
- Feature chỉ chạm API qua **repository**; repository trả `Either<Failure, T>` (dùng helper `guard()`), controller đổi thành `AsyncValue` cho UI.
- DTO (`*_dto.dart`, freezed + json) không đi thẳng vào UI — map về entity.
- Chuỗi text: qua **`context.l10n.<key>`** — key ở `lib/l10n/app_vi.arb` (nguồn) + `app_en.arb` (dịch), chạy `flutter gen-l10n`. Default `vi`; đổi English trong Cài đặt → Tùy chọn → Ngôn ngữ. Vài chuỗi data/nền còn tiếng Việt — xem M6.1 trong `IMPLEMENTATION_PLAN.md`.
- Màu ngữ nghĩa (hạn dùng, tầng bảo quản) đọc qua `Theme.of(context).extension<SweepColors>()` (hoặc `context.sweep`).

## Kiểm tra trước khi tạo PR

```powershell
cd src/frontend
dart format .
flutter analyze          # phải "No issues found!"
flutter test
```

Test đang ở mức tối thiểu (stub + mẫu); sẽ bổ sung unit/integration test theo milestone (xem `IMPLEMENTATION_PLAN.md` M6). `flutter analyze` hiện **sạch** — đừng làm hỏng.

## Build phát hành

```powershell
flutter build apk --release --dart-define-from-file=config/prod.json
flutter build appbundle --release --dart-define-from-file=config/prod.json
flutter build web --release --dart-define-from-file=config/prod.json
```

Artifact nằm trong `build/` (không commit). Trước khi phát hành: đổi `applicationId` mặc định `com.example.frontend` + nhãn app + ký release trong `android/app/build.gradle.kts`, cập nhật `web/manifest.json`, đổi tên package `frontend` → `sweep_food` nếu muốn (kế hoạch: M6).
