import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/shared/domain/nutrition_info.dart';

/// Donut showing kcal in the centre with protein / carb ring segments
/// (dish detail, D-01). Pure [CustomPaint] — no chart library needed.
class MacroRing extends StatelessWidget {
  const MacroRing({required this.nutrition, this.size = 64, super.key});

  final NutritionInfo nutrition;
  final double size;

  @override
  Widget build(BuildContext context) {
    final protein = nutrition.proteinG;
    final carb = nutrition.carbG;
    final lipid = nutrition.lipidG;
    final total = (protein + carb + lipid).clamp(1, double.infinity);

    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        painter: _RingPainter(
          track: context.sweep.subtleFill,
          proteinFrac: protein / total,
          carbFrac: carb / total,
          proteinColor: context.colors.primary,
          carbColor: context.sweep.soon.fg,
          lipidColor: context.sweep.expired.fg,
        ),
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                nutrition.energyKcal.round().toString(),
                style: context.text.titleSmall?.copyWith(fontSize: size * 0.22),
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
    );
  }
}

class _RingPainter extends CustomPainter {
  _RingPainter({
    required this.track,
    required this.proteinFrac,
    required this.carbFrac,
    required this.proteinColor,
    required this.carbColor,
    required this.lipidColor,
  });

  final Color track;
  final double proteinFrac;
  final double carbFrac;
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
      if (frac <= 0) return;
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
    seg((1 - proteinFrac - carbFrac).clamp(0, 1), lipidColor);
  }

  @override
  bool shouldRepaint(_RingPainter old) =>
      old.proteinFrac != proteinFrac || old.carbFrac != carbFrac;
}
