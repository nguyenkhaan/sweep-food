import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/cooking/data/models/cook_result_dto.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooked_food.dart';

/// Talks to `/dishes/{id}/cook` and `/pantry/cooked-food`. Throws on failure.
class CookingRemoteDataSource {
  CookingRemoteDataSource(this._api);

  final ApiClient _api;

  Future<CookResultDto> cook(CookConfirmation confirmation) async {
    final json = await _api.post(
      ApiPaths.cookDish(confirmation.dishId),
      body: confirmation.toBody(),
    );
    return CookResultDto.fromJson(json as Map<String, dynamic>);
  }

  /// Returns the created batch id (the mock echoes the body with an `id`).
  Future<String> saveLeftover(CookedFood food) async {
    final json = await _api.post(ApiPaths.cookedFood, body: food.toBody());
    final id = json is Map ? json['id']?.toString() : null;
    return id ?? 'cooked-${DateTime.now().millisecondsSinceEpoch}';
  }
}
