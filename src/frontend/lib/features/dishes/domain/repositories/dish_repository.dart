import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish.dart';

abstract interface class DishRepository {
  /// Full recipe for the detail screen (`GET /dishes/{id}`).
  Future<Result<Dish>> getById(String id);
}
