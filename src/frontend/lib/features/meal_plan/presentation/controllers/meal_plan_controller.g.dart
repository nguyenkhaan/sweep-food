// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'meal_plan_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// The Monday of the week shown in M-01. `‹ / ›` step it by 7 days.

@ProviderFor(MealPlanWeekStart)
final mealPlanWeekStartProvider = MealPlanWeekStartProvider._();

/// The Monday of the week shown in M-01. `‹ / ›` step it by 7 days.
final class MealPlanWeekStartProvider
    extends $NotifierProvider<MealPlanWeekStart, DateTime> {
  /// The Monday of the week shown in M-01. `‹ / ›` step it by 7 days.
  MealPlanWeekStartProvider._()
      : super(
          from: null,
          argument: null,
          retry: null,
          name: r'mealPlanWeekStartProvider',
          isAutoDispose: true,
          dependencies: null,
          $allTransitiveDependencies: null,
        );

  @override
  String debugGetCreateSourceHash() => _$mealPlanWeekStartHash();

  @$internal
  @override
  MealPlanWeekStart create() => MealPlanWeekStart();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(DateTime value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<DateTime>(value),
    );
  }
}

String _$mealPlanWeekStartHash() => r'dd01d966b129ef67723fdde5090896194170bc9a';

/// The Monday of the week shown in M-01. `‹ / ›` step it by 7 days.

abstract class _$MealPlanWeekStart extends $Notifier<DateTime> {
  DateTime build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<DateTime, DateTime>;
    final element = ref.element as $ClassProviderElement<
        AnyNotifier<DateTime, DateTime>, DateTime, Object?, Object?>;
    element.handleCreate(ref, build);
  }
}

/// M-01 weekly grid. Re-fetches when the week changes; assign / clear update
/// optimistically and persist via `PUT /meal-plans/{weekStart}`.

@ProviderFor(MealPlanController)
final mealPlanControllerProvider = MealPlanControllerProvider._();

/// M-01 weekly grid. Re-fetches when the week changes; assign / clear update
/// optimistically and persist via `PUT /meal-plans/{weekStart}`.
final class MealPlanControllerProvider
    extends $AsyncNotifierProvider<MealPlanController, MealPlan> {
  /// M-01 weekly grid. Re-fetches when the week changes; assign / clear update
  /// optimistically and persist via `PUT /meal-plans/{weekStart}`.
  MealPlanControllerProvider._()
      : super(
          from: null,
          argument: null,
          retry: null,
          name: r'mealPlanControllerProvider',
          isAutoDispose: true,
          dependencies: null,
          $allTransitiveDependencies: null,
        );

  @override
  String debugGetCreateSourceHash() => _$mealPlanControllerHash();

  @$internal
  @override
  MealPlanController create() => MealPlanController();
}

String _$mealPlanControllerHash() =>
    r'f40939e2ffaf8ae06895ba0299103716dbfac80a';

/// M-01 weekly grid. Re-fetches when the week changes; assign / clear update
/// optimistically and persist via `PUT /meal-plans/{weekStart}`.

abstract class _$MealPlanController extends $AsyncNotifier<MealPlan> {
  FutureOr<MealPlan> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<MealPlan>, MealPlan>;
    final element = ref.element as $ClassProviderElement<
        AnyNotifier<AsyncValue<MealPlan>, MealPlan>,
        AsyncValue<MealPlan>,
        Object?,
        Object?>;
    element.handleCreate(ref, build);
  }
}
