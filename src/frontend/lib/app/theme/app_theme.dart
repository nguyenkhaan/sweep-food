import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_colors.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/app/theme/app_typography.dart';

/// Builds the light + dark [ThemeData] from the design tokens.
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
          surface: Color(0xFFF8F9FA),
          onSurface: Color(0xFF1A1C19),
          surfaceContainerLowest: Colors.white,
          surfaceContainerLow: Colors.white,
          surfaceContainer: Color(0xFFF2F4F0),
          surfaceContainerHigh: Color(0xFFEDEFEA),
          outline: Color(0xFFE1E3DE),
          outlineVariant: Color(0xFFEFF1EC),
        ),
        sweep: SweepColors.light,
      );

  static ThemeData get dark => _build(
        brightness: Brightness.dark,
        scheme: const ColorScheme.dark(
          primary: BrandPalette.green600,
          onPrimary: Colors.white,
          primaryContainer: Color(0xFF17301F),
          onPrimaryContainer: BrandPalette.green200,
          secondary: BrandPalette.green400,
          onSecondary: Color(0xFF0F1F17),
          secondaryContainer: Color(0xFF17301F),
          onSecondaryContainer: BrandPalette.green200,
          tertiary: BrandPalette.brick300,
          onTertiary: Color(0xFF2A1516),
          tertiaryContainer: Color(0xFF33211F),
          onTertiaryContainer: BrandPalette.brick200,
          error: BrandPalette.brick300,
          onError: Color(0xFF2A1516),
          surface: Color(0xFF101511),
          onSurface: Color(0xFFECEFEA),
          surfaceContainerLowest: Color(0xFF141A15),
          surfaceContainerLow: Color(0xFF1A211C),
          surfaceContainer: Color(0xFF1A211C),
          surfaceContainerHigh: Color(0xFF222A24),
          outline: Color(0xFF2E362F),
          outlineVariant: Color(0xFF242B25),
        ),
        sweep: SweepColors.dark,
      );

  static ThemeData _build({
    required Brightness brightness,
    required ColorScheme scheme,
    required SweepColors sweep,
  }) {
    final textTheme =
        AppTypography.textTheme(scheme.onSurface, sweep.textSecondary);

    return ThemeData(
      useMaterial3: true,
      brightness: brightness,
      colorScheme: scheme,
      scaffoldBackgroundColor: scheme.surface,
      canvasColor: scheme.surface,
      fontFamily: AppTypography.fontFamily,
      textTheme: textTheme,
      extensions: [sweep],
      splashFactory: InkSparkle.splashFactory,
      dividerTheme: DividerThemeData(
        color: sweep.hairline,
        thickness: 1,
        space: 1,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: scheme.surface,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        titleTextStyle: textTheme.titleMedium,
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
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(50),
          textStyle: textTheme.labelLarge,
          shape: const RoundedRectangleBorder(borderRadius: Radii.brMd),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: const Size.fromHeight(50),
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
        contentPadding:
            const EdgeInsets.symmetric(horizontal: Gap.sm, vertical: Gap.sm),
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
      ),
      chipTheme: ChipThemeData(
        shape: const StadiumBorder(),
        side: BorderSide(color: sweep.hairline),
        backgroundColor: scheme.surfaceContainerLowest,
        labelStyle: textTheme.labelMedium,
        padding: const EdgeInsets.symmetric(horizontal: Gap.sm, vertical: 6),
      ),
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: scheme.surfaceContainerLowest,
        surfaceTintColor: Colors.transparent,
        showDragHandle: true,
        shape: const RoundedRectangleBorder(borderRadius: Radii.brSheet),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: scheme.surfaceContainerLowest,
        surfaceTintColor: Colors.transparent,
        indicatorColor: Colors.transparent,
        height: 64,
        labelTextStyle: WidgetStateProperty.resolveWith(
          (states) => textTheme.labelSmall?.copyWith(
            letterSpacing: 0,
            color: states.contains(WidgetState.selected)
                ? scheme.primary
                : sweep.textTertiary,
          ),
        ),
        iconTheme: WidgetStateProperty.resolveWith(
          (states) => IconThemeData(
            size: 24,
            color: states.contains(WidgetState.selected)
                ? scheme.primary
                : sweep.textTertiary,
          ),
        ),
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: brightness == Brightness.light
            ? const Color(0xFF1A1C19)
            : const Color(0xFF222A24),
        contentTextStyle: textTheme.bodyMedium?.copyWith(color: Colors.white),
        shape: const RoundedRectangleBorder(borderRadius: Radii.brMd),
      ),
    );
  }
}
