import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish.dart';

abstract interface class DishRepository {
  /// Full recipe for the detail screen (`GET /dishes/{id}`).
  Future<Result<Dish>> getById(String id);

  /// Search recipes from catalog (`GET /recipes`).
  Future<Result<List<Dish>>> searchRecipes({
    String? query,
    String? tag,
    int? maxCookingMinutes,
    int page = 1,
    int perPage = 20,
  });
}
