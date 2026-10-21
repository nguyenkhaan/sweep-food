import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooking_preview.dart';
import 'package:sweepfood/features/cooking/presentation/widgets/post_cook_missing_sheet.dart';
import 'package:sweepfood/l10n/app_localizations.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

void main() {
  testWidgets(
    'PostCookMissingSheet renders missing ingredients and handles actions',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 2000));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      const missing = [
        MissingIngredientPreview(
          recipeIngredientId: 'ri1',
          ingredientName: 'Thịt bò nạc',
          missingQuantity: 150,
          unit: MeasurementUnit.gram,
        ),
        MissingIngredientPreview(
          recipeIngredientId: 'ri2',
          ingredientName: 'Hạt nêm',
          missingQuantity: 5,
          unit: MeasurementUnit.gram,
        ),
      ];

      var reducedServings = false;

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            locale: const Locale('vi'),
            supportedLocales: AppL10n.supportedLocales,
            localizationsDelegates: AppL10n.localizationsDelegates,
            theme: AppTheme.light,
            home: Scaffold(
              body: Builder(
                builder: (context) => ElevatedButton(
                  onPressed: () => PostCookMissingSheet.show(
                    context,
                    dishName: 'Bò xào bông thiên lý',
                    servings: 4,
                    missingIngredients: missing,
                    onReduceServings: () => reducedServings = true,
                  ),
                  child: const Text('Open Sheet'),
                ),
              ),
            ),
          ),
        ),
      );

      // Open sheet
      await tester.tap(find.text('Open Sheet'));
      await tester.pumpAndSettle();

      // Verify header and missing items
      expect(find.text('Chưa đủ nguyên liệu (4 phần)'), findsOneWidget);
      expect(find.text('Thịt bò nạc'), findsOneWidget);
      expect(find.text('Thiếu 150 g'), findsOneWidget);
      expect(find.text('Hạt nêm'), findsOneWidget);
      expect(find.text('Thiếu 5 g'), findsOneWidget);

      // Verify reduce servings button
      expect(find.text('Thử giảm khẩu phần (2 phần)'), findsOneWidget);
      await tester.tap(find.text('Thử giảm khẩu phần (2 phần)'));
      await tester.pumpAndSettle();

      expect(reducedServings, isTrue);
    },
  );
}
