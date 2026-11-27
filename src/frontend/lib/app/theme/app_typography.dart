import 'package:flutter/material.dart';

/// Bundled typography scale (`BeVietnamPro` across display & UI for crisp
/// Vietnamese diacritics and modern consumer-app hierarchy).
abstract final class AppTypography {
  static const fontFamily = 'BeVietnamPro';
  static const displayFontFamily = 'BeVietnamPro';

  static const _uiFallback = <String>[
    'BeVietnamPro',
    'Roboto',
    'SF Pro Text',
    'Segoe UI',
    'sans-serif',
  ];

  static const _displayFallback = <String>[
    'BeVietnamPro',
    'Roboto',
    'sans-serif',
  ];

  /// Applies tabular numeral alignment so dynamic counts and timers do not jitter.
  static TextStyle? tabular(TextStyle? style) =>
      style?.copyWith(fontFeatures: const [FontFeature.tabularFigures()]);

  static TextTheme textTheme(Color ink, Color inkSecondary) {
    TextStyle ui(
      double size,
      FontWeight weight, {
      double height = 1.35,
      double letterSpacing = 0,
      Color? color,
    }) => TextStyle(
      fontFamily: fontFamily,
      fontFamilyFallback: _uiFallback,
      fontSize: size,
      fontWeight: weight,
      height: height,
      letterSpacing: letterSpacing,
      color: color ?? ink,
    );

    TextStyle display(
      double size,
      FontWeight weight, {
      double height = 1.22,
      double letterSpacing = -0.4,
      Color? color,
    }) => TextStyle(
      fontFamily: displayFontFamily,
      fontFamilyFallback: _displayFallback,
      fontSize: size,
      fontWeight: weight,
      height: height,
      letterSpacing: letterSpacing,
      color: color ?? ink,
    );

    return TextTheme(
      // Hero culinary questions — "Hôm nay ăn gì?"
      displaySmall: display(
        27,
        FontWeight.w800,
        height: 1.2,
        letterSpacing: -0.6,
      ),
      // Screen & card hero headlines
      headlineMedium: display(
        24,
        FontWeight.w800,
        height: 1.24,
        letterSpacing: -0.45,
      ),
      headlineSmall: display(
        21,
        FontWeight.w800,
        height: 1.26,
        letterSpacing: -0.35,
      ),
      // Card & bar titles
      titleLarge: ui(19, FontWeight.w700, height: 1.3, letterSpacing: -0.15),
      titleMedium: ui(16.5, FontWeight.w700, height: 1.32, letterSpacing: -0.1),
      titleSmall: ui(14.5, FontWeight.w600, height: 1.35),
      // Body copy (generous line height prevents stacked Vietnamese mark clipping)
      bodyLarge: ui(15, FontWeight.w400, height: 1.48),
      bodyMedium: ui(13.5, FontWeight.w400, height: 1.48, color: inkSecondary),
      bodySmall: ui(12, FontWeight.w400, height: 1.42, color: inkSecondary),
      // Controls & labels
      labelLarge: ui(14, FontWeight.w600, height: 1.25),
      labelMedium: ui(13, FontWeight.w500, height: 1.32),
      // Overline — "CẦN DÙNG SỚM"
      labelSmall: ui(
        11,
        FontWeight.w700,
        height: 1.32,
        letterSpacing: 0.7,
        color: inkSecondary,
      ),
    );
  }
}
