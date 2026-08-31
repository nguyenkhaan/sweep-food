import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/locale_controller.dart';
import 'package:frontend/app/router/app_router.dart';
import 'package:frontend/app/theme/app_theme.dart';
import 'package:frontend/app/theme/theme_mode_controller.dart';
import 'package:frontend/core/config/app_constants.dart';
import 'package:frontend/l10n/app_localizations.dart';

/// Root widget. Owns the [MaterialApp.router], theme + theme-mode, and locale.
class SweepFoodApp extends ConsumerWidget {
  const SweepFoodApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);
    final themeMode = ref.watch(themeModeControllerProvider);
    final locale = ref.watch(localeControllerProvider);

    return MaterialApp.router(
      title: AppConstants.appName,
      debugShowCheckedModeBanner: false,
      routerConfig: router,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: themeMode,
      // Strings live in `lib/l10n/*.arb` (reach them via `context.l10n`).
      // Defaults to `vi`; English is opt-in via Cài đặt → Tùy chọn → Ngôn ngữ.
      // Some data-layer strings still fall back to `vi` — see M6.1 in the plan.
      locale: locale,
      supportedLocales: AppL10n.supportedLocales,
      localizationsDelegates: AppL10n.localizationsDelegates,
    );
  }
}
