---
name: sweepfood-flutter-feature
description: >-
  Implements, modifies, or tests Flutter frontend features in `src/frontend/`
  following SweepFood's exact Clean Architecture, Riverpod 3 codegen, Freezed,
  fpdart Either<Failure, T>, DioApiClient/MockApiClient, mocktail, and gen-l10n
  conventions. Use whenever creating or editing a feature, DTO, entity,
  repository, Riverpod controller, GoRouter route, API integration, or test in
  `src/frontend/`.
---

# SweepFood Flutter Feature Workflow

Follow these project-specific conventions for all work under `src/frontend/`.

## 1. Architecture & Layer Boundaries

SweepFood uses **feature-first Clean Architecture** under `src/frontend/lib/features/<feature>/`:

```text
lib/features/<feature>/
├── data/
│   ├── datasources/    # *_remote_data_source.dart (calls ApiClient only)
│   ├── models/         # *_dto.dart (freezed + json_serializable + toEntity())
│   └── repositories/   # *_repository_impl.dart (+ @Riverpod(keepAlive: true) provider)
├── domain/
│   ├── entities/       # pure immutable models (freezed or const Dart class)
│   ├── repositories/   # abstract interface class returning Future<Result<T>>
│   └── usecases/       # optional, only for multi-step domain orchestration
└── presentation/
    ├── controllers/    # @riverpod Notifier/AsyncNotifier controllers
    ├── screens/        # route-level screens
    └── widgets/        # feature-scoped reusable const widgets
```

**Non-negotiable boundaries:**
- Screens/widgets communicate **only** with Riverpod controllers (`@riverpod`). Never call `Dio`, `ApiClient`, `SharedPreferences`, or `FlutterSecureStorage` from UI code.
- Repositories are the single data boundary: they call data sources, wrap errors via `runGuarded()` / `guard()` / `guardVoid()` (`package:sweepfood/core/network/api_result.dart`), and return `Result<T>` (`Either<Failure, T>` from `package:sweepfood/core/utils/result.dart`).
- **DTOs never leak into UI.** Always map `*_dto.dart` → domain entity via `.toEntity()` inside the repository implementation.
- Check `docs/api-contract.md` before changing request/response wire shapes.

## 2. Models & Serialization (`freezed` + `json_serializable`)

- Declare DTOs as `@freezed abstract class FooDto with _$FooDto` with `const FooDto._();` so `.toEntity()` methods can live on the class.
- Map backend `snake_case` fields explicitly with `@JsonKey(name: '...')`.
- Parse backend timestamps defensively (`DateTime.tryParse`, convert to `.toLocal()` when displaying).
- Add both `part '<file>.freezed.dart';` and `part '<file>.g.dart';` for JSON DTOs; only `part '<file>.freezed.dart';` for pure domain entities.
- Never hand-edit `*.freezed.dart` or `*.g.dart`.

## 3. Networking, Idempotency & Mock Parity

- All HTTP calls go through `ApiClient` (`ref.watch(apiClientProvider)`), never a raw `Dio` instance.
- All endpoints live in `lib/core/network/api_paths.dart`.
- **Write mutations (`POST` / `PATCH` / `DELETE`):** attach `Idempotency-Key: Idempotency.newKey()` (`package:sweepfood/core/utils/idempotency.dart`) when required by `docs/api-contract.md`.
- **HTTP headers must be pure ASCII** (e.g., `X-Reason: 'User deleted from inventory'`, never Vietnamese diacritics in headers, which causes Dio to throw `UnknownFailure` before sending).
- **Mock parity:** Whenever adding or changing an endpoint, update `lib/core/network/mock_api_client.dart` and the corresponding fixture in `assets/mock/*.json` so `BACKEND=mock` (`config/dev.json`) continues working end-to-end.

## 4. State Management (`riverpod_generator`, Riverpod 3.x)

- Use `@riverpod` (autoDispose default) for feature controllers and `@Riverpod(keepAlive: true)` for repositories / app-wide singletons.
- Never use legacy `StateProvider`, `StateNotifierProvider`, `ChangeNotifierProvider`, or `get_it`.
- Convert `Result<T>` to `AsyncValue` cleanly in controllers:
  ```dart
  final res = await repo.fetchItems();
  return res.fold((failure) => throw failure, (items) => items);
  ```
- In UI, prefer `AsyncValueWidget` (`package:sweepfood/core/widgets/async_value_widget.dart`) or exhaustive pattern matching on `AsyncValue`, rendering `Failure.localizedMessage(context.l10n)` instead of `error.toString()`.
- **Async safety:** Always check `if (!ref.mounted) return;` in controllers and `if (!context.mounted) return;` in widgets after any `await` before mutating state, navigating, or showing snackbars.
- Minimize rebuilds with `ref.watch(provider.select(...))` in widgets and `ref.read(provider.notifier)` in callbacks.

## 5. Routing, Localization & Lint Rules

- **Routing:** Register routes in `lib/app/router/` (`GoRouter` + `StatefulShellRoute` 5-tab shell). Pass IDs in path/query parameters rather than `state.extra` so deep links (including FCM notifications) survive cold start.
- **Localization:** Never hardcode user-visible strings in widgets. Add keys to **both** `lib/l10n/app_vi.arb` (source of truth) and `lib/l10n/app_en.arb`, run `flutter gen-l10n`, and access via `context.l10n.<key>`.
- **Lint rules (`analysis_options.yaml`):**
  - `prefer_single_quotes: true`
  - `always_use_package_imports: true` (always `package:sweepfood/...`, never relative `../`)
  - `require_trailing_commas: true`
  - `directives_ordering: true`

## 6. Testing Strategy (`mocktail`)

Use **`mocktail`** (not `mockito`) for test doubles:
- Unit tests (`test/unit/<feature>/`): test DTO parsing, repository `Result<T>` mapping, and controller state transitions via `ProviderContainer(overrides: [...])`.
- Widget tests (`test/widget/<feature>/`): verify loading/empty/error/data states and key interactions.
- Live API roundtrip tests (`test/live/`): add/update when wiring new backend endpoints.

## 7. Mandatory Verification Gate

Run from `src/frontend/` before finishing any feature or PR:

```powershell
dart run build_runner build --delete-conflicting-outputs
flutter gen-l10n
dart format .
flutter analyze          # must report "No issues found!"
flutter test
```
