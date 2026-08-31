// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'locale_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// App UI language, persisted to SharedPreferences. Read by [MaterialApp.router]
/// in `app.dart`; changed from Cài đặt → Tùy chọn → Ngôn ngữ.
///
/// Defaults to Vietnamese (the MVP language). English is opt-in and some
/// data-layer strings still fall back to `vi` (see IMPLEMENTATION_PLAN.md M6.1).

@ProviderFor(LocaleController)
final localeControllerProvider = LocaleControllerProvider._();

/// App UI language, persisted to SharedPreferences. Read by [MaterialApp.router]
/// in `app.dart`; changed from Cài đặt → Tùy chọn → Ngôn ngữ.
///
/// Defaults to Vietnamese (the MVP language). English is opt-in and some
/// data-layer strings still fall back to `vi` (see IMPLEMENTATION_PLAN.md M6.1).
final class LocaleControllerProvider
    extends $NotifierProvider<LocaleController, Locale> {
  /// App UI language, persisted to SharedPreferences. Read by [MaterialApp.router]
  /// in `app.dart`; changed from Cài đặt → Tùy chọn → Ngôn ngữ.
  ///
  /// Defaults to Vietnamese (the MVP language). English is opt-in and some
  /// data-layer strings still fall back to `vi` (see IMPLEMENTATION_PLAN.md M6.1).
  LocaleControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'localeControllerProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$localeControllerHash();

  @$internal
  @override
  LocaleController create() => LocaleController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(Locale value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<Locale>(value),
    );
  }
}

String _$localeControllerHash() => r'ec44c1c275997617a7a49fe0d3d1e33b322d6342';

/// App UI language, persisted to SharedPreferences. Read by [MaterialApp.router]
/// in `app.dart`; changed from Cài đặt → Tùy chọn → Ngôn ngữ.
///
/// Defaults to Vietnamese (the MVP language). English is opt-in and some
/// data-layer strings still fall back to `vi` (see IMPLEMENTATION_PLAN.md M6.1).

abstract class _$LocaleController extends $Notifier<Locale> {
  Locale build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<Locale, Locale>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<Locale, Locale>,
              Locale,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
