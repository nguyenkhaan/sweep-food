// test/helpers/pump_app.dart
// Widget-test harness: a MaterialApp wired with the app theme and the `vi`
// localizations (AppL10n), wrapped in a ProviderScope. Screens reach strings
// via `context.l10n`, so every widget test that renders one needs these
// delegates or `AppL10n.of(context)` throws.
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/misc.dart' show Override;
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

/// Wraps [home] in a localized [MaterialApp] + [ProviderScope].
Widget wrapApp(
  Widget home, {
  List<Override> overrides = const [],
  ThemeData? theme,
}) {
  return ProviderScope(
    overrides: overrides,
    child: MaterialApp(
      theme: theme ?? AppTheme.light,
      locale: const Locale('vi'),
      supportedLocales: AppL10n.supportedLocales,
      localizationsDelegates: AppL10n.localizationsDelegates,
      home: home,
    ),
  );
}
