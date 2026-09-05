import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan_entry.dart';

abstract interface class MealPlanRepository {
  /// Finds (or creates) the plan covering the Monday-anchored week
  /// [weekStart] and returns it with its items.
  Future<Result<MealPlan>> forWeek(DateTime weekStart);

  /// `POST /meal-plans/{id}/items` — assigns a dish to an empty cell.
  Future<Result<MealPlanEntry>> addEntry({
    required DateTime weekStart,
    required DateTime date,
    required MealSlot slot,
    required String dishId,
    required double servings,
    String? dishName,
    String? dishImageUrl,
  });

  /// `PATCH /meal-plans/{id}/items/{item_id}` — reassigns an already-filled
  /// cell to a different dish/serving count (keeps the item's identity and
  /// status instead of delete+recreate).
  Future<Result<MealPlanEntry>> updateEntry({
    required DateTime weekStart,
    required String itemId,
    required String dishId,
    required double servings,
    String? dishName,
    String? dishImageUrl,
  });

  /// `DELETE /meal-plans/{id}/items/{item_id}`.
  Future<Result<void>> removeEntry({
    required DateTime weekStart,
    required String itemId,
  });
}
