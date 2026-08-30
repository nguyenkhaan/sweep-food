import 'package:flutter/material.dart';

/// Type scale (from the design "Foundations" artboard).
///
/// Font family is `Inter`. The TTFs are not bundled yet — until then Flutter
/// falls back to the platform sans-serif, which is close enough in metrics.
/// TODO(M6): add `assets/fonts/Inter-*.ttf` + declare the family in pubspec.
abstract final class AppTypography {
  static const fontFamily = 'Inter';
  static const _fallback = <String>[
    'Roboto',
    'SF Pro Text',
    'Segoe UI',
    'sans-serif',
  ];

  static TextTheme textTheme(Color ink, Color inkSecondary) {
    TextStyle s(
      double size,
      FontWeight weight, {
      double height = 1.3,
      double letterSpacing = 0,
      Color? color,
    }) =>
        TextStyle(
          fontFamily: fontFamily,
          fontFamilyFallback: _fallback,
          fontSize: size,
          fontWeight: weight,
          height: height,
          letterSpacing: letterSpacing,
          color: color ?? ink,
        );

    return TextTheme(
      // "Hôm nay ăn gì?" — big screen questions
      displaySmall: s(28, FontWeight.w700, height: 1.2, letterSpacing: -0.5),
      // section / screen headlines
      headlineSmall: s(22, FontWeight.w700, height: 1.25, letterSpacing: -0.2),
      // card titles
      titleMedium: s(17, FontWeight.w600, height: 1.3),
      titleSmall: s(15, FontWeight.w600, height: 1.3),
      // body
      bodyLarge: s(15, FontWeight.w400, height: 1.45),
      bodyMedium: s(13, FontWeight.w400, height: 1.45, color: inkSecondary),
      // labels
      labelLarge: s(14, FontWeight.w600, height: 1.2), // buttons
      labelMedium: s(13, FontWeight.w500, height: 1.3),
      // overline — "CẦN DÙNG SỚM"
      labelSmall: s(
        11,
        FontWeight.w700,
        height: 1.3,
        letterSpacing: 0.8,
        color: inkSecondary,
      ),
    );
  }
}
