// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'nutrition_profile_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Manages editing & saving the 5-field Nutrition Profile via `PATCH /users/profile`.

@ProviderFor(NutritionProfileController)
final nutritionProfileControllerProvider =
    NutritionProfileControllerProvider._();

/// Manages editing & saving the 5-field Nutrition Profile via `PATCH /users/profile`.
final class NutritionProfileControllerProvider
    extends
        $NotifierProvider<
          NutritionProfileController,
          NutritionProfileFormState
        > {
  /// Manages editing & saving the 5-field Nutrition Profile via `PATCH /users/profile`.
  NutritionProfileControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'nutritionProfileControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$nutritionProfileControllerHash();

  @$internal
  @override
  NutritionProfileController create() => NutritionProfileController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(NutritionProfileFormState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<NutritionProfileFormState>(value),
    );
  }
}

String _$nutritionProfileControllerHash() =>
    r'df242fca2e10c80f20818a469615064f87d72372';

/// Manages editing & saving the 5-field Nutrition Profile via `PATCH /users/profile`.

abstract class _$NutritionProfileController
    extends $Notifier<NutritionProfileFormState> {
  NutritionProfileFormState build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<NutritionProfileFormState, NutritionProfileFormState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<NutritionProfileFormState, NutritionProfileFormState>,
              NutritionProfileFormState,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
