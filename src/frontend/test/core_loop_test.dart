// Core loop (VM / `flutter test`): add ingredient -> suggest -> open dish ->
// cook -> pantry decremented. Mirrors integration_test/core_loop_test.dart, but
// runs headless so CI exercises it without a device.
//
// Driven at the provider layer with the real MockApiClient (assets/mock/*.json)
// — the same data path S-01 -> D-01 -> D-03 -> D-05 use. The Home waste count
// reads `pantrySummaryProvider`, invalidated by the cook.
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:sweepfood/features/cooking/presentation/controllers/cooking_controller.dart';
import 'package:sweepfood/features/dishes/presentation/controllers/dish_detail_controller.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:sweepfood/features/suggestions/presentation/controllers/suggestion_list_controller.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  double qty(List<PantryItem> items, String id) =>
      items.firstWhere((i) => i.id == id).quantity;

  test('add -> suggest -> open dish -> cook exact -> stock is deducted', () async {
    final container = ProviderContainer();
    addTearDown(container.dispose);

    // Stand in for the mounted Pantry/Home widgets that keep these alive.
    container.listen(pantryListControllerProvider, (prev, next) {});
    container.listen(pantrySummaryProvider, (prev, next) {});

    final before = await container.read(pantryListControllerProvider.future);
    expect(qty(before, 'b3'), 300); // Ức gà
    expect(qty(before, 'b2'), 500); // Cà chua bi

    final suggestions =
        await container.read(suggestionListControllerProvider.future);
    expect(suggestions.first.id, 'd1');
    expect(suggestions.first.score, 95);

    final dish = await container.read(dishByIdProvider('d1').future);
    expect(dish.name, 'Salad bơ ức gà');
    expect(dish.steps, isNotEmpty);

    final result = await container
        .read(cookingControllerProvider.notifier)
        .confirm(
          const CookConfirmation(
            dishId: 'd1',
            mode: CookMode.exact,
            servingsCooked: 2,
          ),
          dishName: dish.name,
        );

    expect(result.nearExpiryUsedCount, 3);
    expect(result.wasteAvoidedKg, closeTo(0.4, 0.001));

    final after = container.read(pantryListControllerProvider).requireValue;
    expect(qty(after, 'b3'), 100); // 300 -> 100
    expect(qty(after, 'b2'), 400); // 500 -> 400

    // Home reads the summary; the cook invalidated it, so a re-read refetches.
    // The dashboard aggregate has no backend ledger to derive a waste count
    // from (see PantryRepositoryImpl.summary) — the per-cook signal above
    // (nearExpiryUsedCount) is what actually reflects this cook.
    final summary = await container.read(pantrySummaryProvider.future);
    expect(summary.wasteReductionCount, 0);
  });
}
