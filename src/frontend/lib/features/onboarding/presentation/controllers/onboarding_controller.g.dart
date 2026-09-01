// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'onboarding_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Whether the user has finished (or skipped) onboarding. Persisted so it
/// survives a logout/login on the same device. Watched by `route_guards.dart`:
/// a signed-in user with `false` here is pinned to `/onboarding/diet`.

@ProviderFor(OnboardingController)
final onboardingControllerProvider = OnboardingControllerProvider._();

/// Whether the user has finished (or skipped) onboarding. Persisted so it
/// survives a logout/login on the same device. Watched by `route_guards.dart`:
/// a signed-in user with `false` here is pinned to `/onboarding/diet`.
final class OnboardingControllerProvider
    extends $NotifierProvider<OnboardingController, bool> {
  /// Whether the user has finished (or skipped) onboarding. Persisted so it
  /// survives a logout/login on the same device. Watched by `route_guards.dart`:
  /// a signed-in user with `false` here is pinned to `/onboarding/diet`.
  OnboardingControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'onboardingControllerProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$onboardingControllerHash();

  @$internal
  @override
  OnboardingController create() => OnboardingController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(bool value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<bool>(value),
    );
  }
}

String _$onboardingControllerHash() =>
    r'46e28a716242e5b75972570312da3571c246e757';

/// Whether the user has finished (or skipped) onboarding. Persisted so it
/// survives a logout/login on the same device. Watched by `route_guards.dart`:
/// a signed-in user with `false` here is pinned to `/onboarding/diet`.

abstract class _$OnboardingController extends $Notifier<bool> {
  bool build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<bool, bool>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<bool, bool>,
              bool,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

/// The persisted meal-ranking preference (N-01). Chosen at onboarding (A-05),
/// later editable in Cài đặt → Tùy chọn. Feeds the `P` term of suggestion
/// scoring — `SuggestionFilterController` seeds its default from here.

@ProviderFor(DietaryPreferenceController)
final dietaryPreferenceControllerProvider =
    DietaryPreferenceControllerProvider._();

/// The persisted meal-ranking preference (N-01). Chosen at onboarding (A-05),
/// later editable in Cài đặt → Tùy chọn. Feeds the `P` term of suggestion
/// scoring — `SuggestionFilterController` seeds its default from here.
final class DietaryPreferenceControllerProvider
    extends $NotifierProvider<DietaryPreferenceController, DietaryPreference?> {
  /// The persisted meal-ranking preference (N-01). Chosen at onboarding (A-05),
  /// later editable in Cài đặt → Tùy chọn. Feeds the `P` term of suggestion
  /// scoring — `SuggestionFilterController` seeds its default from here.
  DietaryPreferenceControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'dietaryPreferenceControllerProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$dietaryPreferenceControllerHash();

  @$internal
  @override
  DietaryPreferenceController create() => DietaryPreferenceController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(DietaryPreference? value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<DietaryPreference?>(value),
    );
  }
}

String _$dietaryPreferenceControllerHash() =>
    r'2662bb7d4dca5a4fdf456209f238bee38fc15067';

/// The persisted meal-ranking preference (N-01). Chosen at onboarding (A-05),
/// later editable in Cài đặt → Tùy chọn. Feeds the `P` term of suggestion
/// scoring — `SuggestionFilterController` seeds its default from here.

abstract class _$DietaryPreferenceController
    extends $Notifier<DietaryPreference?> {
  DietaryPreference? build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<DietaryPreference?, DietaryPreference?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<DietaryPreference?, DietaryPreference?>,
              DietaryPreference?,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
