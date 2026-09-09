import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/core/storage/prefs.dart';
import 'package:sweepfood/features/settings/presentation/screens/settings_home_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

void main() {
  testWidgets('SettingsHomeScreen displays "Lịch sử nấu ăn" in Vietnamese', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();

    await tester.binding.setSurfaceSize(const Size(1000, 2000));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          sharedPreferencesProvider.overrideWithValue(prefs),
        ],
        child: MaterialApp(
          locale: const Locale('vi'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
          theme: AppTheme.light,
          home: const SettingsHomeScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Lịch sử nấu ăn'), findsOneWidget);
    expect(find.text('Thực đơn tuần'), findsOneWidget);
  });

  testWidgets('SettingsHomeScreen displays "Cooking history" in English', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({'pref.locale': 'en'});
    final prefs = await SharedPreferences.getInstance();

    await tester.binding.setSurfaceSize(const Size(1000, 2000));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          sharedPreferencesProvider.overrideWithValue(prefs),
        ],
        child: MaterialApp(
          locale: const Locale('en'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
          theme: AppTheme.light,
          home: const SettingsHomeScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Cooking history'), findsOneWidget);
    expect(find.text('Weekly plan'), findsOneWidget);
    expect(find.text('Lịch sử nấu ăn'), findsNothing);
  });
}
