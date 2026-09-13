import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/meal_plan/data/models/meal_plan_dto.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan_entry.dart';

/// Talks to `/meal-plans`. Throws on failure — the repository maps.
/// See `docs/api-contract.md` §7.
class MealPlanRemoteDataSource {
  MealPlanRemoteDataSource(this._api);

  final ApiClient _api;

  static String dateOnly(DateTime d) =>
      '${d.year.toString().padLeft(4, '0')}-'
      '${d.month.toString().padLeft(2, '0')}-'
      '${d.day.toString().padLeft(2, '0')}';

  /// No backend equivalent of "list all my plans, most recent first" beyond
  /// this — fetched at the backend's max page size so a returning user's
  /// current week is very likely on the first page (see repository for the
  /// caveat).
  Future<List<MealPlanDto>> listPlans() async {
    final json = await _api.get(ApiPaths.mealPlansList, query: {'limit': 100});
    final items = (json is Map ? json['items'] : json) as List<dynamic>;
    return items
        .map((e) => MealPlanDto.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<MealPlanDto> createPlan({
    required DateTime startsOn,
    required DateTime endsOn,
  }) async {
    final json = await _api.post(
      ApiPaths.mealPlans,
      body: {'starts_on': dateOnly(startsOn), 'ends_on': dateOnly(endsOn)},
    );
    return MealPlanDto.fromJson(json as Map<String, dynamic>);
  }

  Future<MealPlanDto> getPlan(String id) async {
    final json = await _api.get(ApiPaths.mealPlan(id));
    return MealPlanDto.fromJson(json as Map<String, dynamic>);
  }

  Future<MealPlanItemDto> addItem(
    String planId, {
    required String recipeId,
    required DateTime plannedFor,
    required MealSlot slot,
    required double servings,
  }) async {
    final json = await _api.post(
      ApiPaths.mealPlanItems(planId),
      body: {
        'recipe_id': recipeId,
        'planned_for': dateOnly(plannedFor),
        'meal_slot': slot.wire,
        'servings': servings,
      },
    );
    return MealPlanItemDto.fromJson(json as Map<String, dynamic>);
  }

  Future<MealPlanItemDto> updateItem(
    String planId,
    String itemId, {
    required String recipeId,
    required double servings,
  }) async {
    final json = await _api.patch(
      ApiPaths.mealPlanItem(planId, itemId),
      body: {'recipe_id': recipeId, 'servings': servings},
    );
    return MealPlanItemDto.fromJson(json as Map<String, dynamic>);
  }

  Future<void> deleteItem(String planId, String itemId) =>
      _api.delete(ApiPaths.mealPlanItem(planId, itemId));
}
