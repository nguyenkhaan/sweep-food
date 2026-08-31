import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
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

    return MaterialApp.router(
      title: AppConstants.appName,
      debugShowCheckedModeBanner: false,
      routerConfig: router,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: themeMode,
      // MVP ships Vietnamese only; `app_en.arb` is a skeleton for later. Strings
      // live in `lib/l10n/*.arb` — reach them via `context.l10n` / `AppL10n.of`.
      locale: const Locale('vi'),
      supportedLocales: AppL10n.supportedLocales,
      localizationsDelegates: AppL10n.localizationsDelegates,
    );
  }
}
