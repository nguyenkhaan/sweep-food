import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_motion.dart';
import 'package:sweepfood/app/theme/app_typography.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/shared/domain/nutrition_info.dart';

/// Animated donut showing kcal in the centre with protein / carb / fat segments.
/// Pure [CustomPaint] with reduced-motion fallback and semantic summary.
class MacroRing extends StatelessWidget {
  const MacroRing({required this.nutrition, this.size = 68, super.key});

  final NutritionInfo nutrition;
  final double size;

  @override
  Widget build(BuildContext context) {
    final protein = nutrition.proteinG;
    final carb = nutrition.carbG;
    final lipid = nutrition.lipidG;
    final total = (protein + carb + lipid).clamp(1, double.infinity);
    final duration = AppMotion.resolve(context, context.motion.slow);
    final curve = AppMotion.resolveCurve(context, context.motion.enterCurve);
    final kcalText = nutrition.energyKcal.round().toString();

    final track = context.sweep.subtleFill;
    final proteinColor = context.colors.primary;
    final carbColor = context.sweep.soon.fg;
    final lipidColor = context.sweep.expired.fg;

    return Semantics(
      label: '$kcalText kcal',
      child: ExcludeSemantics(
        child: SizedBox(
          width: size,
          height: size,
          child: TweenAnimationBuilder<double>(
            tween: Tween<double>(begin: 0, end: 1),
            duration: duration,
            curve: curve,
            builder: (context, progress, child) {
              return CustomPaint(
                painter: _RingPainter(
                  track: track,
                  proteinFrac: (protein / total) * progress,
                  carbFrac: (carb / total) * progress,
                  lipidFrac: (lipid / total) * progress,
                  proteinColor: proteinColor,
                  carbColor: carbColor,
                  lipidColor: lipidColor,
                ),
                child: child,
              );
            },
            child: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    kcalText,
                    style: AppTypography.tabular(
                      context.text.titleSmall?.copyWith(
                        fontSize: size * 0.22,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                  Text(
                    'kcal',
                    style: context.text.labelSmall?.copyWith(
                      letterSpacing: 0,
                      fontSize: size * 0.13,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _RingPainter extends CustomPainter {
  _RingPainter({
    required this.track,
    required this.proteinFrac,
    required this.carbFrac,
    required this.lipidFrac,
    required this.proteinColor,
    required this.carbColor,
    required this.lipidColor,
  });

  final Color track;
  final double proteinFrac;
  final double carbFrac;
  final double lipidFrac;
  final Color proteinColor;
  final Color carbColor;
  final Color lipidColor;

  @override
  void paint(Canvas canvas, Size size) {
    final stroke = size.width * 0.12;
    final rect = Offset.zero & size;
    final ring = rect.deflate(stroke / 2);
    final base = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = stroke
      ..color = track;
    canvas.drawArc(ring, 0, 2 * math.pi, false, base);

    var start = -math.pi / 2;
    void seg(double frac, Color color) {
      if (frac <= 0.001) return;
      final sweep = frac * 2 * math.pi;
      canvas.drawArc(
        ring,
        start,
        sweep,
        false,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = stroke
          ..strokeCap = StrokeCap.round
          ..color = color,
      );
      start += sweep;
    }

    seg(proteinFrac, proteinColor);
    seg(carbFrac, carbColor);
    seg(lipidFrac, lipidColor);
  }

  @override
  bool shouldRepaint(_RingPainter old) =>
      old.proteinFrac != proteinFrac ||
      old.carbFrac != carbFrac ||
      old.lipidFrac != lipidFrac ||
      old.track != track;
}
