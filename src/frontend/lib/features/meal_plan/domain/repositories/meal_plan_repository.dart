import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/meal_plan/domain/entities/meal_plan.dart';

abstract interface class MealPlanRepository {
  /// `GET /meal-plans?weekStart=` (yyyy-MM-dd).
  Future<Result<MealPlan>> forWeek(DateTime weekStart);

  /// `PUT /meal-plans/{weekStart}` — the frontend sends the whole plan.
  Future<Result<MealPlan>> save(MealPlan plan);
}
