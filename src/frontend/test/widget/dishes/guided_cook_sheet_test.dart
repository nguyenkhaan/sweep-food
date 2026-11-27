import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/dishes/domain/entities/cooking_step.dart';
import 'package:sweepfood/features/dishes/presentation/widgets/guided_cook_sheet.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

void main() {
  testWidgets(
    'GuidedCookSheet steps through recipe instructions and runs step timer',
    (tester) async {
      var finished = false;
      const steps = [
        CookingStep(order: 1, text: 'Ướp thịt với tỏi băm.', durationMin: 1),
        CookingStep(order: 2, text: 'Áp chảo lửa lớn đến khi chín vàng.'),
      ];

      await tester.pumpWidget(
        MaterialApp(
          locale: const Locale('vi'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
          theme: AppTheme.light,
          darkTheme: AppTheme.dark,
          themeMode: ThemeMode.dark,
          home: Scaffold(
            body: Builder(
              builder: (context) => FilledButton(
                onPressed: () => GuidedCookSheet.show(
                  context,
                  dishName: 'Ức gà áp chảo',
                  steps: steps,
                  onFinishCooking: () => finished = true,
                ),
                child: const Text('Start'),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Start'));
      await tester.pumpAndSettle();

      expect(find.text('Bước 1/2'), findsNWidgets(2));
      expect(find.text('01:00'), findsOneWidget);
      expect(find.text('Hẹn giờ 1 phút'), findsOneWidget);

      await tester.tap(find.text('Hẹn giờ 1 phút'));
      await tester.pump(const Duration(seconds: 2));
      expect(find.text('00:58'), findsOneWidget);

      await tester.tap(find.text('Bước tiếp'));
      await tester.pumpAndSettle();

      expect(find.text('Bước 2/2'), findsNWidgets(2));
      await tester.tap(find.text('Hoàn tất và Trừ kho'));
      await tester.pumpAndSettle();

      expect(finished, isTrue);
    },
  );
}
