// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'custom_usage_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// D-04 — per-batch "how much did you actually use" sliders, keyed by
/// `recipe_ingredient_id|batch_id` (a recipe ingredient can be split across
/// more than one matched batch). Seeded from the preview's proposed
/// deductions; the sheet edits each entry.

@ProviderFor(CustomUsageController)
final customUsageControllerProvider = CustomUsageControllerFamily._();

/// D-04 — per-batch "how much did you actually use" sliders, keyed by
/// `recipe_ingredient_id|batch_id` (a recipe ingredient can be split across
/// more than one matched batch). Seeded from the preview's proposed
/// deductions; the sheet edits each entry.
final class CustomUsageControllerProvider
    extends $NotifierProvider<CustomUsageController, Map<String, double>> {
  /// D-04 — per-batch "how much did you actually use" sliders, keyed by
  /// `recipe_ingredient_id|batch_id` (a recipe ingredient can be split across
  /// more than one matched batch). Seeded from the preview's proposed
  /// deductions; the sheet edits each entry.
  CustomUsageControllerProvider._({
    required CustomUsageControllerFamily super.from,
    required CookingPreview super.argument,
  }) : super(
         retry: null,
         name: r'customUsageControllerProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$customUsageControllerHash();

  @override
  String toString() {
    return r'customUsageControllerProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  CustomUsageController create() => CustomUsageController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(Map<String, double> value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<Map<String, double>>(value),
    );
  }

  @override
  bool operator ==(Object other) {
    return other is CustomUsageControllerProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$customUsageControllerHash() =>
    r'5c1769af6e1aa3b2efa083aa5f6f12802fb57511';

/// D-04 — per-batch "how much did you actually use" sliders, keyed by
/// `recipe_ingredient_id|batch_id` (a recipe ingredient can be split across
/// more than one matched batch). Seeded from the preview's proposed
/// deductions; the sheet edits each entry.

final class CustomUsageControllerFamily extends $Family
    with
        $ClassFamilyOverride<
          CustomUsageController,
          Map<String, double>,
          Map<String, double>,
          Map<String, double>,
          CookingPreview
        > {
  CustomUsageControllerFamily._()
    : super(
        retry: null,
        name: r'customUsageControllerProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// D-04 — per-batch "how much did you actually use" sliders, keyed by
  /// `recipe_ingredient_id|batch_id` (a recipe ingredient can be split across
  /// more than one matched batch). Seeded from the preview's proposed
  /// deductions; the sheet edits each entry.

  CustomUsageControllerProvider call(CookingPreview preview) =>
      CustomUsageControllerProvider._(argument: preview, from: this);

  @override
  String toString() => r'customUsageControllerProvider';
}

/// D-04 — per-batch "how much did you actually use" sliders, keyed by
/// `recipe_ingredient_id|batch_id` (a recipe ingredient can be split across
/// more than one matched batch). Seeded from the preview's proposed
/// deductions; the sheet edits each entry.

abstract class _$CustomUsageController extends $Notifier<Map<String, double>> {
  late final _$args = ref.$arg as CookingPreview;
  CookingPreview get preview => _$args;

  Map<String, double> build(CookingPreview preview);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<Map<String, double>, Map<String, double>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<Map<String, double>, Map<String, double>>,
              Map<String, double>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}
