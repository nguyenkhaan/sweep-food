import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/home/presentation/screens/home_screen.dart';
import 'package:sweepfood/features/pantry/presentation/screens/pantry_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

void main() {
  testWidgets(
    'HomeScreen renders in dark mode at 375px width and 1.5x text scale without overflow',
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
            builder: (context, child) => MediaQuery(
              data: MediaQuery.of(
                context,
              ).copyWith(textScaler: const TextScaler.linear(1.5)),
              child: child!,
            ),
            home: const HomeScreen(),
          ),
        ),
      );

      for (var i = 0; i < 8; i++) {
        await tester.pump(const Duration(milliseconds: 300));
      }

      expect(tester.takeException(), isNull);
      expect(find.text('Hôm nay ăn gì?'), findsOneWidget);
    },
  );

  testWidgets(
    'PantryScreen renders in dark mode at 375px width and 1.5x text scale without overflow',
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
            builder: (context, child) => MediaQuery(
              data: MediaQuery.of(
                context,
              ).copyWith(textScaler: const TextScaler.linear(1.5)),
              child: child!,
            ),
            home: const PantryScreen(),
          ),
        ),
      );

      for (var i = 0; i < 8; i++) {
        await tester.pump(const Duration(milliseconds: 300));
      }

      expect(tester.takeException(), isNull);
      expect(find.text('Kho thực phẩm'), findsOneWidget);
    },
  );
}
