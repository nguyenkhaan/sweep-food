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

  Future<RecipeListResponseDto> searchRecipes({
    String? query,
    String? tag,
    int? maxCookingMinutes,
    int page = 1,
    int perPage = 20,
  }) async {
    final json = await _api.get(
      ApiPaths.recipes,
      query: {
        if (query != null && query.isNotEmpty) 'q': query,
        if (tag != null && tag.isNotEmpty) 'tag': tag,
        if (maxCookingMinutes != null) 'max_cooking_minutes': maxCookingMinutes,
        'page': page,
        'per_page': perPage,
      },
    );
    return RecipeListResponseDto.fromJson(json as Map<String, dynamic>);
  }
}
