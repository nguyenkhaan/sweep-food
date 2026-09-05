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

/// M-01 weekly grid. Re-fetches when the week changes. Assigning an empty
/// cell creates a new `meal-plans/{id}/items` row; re-assigning a filled one
/// PATCHes the existing item instead (keeps its id/status); clearing DELETEs
/// it. Failures roll back by refetching from the server.
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
    required double servings,
    String? dishName,
    String? dishImageUrl,
  }) async {
    final plan = state.asData?.value;
    if (plan == null) return;
    final existing = plan.entryAt(date, slot);

    ref.read(analyticsProvider).log(
      AnalyticsEvents.mealPlanEntryAdded,
      {AnalyticsParams.dishId: dishId},
    );

    final repo = ref.read(mealPlanRepositoryProvider);
    final res = existing == null
        ? await repo.addEntry(
            weekStart: plan.weekStart,
            date: date,
            slot: slot,
            dishId: dishId,
            servings: servings,
            dishName: dishName,
            dishImageUrl: dishImageUrl,
          )
        : await repo.updateEntry(
            weekStart: plan.weekStart,
            itemId: existing.id,
            dishId: dishId,
            servings: servings,
            dishName: dishName,
            dishImageUrl: dishImageUrl,
          );

    res.fold(
      (_) => ref.invalidateSelf(),
      (entry) => state = AsyncData(plan.withEntry(entry)),
    );
  }

  Future<void> clear(DateTime date, MealSlot slot) async {
    final plan = state.asData?.value;
    if (plan == null) return;
    final entry = plan.entryAt(date, slot);
    if (entry == null) return;

    state = AsyncData(plan.withoutEntry(date, slot)); // optimistic
    final res = await ref
        .read(mealPlanRepositoryProvider)
        .removeEntry(weekStart: plan.weekStart, itemId: entry.id);
    res.fold((_) => ref.invalidateSelf(), (_) {});
  }
}
