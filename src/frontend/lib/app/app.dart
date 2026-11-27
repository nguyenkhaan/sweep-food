import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/locale_controller.dart';
import 'package:sweepfood/app/router/app_router.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/app/theme/theme_mode_controller.dart';
import 'package:sweepfood/core/config/app_constants.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

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
      themeAnimationStyle: MediaQuery.disableAnimationsOf(context)
          ? AnimationStyle.noAnimation
          : null,
      builder: (context, child) {
        final theme = Theme.of(context);
        final isDark = theme.brightness == Brightness.dark;
        final overlayStyle = SystemUiOverlayStyle(
          statusBarColor: Colors.transparent,
          statusBarIconBrightness: isDark ? Brightness.light : Brightness.dark,
          statusBarBrightness: isDark ? Brightness.dark : Brightness.light,
          systemNavigationBarColor: theme.colorScheme.surfaceContainerLowest,
          systemNavigationBarDividerColor: Colors.transparent,
          systemNavigationBarIconBrightness: isDark
              ? Brightness.light
              : Brightness.dark,
        );
        return AnnotatedRegion<SystemUiOverlayStyle>(
          value: overlayStyle,
          child: child ?? const SizedBox.shrink(),
        );
      },
      // Strings live in `lib/l10n/*.arb` (reach them via `context.l10n`).
      // Defaults to `vi`; English is opt-in via Cài đặt → Tùy chọn → Ngôn ngữ.
      // Some data-layer strings still fall back to `vi` — see M6.1 in the plan.
      locale: locale,
      supportedLocales: AppL10n.supportedLocales,
      localizationsDelegates: AppL10n.localizationsDelegates,
    );
  }
}
