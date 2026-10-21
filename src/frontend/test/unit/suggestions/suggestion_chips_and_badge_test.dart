import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/core/widgets/suggestion_card.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/domain/entities/score_breakdown.dart';
import 'package:sweepfood/features/suggestions/presentation/widgets/suggestion_card_chips.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/nutrition_info.dart';

void main() {
  group('SuggestionCardChips', () {
    test('does not include "Có sẵn x%" chip', () async {
      final l10n = await AppL10n.delegate.load(const Locale('vi'));

      const suggestion = DishSuggestion(
        dish: Dish(
          id: 'd1',
          name: 'Phở bò',
          cookTimeMin: 30,
          prepTimeMin: 10,
          servings: 2,
          nutritionPerServing: NutritionInfo.zero(),
        ),
        breakdown: ScoreBreakdown(e: 10, a: 20, p: 30, u: 40),
        availabilityRatio: 0.8,
        toBuyCount: 1,
      );

      final chips = suggestion.cardChips(l10n);
      final labels = chips.map((c) => c.label).toList();

      for (final label in labels) {
        expect(label.contains('Có sẵn'), isFalse,
            reason: 'Found unexpected "Có sẵn" in chip label: $label');
      }
    });
  });

  group('SuggestionCard rank badge', () {
    testWidgets('shows #1 and does not display AI text on rank badge', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          locale: const Locale('vi'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
          theme: AppTheme.light,
          home: const Scaffold(
            body: SuggestionCard(
              title: 'Phở bò',
              score: 95,
              rank: 1,
              meta: '30 phút · Dễ',
              chips: [],
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('#1'), findsOneWidget);
      expect(find.text('AI'), findsNothing);
    });
  });
}
