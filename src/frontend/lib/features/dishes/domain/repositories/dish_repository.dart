import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/dishes/domain/entities/dish.dart';

abstract interface class DishRepository {
  /// Full recipe for the detail screen (`GET /dishes/{id}`).
  Future<Result<Dish>> getById(String id);
}
