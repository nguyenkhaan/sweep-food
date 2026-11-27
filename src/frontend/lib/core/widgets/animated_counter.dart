import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// Smoothly animates an integer/double metric on mount or change using
/// tabular numerals, while exposing the final value immediately to semantics.
class AnimatedCounter extends StatelessWidget {
  const AnimatedCounter({
    required this.value,
    required this.formatter,
    this.style,
    this.semanticLabel,
    super.key,
  });

  final double value;
  final String Function(double animatedValue) formatter;
  final TextStyle? style;
  final String? semanticLabel;

  @override
  Widget build(BuildContext context) {
    final duration = AppMotion.resolve(context, context.motion.slow);
    final curve = AppMotion.resolveCurve(context, context.motion.enterCurve);
    final finalLabel = formatter(value);
    final effectiveStyle = AppTypography.tabular(
      style ?? context.text.titleLarge,
    );

    if (duration == Duration.zero) {
      return Text(finalLabel, style: effectiveStyle);
    }

    return Semantics(
      label: semanticLabel ?? finalLabel,
      child: ExcludeSemantics(
        child: TweenAnimationBuilder<double>(
          tween: Tween<double>(begin: 0, end: value),
          duration: duration,
          curve: curve,
          builder: (context, current, _) =>
              Text(formatter(current), style: effectiveStyle),
        ),
      ),
    );
  }
}
