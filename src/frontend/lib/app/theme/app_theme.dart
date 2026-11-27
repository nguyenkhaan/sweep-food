import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_colors.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';

/// Builds the hand-authored light + dark [ThemeData] from Design System 2.0 tokens.
abstract final class AppTheme {
  static ThemeData get light => _build(
    brightness: Brightness.light,
    scheme: const ColorScheme.light(
      primary: BrandPalette.green700,
      onPrimary: Colors.white,
      primaryContainer: BrandPalette.green100,
      onPrimaryContainer: BrandPalette.green800,
      secondary: BrandPalette.green600,
      onSecondary: Colors.white,
      secondaryContainer: BrandPalette.green100,
      onSecondaryContainer: BrandPalette.green800,
      tertiary: BrandPalette.brick500,
      onTertiary: Colors.white,
      tertiaryContainer: BrandPalette.brick100,
      onTertiaryContainer: BrandPalette.brick700,
      error: BrandPalette.brick500,
      onError: Colors.white,
      errorContainer: BrandPalette.brick100,
      onErrorContainer: BrandPalette.brick700,
      surface: Color(0xFFF6F7F6),
      onSurface: Color(0xFF111815),
      onSurfaceVariant: Color(0xFF525D57),
      surfaceContainerLowest: Colors.white,
      surfaceContainerLow: Color(0xFFFAFBF9),
      surfaceContainer: Color(0xFFF0F2F0),
      surfaceContainerHigh: Color(0xFFE7EAE8),
      surfaceContainerHighest: Color(0xFFDFE3E0),
      outline: Color(0xFF7B8178),
      outlineVariant: Color(0xFFEFECE3),
    ),
    sweep: SweepColors.light,
    motion: AppMotion.standard,
  );

  static ThemeData get dark => _build(
    brightness: Brightness.dark,
    scheme: const ColorScheme.dark(
      primary: BrandPalette.green400,
      onPrimary: Color(0xFF0A2418),
      primaryContainer: Color(0xFF183324),
      onPrimaryContainer: BrandPalette.green200,
      secondary: BrandPalette.green300,
      onSecondary: Color(0xFF0A2418),
      secondaryContainer: Color(0xFF183324),
      onSecondaryContainer: BrandPalette.green200,
      tertiary: BrandPalette.brick300,
      onTertiary: Color(0xFF2B1415),
      tertiaryContainer: Color(0xFF332020),
      onTertiaryContainer: BrandPalette.brick200,
      error: BrandPalette.brick300,
      onError: Color(0xFF2B1415),
      errorContainer: Color(0xFF332020),
      onErrorContainer: BrandPalette.brick200,
      surface: Color(0xFF0E1411),
      onSurface: Color(0xFFEFF2EC),
      onSurfaceVariant: Color(0xFFB2BAB1),
      surfaceContainerLowest: Color(0xFF151D18),
      surfaceContainerLow: Color(0xFF1B251F),
      surfaceContainer: Color(0xFF202B24),
      surfaceContainerHigh: Color(0xFF27342C),
      surfaceContainerHighest: Color(0xFF2D3931),
      outline: Color(0xFF7C8A80),
      outlineVariant: Color(0xFF202A24),
    ),
    sweep: SweepColors.dark,
    motion: AppMotion.standard,
  );

  static ThemeData _build({
    required Brightness brightness,
    required ColorScheme scheme,
    required SweepColors sweep,
    required AppMotion motion,
  }) {
    final textTheme = AppTypography.textTheme(
      scheme.onSurface,
      sweep.textSecondary,
    );

    return ThemeData(
      useMaterial3: true,
      brightness: brightness,
      colorScheme: scheme,
      scaffoldBackgroundColor: scheme.surface,
      canvasColor: scheme.surface,
      fontFamily: AppTypography.fontFamily,
      textTheme: textTheme,
      extensions: [sweep, motion],
      splashFactory: InkSparkle.splashFactory,
      dividerTheme: DividerThemeData(
        color: sweep.hairline,
        thickness: 1,
        space: 1,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: scheme.surface,
        foregroundColor: scheme.onSurface,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        titleTextStyle: textTheme.titleLarge,
      ),
      cardTheme: CardThemeData(
        color: scheme.surfaceContainerLowest,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: Radii.brLg,
          side: BorderSide(color: sweep.hairline),
        ),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: scheme.surfaceContainerLowest,
        surfaceTintColor: Colors.transparent,
        shape: const RoundedRectangleBorder(borderRadius: Radii.brXl),
        titleTextStyle: textTheme.titleLarge,
        contentTextStyle: textTheme.bodyMedium,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size(88, 48),
          padding: const EdgeInsets.symmetric(
            horizontal: Gap.lg,
            vertical: Gap.sm + 2,
          ),
          textStyle: textTheme.labelLarge,
          shape: const RoundedRectangleBorder(borderRadius: Radii.brMd),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: const Size(88, 48),
          padding: const EdgeInsets.symmetric(
            horizontal: Gap.lg,
            vertical: Gap.sm + 2,
          ),
          textStyle: textTheme.labelLarge,
          side: BorderSide(color: scheme.primary),
          shape: const RoundedRectangleBorder(borderRadius: Radii.brMd),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(textStyle: textTheme.labelLarge),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: scheme.surfaceContainerLowest,
        hintStyle: textTheme.bodyLarge?.copyWith(color: sweep.textTertiary),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: Gap.md,
          vertical: Gap.sm + 2,
        ),
        border: OutlineInputBorder(
          borderRadius: Radii.brMd,
          borderSide: BorderSide(color: sweep.hairline),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: Radii.brMd,
          borderSide: BorderSide(color: sweep.hairline),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: Radii.brMd,
          borderSide: BorderSide(color: scheme.primary, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: Radii.brMd,
          borderSide: BorderSide(color: scheme.error),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: Radii.brMd,
          borderSide: BorderSide(color: scheme.error, width: 1.5),
        ),
      ),
      chipTheme: ChipThemeData(
        shape: const StadiumBorder(),
        side: BorderSide(color: sweep.hairline),
        backgroundColor: scheme.surfaceContainerLowest,
        selectedColor: scheme.primary,
        checkmarkColor: scheme.onPrimary,
        labelStyle: textTheme.labelMedium?.copyWith(
          color: scheme.onSurface,
          fontWeight: FontWeight.w500,
        ),
        secondaryLabelStyle: textTheme.labelMedium?.copyWith(
          color: scheme.onPrimary,
          fontWeight: FontWeight.w600,
        ),
        padding: const EdgeInsets.symmetric(horizontal: Gap.sm, vertical: 6),
      ),
      switchTheme: SwitchThemeData(
        thumbColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) return scheme.onPrimary;
          return scheme.outline;
        }),
        trackColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) return scheme.primary;
          return scheme.surfaceContainerHighest;
        }),
        trackOutlineColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) return Colors.transparent;
          return scheme.outline;
        }),
      ),
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: scheme.surfaceContainerLowest,
        surfaceTintColor: Colors.transparent,
        showDragHandle: true,
        dragHandleColor: sweep.hairline,
        dragHandleSize: const Size(40, 4),
        shape: const RoundedRectangleBorder(borderRadius: Radii.brSheet),
      ),
      tabBarTheme: TabBarThemeData(
        labelColor: scheme.primary,
        unselectedLabelColor: sweep.textTertiary,
        indicatorColor: scheme.primary,
        dividerColor: sweep.hairline,
        labelStyle: textTheme.labelLarge,
        unselectedLabelStyle: textTheme.labelMedium,
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: scheme.surfaceContainerLowest,
        surfaceTintColor: Colors.transparent,
        indicatorColor: scheme.primaryContainer,
        height: 68,
        labelTextStyle: WidgetStateProperty.resolveWith(
          (states) => textTheme.labelSmall?.copyWith(
            letterSpacing: 0,
            fontWeight: states.contains(WidgetState.selected)
                ? FontWeight.w700
                : FontWeight.w500,
            color: states.contains(WidgetState.selected)
                ? scheme.primary
                : sweep.textTertiary,
          ),
        ),
        iconTheme: WidgetStateProperty.resolveWith(
          (states) => IconThemeData(
            size: 22,
            color: states.contains(WidgetState.selected)
                ? scheme.primary
                : sweep.textTertiary,
          ),
        ),
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: brightness == Brightness.light
            ? const Color(0xFF181C18)
            : const Color(0xFF233028),
        contentTextStyle: textTheme.bodyMedium?.copyWith(color: Colors.white),
        actionTextColor: BrandPalette.green300,
        shape: const RoundedRectangleBorder(borderRadius: Radii.brMd),
      ),
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: scheme.primary,
        foregroundColor: scheme.onPrimary,
        elevation: 3,
        shape: const StadiumBorder(),
      ),
    );
  }
}
