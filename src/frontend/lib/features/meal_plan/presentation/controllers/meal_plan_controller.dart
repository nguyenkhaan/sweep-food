import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/analytics/analytics_events.dart';
import 'package:sweepfood/core/analytics/analytics_provider.dart';
import 'package:sweepfood/features/meal_plan/data/repositories/meal_plan_repository_impl.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan_entry.dart';

part 'meal_plan_controller.g.dart';

/// The Monday of the week shown in M-01. `‹ / ›` step it by 7 days.
@riverpod
class MealPlanWeekStart extends _$MealPlanWeekStart {
  @override
  DateTime build() => MealPlan.weekStartOf(DateTime.now());

  void next() => state = state.add(const Duration(days: 7));
  void previous() => state = state.subtract(const Duration(days: 7));
  void thisWeek() => state = MealPlan.weekStartOf(DateTime.now());
}

/// M-01 weekly grid. Re-fetches when the week changes; assign / clear update
/// optimistically and persist via `PUT /meal-plans/{weekStart}`.
@riverpod
class MealPlanController extends _$MealPlanController {
  @override
  Future<MealPlan> build() async {
    final weekStart = ref.watch(mealPlanWeekStartProvider);
    final res = await ref.watch(mealPlanRepositoryProvider).forWeek(weekStart);
    return res.fold((f) => throw f, (plan) => plan);
  }

  Future<void> assign({
    required DateTime date,
    required MealSlot slot,
    required String dishId,
    String? dishName,
    String? dishImageUrl,
  }) async {
    final plan = state.asData?.value;
    if (plan == null) return;
    final next = plan.withEntry(
      MealPlanEntry(
        date: date,
        slot: slot,
        dishId: dishId,
        dishName: dishName,
        dishImageUrl: dishImageUrl,
      ),
    );
    state = AsyncData(next);
    ref.read(analyticsProvider).log(
      AnalyticsEvents.mealPlanEntryAdded,
      {AnalyticsParams.dishId: dishId},
    );
    final res = await ref.read(mealPlanRepositoryProvider).save(next);
    res.fold((_) => ref.invalidateSelf(), (_) {});
  }

  Future<void> clear(DateTime date, MealSlot slot) async {
    final plan = state.asData?.value;
    if (plan == null) return;
    final next = plan.withoutEntry(date, slot);
    state = AsyncData(next);
    final res = await ref.read(mealPlanRepositoryProvider).save(next);
    res.fold((_) => ref.invalidateSelf(), (_) {});
  }
}
