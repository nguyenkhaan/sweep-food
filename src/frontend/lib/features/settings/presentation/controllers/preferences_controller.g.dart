// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'preferences_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// P-03 Tùy chọn. Reads/writes SharedPreferences. Dietary preference is
/// delegated to [DietaryPreferenceController] (shared with onboarding A-05 and
/// the suggestion scorer) so there's a single source of truth.

@ProviderFor(PreferencesController)
final preferencesControllerProvider = PreferencesControllerProvider._();

/// P-03 Tùy chọn. Reads/writes SharedPreferences. Dietary preference is
/// delegated to [DietaryPreferenceController] (shared with onboarding A-05 and
/// the suggestion scorer) so there's a single source of truth.
final class PreferencesControllerProvider
    extends $NotifierProvider<PreferencesController, AppPreferences> {
  /// P-03 Tùy chọn. Reads/writes SharedPreferences. Dietary preference is
  /// delegated to [DietaryPreferenceController] (shared with onboarding A-05 and
  /// the suggestion scorer) so there's a single source of truth.
  PreferencesControllerProvider._()
      : super(
          from: null,
          argument: null,
          retry: null,
          name: r'preferencesControllerProvider',
          isAutoDispose: false,
          dependencies: null,
          $allTransitiveDependencies: null,
        );

  @override
  String debugGetCreateSourceHash() => _$preferencesControllerHash();

  @$internal
  @override
  PreferencesController create() => PreferencesController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AppPreferences value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AppPreferences>(value),
    );
  }
}

String _$preferencesControllerHash() =>
    r'b5b2555e0a029a5fde083f9567f13065b92eeab9';

/// P-03 Tùy chọn. Reads/writes SharedPreferences. Dietary preference is
/// delegated to [DietaryPreferenceController] (shared with onboarding A-05 and
/// the suggestion scorer) so there's a single source of truth.

abstract class _$PreferencesController extends $Notifier<AppPreferences> {
  AppPreferences build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AppPreferences, AppPreferences>;
    final element = ref.element as $ClassProviderElement<
        AnyNotifier<AppPreferences, AppPreferences>,
        AppPreferences,
        Object?,
        Object?>;
    element.handleCreate(ref, build);
  }
}
