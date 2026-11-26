// Widget tests for S-01 suggestions list, fit_reasons on cards & S-02 sheet,
// medical disclaimer, and filtered-empty state.
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:sweepfood/features/suggestions/data/datasources/suggestion_remote_data_source.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/presentation/controllers/suggestion_list_controller.dart';
import 'package:sweepfood/features/suggestions/presentation/screens/suggestion_list_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/storage_tier.dart';

class _EmptySuggestionListController extends SuggestionListController {
  @override
  Future<List<DishSuggestion>> build() async => const [];
}

class _ActivePantryListController extends PantryListController {
  @override
  Future<List<PantryItem>> build() async => [
    PantryItem(
      id: 'p-1',
      name: 'Thịt bò',
      category: 'Thịt',
      quantity: 300,
      unit: MeasurementUnit.gram,
      storageTier: StorageTier.fridge,
      addedAt: DateTime(2026, 11, 20),
      source: PantrySource.manual,
      status: PantryItemStatus.active,
    ),
  ];
}

void main() {
  testWidgets(
    'renders ranked cards with fit_reasons, disclaimer, and opens score-breakdown sheet',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(430, 1200));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            locale: const Locale('vi'),
            supportedLocales: AppL10n.supportedLocales,
            localizationsDelegates: AppL10n.localizationsDelegates,
            theme: AppTheme.light,
            home: const SuggestionListScreen(),
          ),
        ),
      );
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 1000));

      expect(find.text('Salad bơ ức gà'), findsOneWidget);
      expect(find.text('Canh chua cá lóc'), findsOneWidget);
      expect(find.textContaining('món hợp nhất'), findsOneWidget);
      expect(
        find.text('Gợi ý tham khảo, không thay lời khuyên của bác sĩ'),
        findsOneWidget,
      );
      expect(find.text('Ít muối, hợp người cao huyết áp'), findsOneWidget);

      await tester.tap(find.byIcon(Icons.help_outline_rounded).first);
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 300));

      expect(find.text('Vì sao hợp với hồ sơ của bạn'), findsOneWidget);
      expect(find.textContaining('Điểm = 0.4·E'), findsOneWidget);
      expect(find.textContaining('Dùng đồ cận hạn'), findsOneWidget);
    },
  );

  testWidgets(
    'shows filtered empty state with nutrition profile CTA when pantry has items',
    (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            aiServiceHealthProvider.overrideWith(
              (_) async => AiServiceHealthDto.fromJson({'status': 'ready'}),
            ),
            suggestionListControllerProvider.overrideWith(
              _EmptySuggestionListController.new,
            ),
            pantryListControllerProvider.overrideWith(
              _ActivePantryListController.new,
            ),
          ],
          child: MaterialApp(
            locale: const Locale('vi'),
            supportedLocales: AppL10n.supportedLocales,
            localizationsDelegates: AppL10n.localizationsDelegates,
            theme: AppTheme.light,
            darkTheme: AppTheme.dark,
            themeMode: ThemeMode.dark,
            home: const SuggestionListScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Chưa có món hợp với hồ sơ hiện tại'), findsOneWidget);
      expect(find.text('Xem hồ sơ ăn uống'), findsOneWidget);
      expect(
        find.text('Gợi ý tham khảo, không thay lời khuyên của bác sĩ'),
        findsOneWidget,
      );
    },
  );
}
