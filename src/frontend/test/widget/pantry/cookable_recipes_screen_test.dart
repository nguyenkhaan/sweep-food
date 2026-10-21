import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/core/widgets/loading_skeleton.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/screens/cookable_recipes_screen.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/presentation/controllers/suggestion_list_controller.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

void main() {
  testWidgets(
    'CookableRecipesScreen shows skeletons instead of hard-coded recipes',
    (tester) async {
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
          overrides: [
            cookableSuggestionProvider.overrideWith(
              (ref, query) => Completer<List<DishSuggestion>>().future,
            ),
          ],
          child: MaterialApp(
            locale: const Locale('vi'),
            supportedLocales: AppL10n.supportedLocales,
            localizationsDelegates: AppL10n.localizationsDelegates,
            theme: AppTheme.light,
            home: CookableRecipesScreen(selectedItems: selectedItems),
          ),
        ),
      );
      await tester.pump();

      expect(find.text('Công thức có thể nấu'), findsOneWidget);
      expect(
        find.byKey(const Key('cookable-recipes-skeleton')),
        findsOneWidget,
      );
      expect(find.byType(SkeletonBox), findsWidgets);
      expect(find.text('Trứng chiên hành lá'), findsNothing);
      expect(find.text('Đậu hũ sốt cà chua'), findsNothing);
    },
  );

  testWidgets(
    'CookableRecipesScreen also shows skeletons without selected items',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 2000));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            cookableSuggestionProvider.overrideWith(
              (ref, query) => Completer<List<DishSuggestion>>().future,
            ),
          ],
          child: MaterialApp(
            locale: const Locale('vi'),
            supportedLocales: AppL10n.supportedLocales,
            localizationsDelegates: AppL10n.localizationsDelegates,
            theme: AppTheme.light,
            home: const CookableRecipesScreen(selectedItems: []),
          ),
        ),
      );
      await tester.pump();

      expect(
        find.byKey(const Key('cookable-recipes-skeleton')),
        findsOneWidget,
      );
      expect(find.byType(SkeletonBox), findsWidgets);
    },
  );
}
