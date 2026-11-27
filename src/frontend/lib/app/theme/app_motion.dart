import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Semantic motion durations, curves, and haptic helpers (`AppMotion.of(context)`).
///
/// Reduced-motion collapses durations strictly to [Duration.zero] per
/// `design-system-structure` and `accessibility-as-code`.
@immutable
class AppMotion extends ThemeExtension<AppMotion> {
  const AppMotion({
    required this.fast,
    required this.medium,
    required this.slow,
    required this.pageTransition,
    required this.enterCurve,
    required this.exitCurve,
    required this.springCurve,
  });

  final Duration fast;
  final Duration medium;
  final Duration slow;
  final Duration pageTransition;
  final Curve enterCurve;
  final Curve exitCurve;
  final Curve springCurve;

  static const standard = AppMotion(
    fast: Duration(milliseconds: 140),
    medium: Duration(milliseconds: 260),
    slow: Duration(milliseconds: 420),
    pageTransition: Duration(milliseconds: 280),
    enterCurve: Curves.easeOutCubic,
    exitCurve: Curves.easeInCubic,
    springCurve: Curves.easeOutBack,
  );

  static AppMotion of(BuildContext context) {
    final ext = Theme.of(context).extension<AppMotion>();
    assert(
      ext != null,
      'AppMotion missing from ThemeData. Build ThemeData via AppTheme.',
    );
    return ext!;
  }

  /// Collapses any animation duration to [Duration.zero] when the OS requests
  /// reduced motion (`MediaQuery.disableAnimationsOf`).
  static Duration resolve(BuildContext context, Duration full) =>
      MediaQuery.disableAnimationsOf(context) ? Duration.zero : full;

  static Curve resolveCurve(BuildContext context, Curve curve) =>
      MediaQuery.disableAnimationsOf(context) ? Curves.linear : curve;

  @override
  AppMotion copyWith({
    Duration? fast,
    Duration? medium,
    Duration? slow,
    Duration? pageTransition,
    Curve? enterCurve,
    Curve? exitCurve,
    Curve? springCurve,
  }) {
    return AppMotion(
      fast: fast ?? this.fast,
      medium: medium ?? this.medium,
      slow: slow ?? this.slow,
      pageTransition: pageTransition ?? this.pageTransition,
      enterCurve: enterCurve ?? this.enterCurve,
      exitCurve: exitCurve ?? this.exitCurve,
      springCurve: springCurve ?? this.springCurve,
    );
  }

  @override
  AppMotion lerp(covariant AppMotion? other, double t) {
    if (other == null) return this;
    // Durations & curves snap cleanly at midpoint.
    return t < 0.5 ? this : other;
  }
}

/// Tactile feedback helpers paired with key micro-interactions.
/// Haptics remain active under reduced motion (`accessibility-as-code`).
abstract final class AppHaptics {
  static void selection() => HapticFeedback.selectionClick();
  static void light() => HapticFeedback.lightImpact();
  static void medium() => HapticFeedback.mediumImpact();
  static void success() => HapticFeedback.mediumImpact();
}
