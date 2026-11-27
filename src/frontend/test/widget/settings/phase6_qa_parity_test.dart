import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/core/storage/prefs.dart';
import 'package:sweepfood/features/favorites/presentation/screens/favorites_screen.dart';
import 'package:sweepfood/features/notifications/presentation/screens/notification_center_screen.dart';
import 'package:sweepfood/features/settings/presentation/screens/settings_home_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

Future<Widget> _qaHarness(Widget child) async {
  SharedPreferences.setMockInitialValues({});
  final prefs = await SharedPreferences.getInstance();
  return ProviderScope(
    overrides: [sharedPreferencesProvider.overrideWithValue(prefs)],
    child: MaterialApp(
      locale: const Locale('vi'),
      supportedLocales: AppL10n.supportedLocales,
      localizationsDelegates: AppL10n.localizationsDelegates,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: ThemeMode.dark,
      builder: (context, inner) => MediaQuery(
        data: MediaQuery.of(context).copyWith(
          textScaler: const TextScaler.linear(1.5),
          disableAnimations: true,
        ),
        child: inner!,
      ),
      home: child,
    ),
  );
}

Future<void> _drainMockAsync(WidgetTester tester) async {
  for (var i = 0; i < 6; i++) {
    await tester.pump(const Duration(milliseconds: 250));
  }
}

void main() {
  testWidgets(
    'SettingsHomeScreen renders under dark mode, 375px, 1.5x text scale, and reduced motion',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 812));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(await _qaHarness(const SettingsHomeScreen()));
      await _drainMockAsync(tester);

      expect(find.text('Cá nhân'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'FavoritesScreen renders under dark mode, 375px, and reduced motion',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 812));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(await _qaHarness(const FavoritesScreen()));
      await _drainMockAsync(tester);

      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'NotificationCenterScreen renders under dark mode, 375px, and reduced motion',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 812));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        await _qaHarness(const NotificationCenterScreen()),
      );
      await _drainMockAsync(tester);

      expect(tester.takeException(), isNull);
    },
  );
}
