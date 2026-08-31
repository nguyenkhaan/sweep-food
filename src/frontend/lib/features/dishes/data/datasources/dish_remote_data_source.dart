import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/dishes/data/models/dish_dto.dart';

/// Talks to `/dishes/*`. Throws on failure — the repository catches and maps.
class DishRemoteDataSource {
  DishRemoteDataSource(this._api);

  final ApiClient _api;

  Future<DishDto> getById(String id) async {
    final json = await _api.get(ApiPaths.dish(id));
    return DishDto.fromJson(json as Map<String, dynamic>);
  }
}
