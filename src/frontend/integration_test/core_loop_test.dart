// Core loop: add ingredient -> suggest -> open dish -> cook -> pantry decremented.
//
// Driven at the provider layer with the real MockApiClient (assets/mock/*.json),
// which is exactly the data path the S-01 -> D-01 -> D-03 -> D-05 screens use.
// The Home waste count reads `pantrySummaryProvider`, invalidated by the cook.
//
// Run: flutter test integration_test/core_loop_test.dart -d <device>
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:sweepfood/features/cooking/presentation/controllers/cooking_controller.dart';
import 'package:sweepfood/features/dishes/presentation/controllers/dish_detail_controller.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:sweepfood/features/suggestions/presentation/controllers/suggestion_list_controller.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  double qty(List<PantryItem> items, String id) =>
      items.firstWhere((i) => i.id == id).quantity;

  testWidgets('add -> suggest -> open dish -> cook exact -> stock deducted', (
    tester,
  ) async {
    final container = ProviderContainer();
    addTearDown(container.dispose);

    // Stand in for the mounted Pantry/Home widgets that keep these alive.
    container.listen(pantryListControllerProvider, (prev, next) {});
    container.listen(pantrySummaryProvider, (prev, next) {});

    // Pantry starts from the fixture.
    final before = await container.read(pantryListControllerProvider.future);
    expect(qty(before, 'b3'), 300); // Ức gà
    expect(qty(before, 'b2'), 500); // Cà chua bi

    // Suggestions come back ranked; the top pick is "Salad bơ ức gà" (d1).
    final suggestions =
        await container.read(suggestionListControllerProvider.future);
    expect(suggestions, isNotEmpty);
    expect(suggestions.first.id, 'd1');
    expect(suggestions.first.score, 95);

    // Open the dish detail (loads the full recipe + steps).
    final dish = await container.read(dishByIdProvider('d1').future);
    expect(dish.name, 'Salad bơ ức gà');
    expect(dish.steps, isNotEmpty);

    // "Đã nấu" with exact amounts.
    final cooking = container.read(cookingControllerProvider.notifier);
    final preview = await cooking.previewForDish(dishId: 'd1', servings: 2);
    final result = await cooking.confirm(
      preview: preview,
      mode: CookMode.exact,
      dishName: dish.name,
    );

    // Matched against inventory_batches.json by name: Ức gà (b3) and Cà chua
    // bi (b2) — both near-expiry. "Bơ"/"Xà lách" have no matching batch, so
    // they land in missing_ingredients instead of contributing here.
    expect(result.nearExpiryUsedCount, 2);
    expect(result.wasteAvoidedKg, closeTo(0.3, 0.001));

    // The loaded pantry list now reflects the deduction.
    final after = container.read(pantryListControllerProvider).requireValue;
    expect(qty(after, 'b3'), 100); // 300 -> 100
    expect(qty(after, 'b2'), 400); // 500 -> 400
  });
}
