import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/dishes/data/repositories/dish_repository_impl.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish.dart';

part 'dish_detail_controller.g.dart';

/// Loads the full recipe once (`GET /dishes/{id}`). Kept at the base serving
/// count — [scaledDish] applies the user's choice from [DishServings].
@riverpod
Future<Dish> dishById(Ref ref, String dishId) async {
  final res = await ref.watch(dishRepositoryProvider).getById(dishId);
  return res.fold((f) => throw f, (d) => d);
}

/// The serving count chosen on the D-01 stepper. `null` = "use the recipe's own".
@riverpod
class DishServings extends _$DishServings {
  @override
  int? build(String dishId) => null;

  void set(int servings) => state = servings < 1 ? 1 : servings;
}

/// The recipe re-scaled to the chosen servings (quantities + nutrition).
/// Always derived from the base dish, so repeated changes don't drift.
@riverpod
Dish? scaledDish(Ref ref, String dishId) {
  final dish = ref.watch(dishByIdProvider(dishId)).asData?.value;
  if (dish == null) return null;
  final chosen = ref.watch(dishServingsProvider(dishId)) ?? dish.servings;
  return dish.scaledTo(chosen);
}
