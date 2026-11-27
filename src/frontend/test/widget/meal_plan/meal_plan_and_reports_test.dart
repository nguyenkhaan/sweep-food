import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/meal_plan/presentation/screens/meal_plan_screen.dart';
import 'package:sweepfood/features/reports/presentation/screens/reports_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

void main() {
  testWidgets(
    'MealPlanScreen day-strip switches days in dark mode without overflow',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 812));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            locale: const Locale('vi'),
            supportedLocales: AppL10n.supportedLocales,
            localizationsDelegates: AppL10n.localizationsDelegates,
            theme: AppTheme.light,
            darkTheme: AppTheme.dark,
            themeMode: ThemeMode.dark,
            home: const MealPlanScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Thực đơn tuần'), findsOneWidget);
      expect(find.text('Tạo danh sách mua sắm'), findsOneWidget);

      await tester.tap(find.text('T5'));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'ReportsScreen renders hero counter and bar chart cleanly in dark mode',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 812));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            locale: const Locale('vi'),
            supportedLocales: AppL10n.supportedLocales,
            localizationsDelegates: AppL10n.localizationsDelegates,
            theme: AppTheme.light,
            darkTheme: AppTheme.dark,
            themeMode: ThemeMode.dark,
            home: const ReportsScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Chống lãng phí'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
}
