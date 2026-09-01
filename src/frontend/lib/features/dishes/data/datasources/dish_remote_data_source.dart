import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/dishes/data/models/recipe_dto.dart';

/// Reads the full recipe for the Dish detail screen from the real backend
/// (`GET /recipes/{id}`). Throws on failure — the repository catches and maps.
class DishRemoteDataSource {
  DishRemoteDataSource(this._api);

  final ApiClient _api;

  Future<RecipeDto> getById(String id) async {
    final json = await _api.get(ApiPaths.recipe(id));
    return RecipeDto.fromJson(json as Map<String, dynamic>);
  }
}
