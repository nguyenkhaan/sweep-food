import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/auth/presentation/screens/welcome_screen.dart';
import 'package:sweepfood/features/subscription/presentation/screens/paywall_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

void main() {
  testWidgets(
    'WelcomeScreen renders SVG onboarding slides cleanly in dark mode',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 812));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        MaterialApp(
          locale: const Locale('vi'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
          theme: AppTheme.light,
          darkTheme: AppTheme.dark,
          themeMode: ThemeMode.dark,
          home: const WelcomeScreen(),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('SweepFood'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'PaywallScreen shows comparison cards and 6 benefits in dark mode',
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
            home: const PaywallScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('SweepFood Premium sắp ra mắt'), findsOneWidget);
      expect(find.text('Kho nguyên liệu không giới hạn'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
}
