import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/screens/cookable_recipes_screen.dart';
import 'package:sweepfood/features/shopping_list/presentation/controllers/shopping_list_controller.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

void main() {
  testWidgets('CookableRecipesScreen shows matched recipes and missing ingredients', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1200, 2000));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    final selectedItems = [
      PantryItem(
        id: 'p1',
        name: 'Trứng gà',
        quantity: 4,
        unit: MeasurementUnit.piece,
        category: 'Trứng',
        storageTier: StorageTier.fridge,
        addedAt: DateTime.now(),
        source: PantrySource.manual,
        status: PantryItemStatus.active,
        expiryDate: DateTime.now().add(const Duration(days: 10)),
      ),
      PantryItem(
        id: 'p2',
        name: 'Cà chua bi',
        quantity: 3,
        unit: MeasurementUnit.piece,
        category: 'Rau củ',
        storageTier: StorageTier.fridge,
        addedAt: DateTime.now(),
        source: PantrySource.manual,
        status: PantryItemStatus.active,
        expiryDate: DateTime.now().add(const Duration(days: 5)),
      ),
    ];

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          locale: const Locale('vi'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
          theme: AppTheme.light,
          home: CookableRecipesScreen(selectedItems: selectedItems),
        ),
      ),
    );
    // Pre-warm ShoppingListController
    final element = tester.element(find.byType(CookableRecipesScreen));
    final container = ProviderScope.containerOf(element);
    container.read(shoppingListControllerProvider);

    for (var i = 0; i < 5; i++) {
      await tester.pump(const Duration(milliseconds: 300));
    }

    // Verify title and selected chips
    expect(find.text('Công thức có thể nấu'), findsOneWidget);
    expect(find.text('Trứng gà'), findsOneWidget);
    expect(find.text('Cà chua bi'), findsOneWidget);

    // Verify recipes found
    expect(find.text('Trứng chiên hành lá'), findsOneWidget);
    expect(find.text('Đậu hũ sốt cà chua'), findsOneWidget);

    // Verify missing ingredients section: name and displayQty are in separate Text widgets
    expect(find.text('Hành lá'), findsWidgets);
    expect(find.text('20g'), findsWidgets);

    // Verify bottom action bar
    expect(find.text('Thêm tất cả nguyên liệu thiếu vào giỏ mua'), findsOneWidget);

    // Tap Thêm tất cả nguyên liệu thiếu vào giỏ mua
    await tester.tap(find.text('Thêm tất cả nguyên liệu thiếu vào giỏ mua'));
    for (var i = 0; i < 15; i++) {
      await tester.pump(const Duration(milliseconds: 300));
    }

    expect(find.textContaining('Đã thêm'), findsOneWidget);
  });

  testWidgets('CookableRecipesScreen shows empty state when no items selected', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1200, 2000));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          locale: const Locale('vi'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
          theme: AppTheme.light,
          home: const CookableRecipesScreen(selectedItems: []),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Chưa có công thức phù hợp'), findsOneWidget);
    expect(
      find.text('Hãy chọn thêm nguyên liệu trong kho để tìm công thức nấu ăn.'),
      findsOneWidget,
    );
  });
}
