import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/core/widgets/empty_state.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:sweepfood/features/shopping_list/presentation/controllers/shopping_list_controller.dart';
import 'package:sweepfood/features/shopping_list/presentation/screens/shopping_list_screen.dart';
import 'package:sweepfood/features/shopping_list/presentation/widgets/shopping_item_row.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

class _FakeShoppingListController extends ShoppingListController {
  _FakeShoppingListController(this._initialList);

  final ShoppingList? _initialList;

  @override
  Future<ShoppingList?> build() async => _initialList;
}

void main() {
  testWidgets('does not render checked items on screen', (tester) async {
    const listWithBought = ShoppingList(
      id: 'sl1',
      items: [
        ShoppingListItem(
          id: 'item-1',
          name: 'Thịt bò',
          quantity: 500,
          unit: MeasurementUnit.gram,
          category: 'Từ công thức',
          checked: false,
          alreadyInPantry: false,
        ),
        ShoppingListItem(
          id: 'item-2',
          name: 'Cà rốt',
          quantity: 2,
          unit: MeasurementUnit.piece,
          category: 'Từ công thức',
          checked: true,
          alreadyInPantry: false,
        ),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          shoppingListControllerProvider.overrideWith(
            () => _FakeShoppingListController(listWithBought),
          ),
        ],
        child: MaterialApp(
          locale: const Locale('vi'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
          theme: AppTheme.light,
          home: const ShoppingListScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Thịt bò (unchecked) is rendered
    expect(find.text('Thịt bò'), findsOneWidget);
    // Cà rốt (checked / bought) is NOT rendered
    expect(find.text('Cà rốt'), findsNothing);
    expect(find.byType(ShoppingItemRow), findsOneWidget);
  });

  testWidgets('renders all bought empty state when all items are checked', (tester) async {
    const listAllBought = ShoppingList(
      id: 'sl1',
      items: [
        ShoppingListItem(
          id: 'item-1',
          name: 'Cà chua',
          quantity: 3,
          unit: MeasurementUnit.piece,
          category: 'Từ công thức',
          checked: true,
          alreadyInPantry: false,
        ),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          shoppingListControllerProvider.overrideWith(
            () => _FakeShoppingListController(listAllBought),
          ),
        ],
        child: MaterialApp(
          locale: const Locale('vi'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
          theme: AppTheme.light,
          home: const ShoppingListScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Cà chua'), findsNothing);
    expect(find.byType(EmptyState), findsOneWidget);
    expect(find.text('Đã mua hết nguyên liệu'), findsOneWidget);
  });
}
