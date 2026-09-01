// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'dish_detail_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Loads the full recipe once (`GET /dishes/{id}`). Kept at the base serving
/// count — [scaledDish] applies the user's choice from [DishServings].

@ProviderFor(dishById)
final dishByIdProvider = DishByIdFamily._();

/// Loads the full recipe once (`GET /dishes/{id}`). Kept at the base serving
/// count — [scaledDish] applies the user's choice from [DishServings].

final class DishByIdProvider
    extends $FunctionalProvider<AsyncValue<Dish>, Dish, FutureOr<Dish>>
    with $FutureModifier<Dish>, $FutureProvider<Dish> {
  /// Loads the full recipe once (`GET /dishes/{id}`). Kept at the base serving
  /// count — [scaledDish] applies the user's choice from [DishServings].
  DishByIdProvider._({
    required DishByIdFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'dishByIdProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$dishByIdHash();

  @override
  String toString() {
    return r'dishByIdProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<Dish> $createElement($ProviderPointer pointer) =>
      $FutureProviderElement(pointer);

  @override
  FutureOr<Dish> create(Ref ref) {
    final argument = this.argument as String;
    return dishById(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is DishByIdProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$dishByIdHash() => r'90ea8cd3a4e0ad4d5c442d7fb25a9c2a5796beb6';

/// Loads the full recipe once (`GET /dishes/{id}`). Kept at the base serving
/// count — [scaledDish] applies the user's choice from [DishServings].

final class DishByIdFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<Dish>, String> {
  DishByIdFamily._()
    : super(
        retry: null,
        name: r'dishByIdProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Loads the full recipe once (`GET /dishes/{id}`). Kept at the base serving
  /// count — [scaledDish] applies the user's choice from [DishServings].

  DishByIdProvider call(String dishId) =>
      DishByIdProvider._(argument: dishId, from: this);

  @override
  String toString() => r'dishByIdProvider';
}

/// The serving count chosen on the D-01 stepper. `null` = "use the recipe's own".

@ProviderFor(DishServings)
final dishServingsProvider = DishServingsFamily._();

/// The serving count chosen on the D-01 stepper. `null` = "use the recipe's own".
final class DishServingsProvider extends $NotifierProvider<DishServings, int?> {
  /// The serving count chosen on the D-01 stepper. `null` = "use the recipe's own".
  DishServingsProvider._({
    required DishServingsFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'dishServingsProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$dishServingsHash();

  @override
  String toString() {
    return r'dishServingsProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  DishServings create() => DishServings();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(int? value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<int?>(value),
    );
  }

  @override
  bool operator ==(Object other) {
    return other is DishServingsProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$dishServingsHash() => r'c90198a74ae1111def0c71fda5019a9e5f702e7a';

/// The serving count chosen on the D-01 stepper. `null` = "use the recipe's own".

final class DishServingsFamily extends $Family
    with $ClassFamilyOverride<DishServings, int?, int?, int?, String> {
  DishServingsFamily._()
    : super(
        retry: null,
        name: r'dishServingsProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// The serving count chosen on the D-01 stepper. `null` = "use the recipe's own".

  DishServingsProvider call(String dishId) =>
      DishServingsProvider._(argument: dishId, from: this);

  @override
  String toString() => r'dishServingsProvider';
}

/// The serving count chosen on the D-01 stepper. `null` = "use the recipe's own".

abstract class _$DishServings extends $Notifier<int?> {
  late final _$args = ref.$arg as String;
  String get dishId => _$args;

  int? build(String dishId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<int?, int?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<int?, int?>,
              int?,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}

/// The recipe re-scaled to the chosen servings (quantities + nutrition).
/// Always derived from the base dish, so repeated changes don't drift.

@ProviderFor(scaledDish)
final scaledDishProvider = ScaledDishFamily._();

/// The recipe re-scaled to the chosen servings (quantities + nutrition).
/// Always derived from the base dish, so repeated changes don't drift.

final class ScaledDishProvider extends $FunctionalProvider<Dish?, Dish?, Dish?>
    with $Provider<Dish?> {
  /// The recipe re-scaled to the chosen servings (quantities + nutrition).
  /// Always derived from the base dish, so repeated changes don't drift.
  ScaledDishProvider._({
    required ScaledDishFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'scaledDishProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$scaledDishHash();

  @override
  String toString() {
    return r'scaledDishProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $ProviderElement<Dish?> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  Dish? create(Ref ref) {
    final argument = this.argument as String;
    return scaledDish(ref, argument);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(Dish? value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<Dish?>(value),
    );
  }

  @override
  bool operator ==(Object other) {
    return other is ScaledDishProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$scaledDishHash() => r'5b810b31193cd54b92f574457e4a9d226d5d28e5';

/// The recipe re-scaled to the chosen servings (quantities + nutrition).
/// Always derived from the base dish, so repeated changes don't drift.

final class ScaledDishFamily extends $Family
    with $FunctionalFamilyOverride<Dish?, String> {
  ScaledDishFamily._()
    : super(
        retry: null,
        name: r'scaledDishProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// The recipe re-scaled to the chosen servings (quantities + nutrition).
  /// Always derived from the base dish, so repeated changes don't drift.

  ScaledDishProvider call(String dishId) =>
      ScaledDishProvider._(argument: dishId, from: this);

  @override
  String toString() => r'scaledDishProvider';
}
