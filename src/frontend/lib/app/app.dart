import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/app_router.dart';
import 'package:frontend/app/theme/app_theme.dart';
import 'package:frontend/app/theme/theme_mode_controller.dart';
import 'package:frontend/core/config/app_constants.dart';

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
      // MVP is Vietnamese-only; strings are hardcoded until the M6 l10n pass.
      locale: const Locale('vi'),
      supportedLocales: const [Locale('vi'), Locale('en')],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
    );
  }
}
