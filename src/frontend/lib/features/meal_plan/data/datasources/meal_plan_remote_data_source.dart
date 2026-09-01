import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/meal_plan/data/models/meal_plan_dto.dart';

/// Talks to `/meal-plans`. Throws on failure — the repository maps.
class MealPlanRemoteDataSource {
  MealPlanRemoteDataSource(this._api);

  final ApiClient _api;

  static String _key(DateTime weekStart) =>
      '${weekStart.year.toString().padLeft(4, '0')}-'
      '${weekStart.month.toString().padLeft(2, '0')}-'
      '${weekStart.day.toString().padLeft(2, '0')}';

  Future<MealPlanDto> forWeek(DateTime weekStart) async {
    final json = await _api.get(
      ApiPaths.mealPlans,
      query: {'week_start': _key(weekStart)},
    );
    final map = json is List ? json.first : json;
    return MealPlanDto.fromJson(map as Map<String, dynamic>);
  }

  Future<MealPlanDto> save(MealPlanDto plan) async {
    final json = await _api.put(
      ApiPaths.mealPlan(_key(plan.weekStart)),
      body: plan.toJson(),
    );
    return MealPlanDto.fromJson(json as Map<String, dynamic>);
  }
}
