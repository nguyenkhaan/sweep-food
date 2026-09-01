import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/catalog/data/models/ingredient_dto.dart';

class IngredientRemoteDataSource {
  IngredientRemoteDataSource(this._api);

  final ApiClient _api;

  Future<List<IngredientDto>> search(String query) async {
    final json = await _api.get(
      ApiPaths.ingredients,
      query: {if (query.trim().isNotEmpty) 'query': query.trim()},
    );
    final list = (json is Map ? json['items'] : json) as List<dynamic>;
    return list
        .map((e) => IngredientDto.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<IngredientDto> byId(String id) async {
    final json = await _api.get(ApiPaths.ingredient(id));
    return IngredientDto.fromJson(json as Map<String, dynamic>);
  }
}
