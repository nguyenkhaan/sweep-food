import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/utils/idempotency.dart';
import 'package:sweepfood/features/cooking/data/models/cooked_leftover_dto.dart';
import 'package:sweepfood/features/cooking/data/models/cooking_preview_dto.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooked_food.dart';

/// Talks to `/cooking/*`. Throws on failure — the repository maps.
/// See `docs/api-contract.md` §6.
class CookingRemoteDataSource {
  CookingRemoteDataSource(this._api);

  final ApiClient _api;

  Future<CookingPreviewResponseDto> preview(String mealPlanItemId) async {
    final json = await _api.post(
      ApiPaths.cookingPreview,
      body: {'meal_plan_item_id': mealPlanItemId},
    );
    return CookingPreviewResponseDto.fromJson(json as Map<String, dynamic>);
  }

  /// Returns the created session id. The backend responds 409 (surfaced as a
  /// generic [Failure] by `error_mapper.dart`) when the recipe's ingredients
  /// no longer match — callers should check `preview.hasMissingIngredients`
  /// beforehand to avoid relying on that.
  Future<String> createSession(String mealPlanItemId) async {
    final json = await _api.post(
      ApiPaths.cookingSessions,
      body: {'meal_plan_item_id': mealPlanItemId},
    );
    return (json as Map<String, dynamic>)['id'] as String;
  }

  Future<void> completeSession(
    String sessionId,
    CookMode mode,
    List<ConsumptionLine>? consumptions,
  ) =>
      _api.post(
        ApiPaths.cookingSessionComplete(sessionId),
        body: {
          'consumption_mode': mode.wire,
          if (consumptions != null)
            'consumptions': [for (final c in consumptions) c.toBody()],
        },
        headers: {'Idempotency-Key': Idempotency.newKey()},
      );

  Future<CookedLeftoverDto> saveLeftover(CookedFood food) async {
    final json = await _api.post(
      ApiPaths.cookingSessionLeftovers(food.sessionId),
      body: food.toBody(),
    );
    return CookedLeftoverDto.fromJson(json as Map<String, dynamic>);
  }
}
