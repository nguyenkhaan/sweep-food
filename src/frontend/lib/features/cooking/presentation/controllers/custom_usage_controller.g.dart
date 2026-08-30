// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'custom_usage_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// D-04 — per-ingredient "how much did you actually use" sliders, keyed by dish.
/// Seeded from the scaled recipe amounts; the sheet edits each entry.

@ProviderFor(CustomUsageController)
final customUsageControllerProvider = CustomUsageControllerFamily._();

/// D-04 — per-ingredient "how much did you actually use" sliders, keyed by dish.
/// Seeded from the scaled recipe amounts; the sheet edits each entry.
final class CustomUsageControllerProvider
    extends $NotifierProvider<CustomUsageController, Map<String, double>> {
  /// D-04 — per-ingredient "how much did you actually use" sliders, keyed by dish.
  /// Seeded from the scaled recipe amounts; the sheet edits each entry.
  CustomUsageControllerProvider._(
      {required CustomUsageControllerFamily super.from,
      required String super.argument})
      : super(
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
    r'516b7c8b4d5744d11191d0cb0699a788bcef288e';

/// D-04 — per-ingredient "how much did you actually use" sliders, keyed by dish.
/// Seeded from the scaled recipe amounts; the sheet edits each entry.

final class CustomUsageControllerFamily extends $Family
    with
        $ClassFamilyOverride<CustomUsageController, Map<String, double>,
            Map<String, double>, Map<String, double>, String> {
  CustomUsageControllerFamily._()
      : super(
          retry: null,
          name: r'customUsageControllerProvider',
          dependencies: null,
          $allTransitiveDependencies: null,
          isAutoDispose: true,
        );

  /// D-04 — per-ingredient "how much did you actually use" sliders, keyed by dish.
  /// Seeded from the scaled recipe amounts; the sheet edits each entry.

  CustomUsageControllerProvider call(
    String dishId,
  ) =>
      CustomUsageControllerProvider._(argument: dishId, from: this);

  @override
  String toString() => r'customUsageControllerProvider';
}

/// D-04 — per-ingredient "how much did you actually use" sliders, keyed by dish.
/// Seeded from the scaled recipe amounts; the sheet edits each entry.

abstract class _$CustomUsageController extends $Notifier<Map<String, double>> {
  late final _$args = ref.$arg as String;
  String get dishId => _$args;

  Map<String, double> build(
    String dishId,
  );
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<Map<String, double>, Map<String, double>>;
    final element = ref.element as $ClassProviderElement<
        AnyNotifier<Map<String, double>, Map<String, double>>,
        Map<String, double>,
        Object?,
        Object?>;
    element.handleCreate(
        ref,
        () => build(
              _$args,
            ));
  }
}
