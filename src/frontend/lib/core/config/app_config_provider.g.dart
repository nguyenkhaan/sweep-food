// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_config_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// The app-wide [AppConfig]. Overridden in `bootstrap()` with the instance read
/// from `--dart-define`; the fallback here keeps tests / previews working.

@ProviderFor(appConfig)
final appConfigProvider = AppConfigProvider._();

/// The app-wide [AppConfig]. Overridden in `bootstrap()` with the instance read
/// from `--dart-define`; the fallback here keeps tests / previews working.

final class AppConfigProvider
    extends $FunctionalProvider<AppConfig, AppConfig, AppConfig>
    with $Provider<AppConfig> {
  /// The app-wide [AppConfig]. Overridden in `bootstrap()` with the instance read
  /// from `--dart-define`; the fallback here keeps tests / previews working.
  AppConfigProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'appConfigProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$appConfigHash();

  @$internal
  @override
  $ProviderElement<AppConfig> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  AppConfig create(Ref ref) {
    return appConfig(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AppConfig value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AppConfig>(value),
    );
  }
}

String _$appConfigHash() => r'87f9d20a2d92252672162b2ce97547b7b2479239';
