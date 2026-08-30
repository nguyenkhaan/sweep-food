import 'package:frontend/features/dishes/presentation/controllers/dish_detail_controller.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'custom_usage_controller.g.dart';

/// D-04 — per-ingredient "how much did you actually use" sliders, keyed by dish.
/// Seeded from the scaled recipe amounts; the sheet edits each entry.
@riverpod
class CustomUsageController extends _$CustomUsageController {
  @override
  Map<String, double> build(String dishId) {
    final dish = ref.watch(scaledDishProvider(dishId));
    if (dish == null) return {};
    return {for (final i in dish.mainIngredients) i.name: i.quantity};
  }

  void setUsage(String name, double quantity) =>
      state = {...state, name: quantity < 0 ? 0 : quantity};
}
