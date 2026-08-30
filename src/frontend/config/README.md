# Run configs

Run with:

```
flutter run --dart-define-from-file=config/dev.json
```

`AppConfig` (lib/core/config/app_config.dart) reads these keys.
`BACKEND=mock` makes the app use `MockApiClient` (assets/mock/*.json); `live` uses Dio.
`PREMIUM_ENABLED=false` for the MVP (all features unlocked, no gating).
