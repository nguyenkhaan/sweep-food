import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/cooking/presentation/widgets/post_cook_confirm_sheet.dart';
import 'package:sweepfood/features/dishes/presentation/screens/dish_detail_screen.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

class _FakePantryController extends PantryListController {
  @override
  Future<List<PantryItem>> build() async => [
        PantryItem(
          id: 'p1',
          name: 'Ức gà',
          category: 'Thịt',
          quantity: 300,
          unit: MeasurementUnit.gram,
          storageTier: StorageTier.fridge,
          addedAt: DateTime.now(),
          source: PantrySource.manual,
          status: PantryItemStatus.active,
        ),
        PantryItem(
          id: 'p2',
          name: 'Bơ',
          category: 'Trái cây',
          quantity: 2,
          unit: MeasurementUnit.fruit,
          storageTier: StorageTier.eatSoon,
          addedAt: DateTime.now(),
          source: PantrySource.manual,
          status: PantryItemStatus.active,
        ),
        PantryItem(
          id: 'p3',
          name: 'Xà lách',
          category: 'Rau',
          quantity: 200,
          unit: MeasurementUnit.gram,
          storageTier: StorageTier.fridge,
          addedAt: DateTime.now(),
          source: PantrySource.manual,
          status: PantryItemStatus.active,
        ),
        PantryItem(
          id: 'p4',
          name: 'Cà chua bi',
          category: 'Rau',
          quantity: 100,
          unit: MeasurementUnit.gram,
          storageTier: StorageTier.fridge,
          addedAt: DateTime.now(),
          source: PantrySource.manual,
          status: PantryItemStatus.active,
        ),
      ];
}

void main() {
  testWidgets('DishDetailScreen cook button opens PostCookConfirmSheet (AISC Section 6.3.5)', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1200, 2000));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          pantryListControllerProvider.overrideWith(() => _FakePantryController()),
        ],
        child: MaterialApp(
          locale: const Locale('vi'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
          theme: AppTheme.light,
          home: const DishDetailScreen(dishId: 'd1'),
        ),
      ),
    );
    // Wait for recipe to load
    for (var i = 0; i < 5; i++) {
      await tester.pump(const Duration(milliseconds: 300));
    }

    expect(find.text('Salad bơ ức gà'), findsWidgets);
    expect(find.text('Đã nấu món này'), findsOneWidget);

    // Tap "Đã nấu món này".
    await tester.tap(find.text('Đã nấu món này'));
    await tester.pump();
    for (var i = 0; i < 10; i++) {
      await tester.pump(const Duration(milliseconds: 300));
    }

    // Must show PostCookConfirmSheet
    expect(find.byType(PostCookConfirmSheet), findsOneWidget);
  });
}
